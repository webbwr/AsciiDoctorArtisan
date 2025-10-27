"""
Grammar Manager - Orchestration layer for hybrid grammar checking system.

This module provides the GrammarManager class which coordinates the
dual-engine grammar checking system (LanguageTool + Ollama AI).

Implements:
- FR-077: Grammar checking orchestration
- FR-078: Visual indicator management
- FR-079: Result aggregation and deduplication
- FR-080: User interaction handling

Architecture:
- Facade pattern for complex subsystem
- Observer pattern for text changes
- Strategy pattern for checking modes
- Coordinator for multiple workers

Responsibilities:
- Worker lifecycle management
- Debounce timer coordination
- Result aggregation and merging
- Visual underline application
- Tooltip management
- Context menu integration
- Cache coordination

Author: AsciiDoc Artisan Development Team
Version: 1.3.0
"""

import hashlib
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING, Dict, List, Optional

from PySide6.QtCore import QObject, QPoint, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QMenu, QTextEdit, QToolTip

from asciidoc_artisan.core.grammar_config import (
    DEFAULT_PERFORMANCE_PROFILE,
    PERFORMANCE_PROFILES,
)
from asciidoc_artisan.core.grammar_models import (
    AggregatedGrammarResult,
    GrammarResult,
    GrammarSource,
    GrammarSuggestion,
)
from asciidoc_artisan.workers import LanguageToolWorker, OllamaGrammarWorker

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


# ============================================================================
# CHECKING MODE ENUM
# ============================================================================


class CheckingMode:
    """Grammar checking mode configuration."""

    DISABLED = "disabled"  # No checking
    LANGUAGETOOL_ONLY = "languagetool"  # Fast rules-based only
    OLLAMA_ONLY = "ollama"  # AI-only (slow)
    HYBRID = "hybrid"  # Both engines (recommended)


# ============================================================================
# RESULT DEDUPLICATOR
# ============================================================================


class SuggestionDeduplicator:
    """Deduplicates suggestions from multiple sources.

    When both LanguageTool and Ollama flag the same issue,
    we keep the higher-quality suggestion and avoid duplicates.
    """

    @staticmethod
    def deduplicate(
        lt_suggestions: List[GrammarSuggestion],
        ollama_suggestions: List[GrammarSuggestion],
    ) -> List[GrammarSuggestion]:
        """Deduplicate suggestions from both sources.

        Args:
            lt_suggestions: Suggestions from LanguageTool
            ollama_suggestions: Suggestions from Ollama

        Returns:
            Merged list with duplicates removed
        """
        if not ollama_suggestions:
            return lt_suggestions

        if not lt_suggestions:
            return ollama_suggestions

        # Start with all LanguageTool suggestions
        merged = list(lt_suggestions)

        # Add Ollama suggestions that don't overlap
        for ollama_sugg in ollama_suggestions:
            if not SuggestionDeduplicator._overlaps_with_any(
                ollama_sugg, lt_suggestions
            ):
                merged.append(ollama_sugg)
            else:
                logger.debug(
                    f"Skipping duplicate Ollama suggestion at [{ollama_sugg.start}:{ollama_sugg.end}]"
                )

        # Sort by position
        merged.sort(key=lambda s: (s.start, s.end))

        logger.info(
            f"Deduplicated: {len(lt_suggestions)} LT + {len(ollama_suggestions)} Ollama "
            f"-> {len(merged)} merged"
        )

        return merged

    @staticmethod
    def _overlaps_with_any(
        suggestion: GrammarSuggestion, others: List[GrammarSuggestion]
    ) -> bool:
        """Check if suggestion overlaps with any in list.

        Args:
            suggestion: Suggestion to check
            others: List of other suggestions

        Returns:
            True if overlaps with any
        """
        for other in others:
            if SuggestionDeduplicator._ranges_overlap(
                (suggestion.start, suggestion.end), (other.start, other.end)
            ):
                return True
        return False

    @staticmethod
    def _ranges_overlap(range1: tuple, range2: tuple) -> bool:
        """Check if two ranges overlap.

        Args:
            range1: (start, end) tuple
            range2: (start, end) tuple

        Returns:
            True if ranges overlap
        """
        start1, end1 = range1
        start2, end2 = range2

        # Ranges overlap if one starts before the other ends
        return start1 < end2 and start2 < end1


# ============================================================================
# GRAMMAR MANAGER
# ============================================================================


class GrammarManager(QObject):
    """Orchestrates hybrid grammar checking system.

    This is the main public interface for grammar checking in
    AsciiDoc Artisan. It coordinates two worker threads:
    - LanguageTool: Fast rules-based checking
    - Ollama AI: Slower context-aware analysis

    Features:
    - Dual-engine coordination
    - Intelligent result merging
    - Visual underline management
    - Debounced auto-checking
    - Cache coordination
    - Performance profiling

    Usage:
        ```python
        manager = GrammarManager(editor)
        manager.enable_grammar_checking(True)
        ```
    """

    # Signal for thread-safe status updates
    status_update_requested = Signal(str, int)

    def __init__(self, editor: "AsciiDocEditor"):
        """Initialize GrammarManager.

        Args:
            editor: Reference to main AsciiDocEditor window
        """
        super().__init__()
        self.editor = editor

        # Configuration
        self._enabled = False
        self._checking_mode = CheckingMode.HYBRID
        self._performance_profile = DEFAULT_PERFORMANCE_PROFILE

        # Workers and threads
        self._setup_languagetool_worker()
        self._setup_ollama_worker()

        # Debounce timers
        self._lt_timer = QTimer()
        self._lt_timer.setSingleShot(True)
        self._lt_timer.timeout.connect(self._trigger_languagetool_check)

        self._ollama_timer = QTimer()
        self._ollama_timer.setSingleShot(True)
        self._ollama_timer.timeout.connect(self._trigger_ollama_check)

        # State
        self._current_suggestions: List[GrammarSuggestion] = []
        self._lt_result: Optional[GrammarResult] = None
        self._ollama_result: Optional[GrammarResult] = None
        self._is_checking = False

        # Global cache (supplements worker caches)
        self._result_cache: OrderedDict[str, AggregatedGrammarResult] = OrderedDict()
        self._cache_max_size = 50

        # Deduplicator
        self._deduplicator = SuggestionDeduplicator()

        logger.info("GrammarManager initialized")

    # ========================================================================
    # WORKER SETUP
    # ========================================================================

    def _setup_languagetool_worker(self):
        """Set up LanguageTool worker and thread."""
        self.lt_worker = LanguageToolWorker()
        self.lt_thread = QThread()
        self.lt_worker.moveToThread(self.lt_thread)

        # Connect signals
        self.lt_worker.grammar_result_ready.connect(self._handle_languagetool_result)
        self.lt_worker.progress_update.connect(self._handle_progress_update)
        self.lt_worker.initialization_complete.connect(self._handle_lt_initialization)

        # Thread will be started later in start_workers()

        logger.info("LanguageTool worker setup complete")

    def _setup_ollama_worker(self):
        """Set up Ollama worker and thread."""
        self.ollama_worker = OllamaGrammarWorker()
        self.ollama_thread = QThread()
        self.ollama_worker.moveToThread(self.ollama_thread)

        # Connect signals
        self.ollama_worker.grammar_result_ready.connect(self._handle_ollama_result)
        self.ollama_worker.progress_update.connect(self._handle_progress_update)

        # Thread will be started later in start_workers()

        # Load configuration from settings
        self._load_ollama_config()

        logger.info("Ollama worker setup complete")

    def _load_ollama_config(self):
        """Load Ollama configuration from settings."""
        try:
            settings = self.editor._settings
            ollama_enabled = getattr(settings, "ollama_grammar_enabled", False)
            ollama_model = getattr(settings, "ollama_model", "gnokit/improve-grammar")

            self.ollama_worker.set_config(ollama_enabled, ollama_model)
            logger.info(
                f"Ollama config loaded: enabled={ollama_enabled}, model={ollama_model}"
            )

        except Exception as e:
            logger.error(f"Failed to load Ollama config: {e}")

    def start_workers(self):
        """Start worker threads. Must be called after main window is fully initialized."""
        # Start LanguageTool thread
        self.lt_thread.start()

        # Initialize LanguageTool worker
        self.lt_worker.initialize_tool("en-US")

        # Start Ollama thread
        self.ollama_thread.start()

        logger.info("Grammar worker threads started")

    # ========================================================================
    # PUBLIC API - ENABLE/DISABLE
    # ========================================================================

    def check_now(self):
        """Manually trigger grammar check immediately."""
        if not self._enabled:
            self.enable_grammar_checking(True)
        self._trigger_languagetool_check()
        logger.info("Manual grammar check triggered")

    def toggle_auto_check(self, checked: bool):
        """Toggle automatic grammar checking on/off.

        Args:
            checked: True to enable auto-checking, False to disable
        """
        self.enable_grammar_checking(checked)

    def navigate_to_next_issue(self):
        """Navigate cursor to next grammar issue."""
        if not self._current_suggestions:
            self._update_status("No grammar issues to navigate", timeout=2000)
            return

        cursor = self.editor.editor.textCursor()
        current_pos = cursor.position()

        # Find next suggestion after current position
        next_suggestion = None
        for suggestion in self._current_suggestions:
            if suggestion.start > current_pos:
                next_suggestion = suggestion
                break

        # If no suggestion after cursor, wrap to first
        if not next_suggestion and self._current_suggestions:
            next_suggestion = self._current_suggestions[0]

        if next_suggestion:
            # Move cursor to suggestion
            cursor.setPosition(next_suggestion.start)
            cursor.setPosition(next_suggestion.end, QTextCursor.MoveMode.KeepAnchor)
            self.editor.editor.setTextCursor(cursor)
            self.editor.editor.ensureCursorVisible()

            # Show tooltip
            self.show_suggestion_at_cursor()
            logger.debug(f"Navigated to issue at position {next_suggestion.start}")

    def ignore_current_suggestion(self):
        """Ignore grammar suggestion at current cursor position."""
        cursor = self.editor.editor.textCursor()
        pos = cursor.position()

        suggestion = self._find_suggestion_at_position(pos)
        if suggestion:
            self._ignore_suggestion(suggestion)
        else:
            self._update_status("No grammar issue at cursor", timeout=2000)

    def enable_grammar_checking(self, enabled: bool):
        """Enable or disable grammar checking.

        Args:
            enabled: True to enable, False to disable
        """
        if self._enabled == enabled:
            return  # No change

        self._enabled = enabled
        logger.info(f"Grammar checking {'enabled' if enabled else 'disabled'}")

        if enabled:
            # Connect to text changes
            self.editor.editor.textChanged.connect(self._on_text_changed)

            # Trigger initial check
            self._trigger_languagetool_check()

            # Update status
            self._update_status("Grammar checking enabled")

        else:
            # Disconnect from text changes
            try:
                self.editor.editor.textChanged.disconnect(self._on_text_changed)
            except RuntimeError:
                pass  # Not connected

            # Clear visual indicators
            self._clear_underlines()

            # Update status
            self._update_status("Grammar checking disabled")

    def set_checking_mode(self, mode: str):
        """Set grammar checking mode.

        Args:
            mode: One of CheckingMode constants
        """
        if mode not in [
            CheckingMode.DISABLED,
            CheckingMode.LANGUAGETOOL_ONLY,
            CheckingMode.OLLAMA_ONLY,
            CheckingMode.HYBRID,
        ]:
            logger.warning(f"Invalid checking mode: {mode}")
            return

        self._checking_mode = mode
        logger.info(f"Checking mode set to: {mode}")

        # Re-check if enabled
        if self._enabled:
            self._trigger_languagetool_check()

    def set_performance_profile(self, profile_name: str):
        """Set performance profile.

        Args:
            profile_name: Name of profile (realtime/balanced/thorough)
        """
        if profile_name not in PERFORMANCE_PROFILES:
            logger.warning(f"Unknown profile: {profile_name}")
            return

        self._performance_profile = profile_name
        profile = PERFORMANCE_PROFILES[profile_name]

        logger.info(f"Performance profile set to: {profile_name}")
        logger.debug(f"Profile settings: {profile}")

    # ========================================================================
    # TEXT CHANGE HANDLING
    # ========================================================================

    @Slot()
    def _on_text_changed(self):
        """Handle editor text change event."""
        if not self._enabled:
            return

        # Stop existing timers
        self._lt_timer.stop()
        self._ollama_timer.stop()

        # Get debounce times from profile
        profile = PERFORMANCE_PROFILES.get(
            self._performance_profile, PERFORMANCE_PROFILES["balanced"]
        )

        # Start LanguageTool timer (fast)
        self._lt_timer.start(profile.languagetool_debounce_ms)

        logger.debug("Text changed - debounce timers restarted")

    # ========================================================================
    # CHECKING TRIGGERS
    # ========================================================================

    @Slot()
    def _trigger_languagetool_check(self):
        """Trigger LanguageTool grammar check."""
        if not self._enabled:
            return

        if self._checking_mode == CheckingMode.DISABLED:
            return

        if self._checking_mode == CheckingMode.OLLAMA_ONLY:
            # Skip LanguageTool, go straight to Ollama
            self._trigger_ollama_check()
            return

        text = self.editor.editor.toPlainText()

        # Check cache first
        text_hash = self._compute_hash(text)
        cached = self._result_cache.get(text_hash)
        if cached:
            logger.debug("Using cached aggregated result")
            self._apply_aggregated_result(cached)
            return

        # Send to LanguageTool worker
        self._is_checking = True
        self._update_status("Checking grammar...")
        self.lt_worker.check_text(text)

    @Slot()
    def _trigger_ollama_check(self):
        """Trigger Ollama AI grammar check."""
        if not self._enabled:
            return

        if self._checking_mode in [
            CheckingMode.DISABLED,
            CheckingMode.LANGUAGETOOL_ONLY,
        ]:
            return

        # Get profile
        profile = PERFORMANCE_PROFILES.get(
            self._performance_profile, PERFORMANCE_PROFILES["balanced"]
        )

        if not profile.ollama_enabled:
            logger.debug("Ollama disabled by performance profile")
            return

        text = self.editor.editor.toPlainText()

        # Send to Ollama worker
        self._update_status("Analyzing with AI...")
        self.ollama_worker.check_text(text)

    # ========================================================================
    # RESULT HANDLING
    # ========================================================================

    @Slot(GrammarResult)
    def _handle_languagetool_result(self, result: GrammarResult):
        """Handle LanguageTool check result.

        Args:
            result: Grammar check result
        """
        self._lt_result = result
        self._is_checking = False

        if not result.success:
            logger.error(f"LanguageTool check failed: {result.error_message}")
            self._update_status(
                f"Grammar check failed: {result.error_message}", timeout=5000
            )
            return

        logger.info(
            f"LanguageTool: {result.suggestion_count} issues, "
            f"{result.processing_time_ms}ms"
        )

        # If hybrid mode, trigger Ollama after LanguageTool
        if self._checking_mode == CheckingMode.HYBRID:
            profile = PERFORMANCE_PROFILES.get(
                self._performance_profile, PERFORMANCE_PROFILES["balanced"]
            )

            if profile.ollama_enabled:
                # Start Ollama timer
                self._ollama_timer.stop()
                self._ollama_timer.start(profile.ollama_debounce_ms)

        # Apply LanguageTool results immediately
        self._apply_languagetool_result(result)

    @Slot(GrammarResult)
    def _handle_ollama_result(self, result: GrammarResult):
        """Handle Ollama check result.

        Args:
            result: Grammar check result
        """
        self._ollama_result = result

        if not result.success:
            logger.warning(f"Ollama check failed: {result.error_message}")
            # Don't show error to user - LanguageTool results are already displayed
            return

        logger.info(
            f"Ollama: {result.suggestion_count} suggestions, "
            f"{result.processing_time_ms}ms"
        )

        # Merge with LanguageTool results
        self._merge_and_apply_results()

    def _apply_languagetool_result(self, result: GrammarResult):
        """Apply LanguageTool results to editor.

        Args:
            result: LanguageTool result
        """
        self._current_suggestions = result.suggestions
        self._apply_underlines(result.suggestions)

        # Update status
        count = result.suggestion_count
        if count == 0:
            self._update_status("No issues found", timeout=3000)
        else:
            self._update_status(
                f"Grammar: {count} issue{'s' if count != 1 else ''} found", timeout=5000
            )

    def _merge_and_apply_results(self):
        """Merge LanguageTool and Ollama results and apply."""
        if not self._lt_result or not self._ollama_result:
            logger.warning("Cannot merge - missing results")
            return

        # Deduplicate suggestions
        merged = self._deduplicator.deduplicate(
            self._lt_result.suggestions, self._ollama_result.suggestions
        )

        # Create aggregated result
        aggregated = AggregatedGrammarResult(
            languagetool_result=self._lt_result,
            ollama_result=self._ollama_result,
            merged_suggestions=merged,
            total_processing_time_ms=(
                self._lt_result.processing_time_ms
                + self._ollama_result.processing_time_ms
            ),
        )

        # Cache result
        text = self.editor.editor.toPlainText()
        text_hash = self._compute_hash(text)
        self._cache_result(text_hash, aggregated)

        # Apply to editor
        self._apply_aggregated_result(aggregated)

    def _apply_aggregated_result(self, result: AggregatedGrammarResult):
        """Apply aggregated result to editor.

        Args:
            result: Aggregated result
        """
        self._current_suggestions = result.merged_suggestions
        self._apply_underlines(result.merged_suggestions)

        # Update status
        lt_count = result.languagetool_count
        ollama_count = result.ollama_count
        total = result.suggestion_count

        if total == 0:
            self._update_status("No issues found", timeout=3000)
        else:
            self._update_status(
                f"Grammar: {total} issues ({lt_count} rules, {ollama_count} AI)",
                timeout=5000,
            )

    # ========================================================================
    # VISUAL INDICATORS
    # ========================================================================

    def _apply_underlines(self, suggestions: List[GrammarSuggestion]):
        """Apply colored underlines to editor for suggestions.

        Args:
            suggestions: List of grammar suggestions
        """
        extra_selections = []

        for suggestion in suggestions:
            selection = QTextEdit.ExtraSelection()

            # Set cursor position
            cursor = self.editor.editor.textCursor()
            cursor.setPosition(suggestion.start)
            cursor.setPosition(suggestion.end, QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor

            # Get color for category
            rgb = suggestion.category.get_color_rgb()
            color = QColor(*rgb)

            # Apply wavy underline
            underline_format = QTextCharFormat()
            underline_format.setUnderlineColor(color)
            underline_format.setUnderlineStyle(
                QTextCharFormat.UnderlineStyle.WaveUnderline
            )
            selection.format = underline_format

            extra_selections.append(selection)

        self.editor.editor.setExtraSelections(extra_selections)

        logger.debug(f"Applied {len(extra_selections)} underlines")

    def _clear_underlines(self):
        """Clear all grammar underlines from editor."""
        self.editor.editor.setExtraSelections([])
        self._current_suggestions = []
        logger.debug("Cleared all underlines")

    # ========================================================================
    # TOOLTIP MANAGEMENT
    # ========================================================================

    def show_suggestion_at_cursor(self):
        """Show tooltip with suggestion at current cursor position."""
        cursor = self.editor.editor.textCursor()
        pos = cursor.position()

        suggestion = self._find_suggestion_at_position(pos)
        if not suggestion:
            return

        # Build tooltip HTML
        tooltip = self._build_suggestion_tooltip(suggestion)

        # Show tooltip
        cursor_rect = self.editor.editor.cursorRect(cursor)
        global_pos = self.editor.editor.mapToGlobal(cursor_rect.bottomLeft())
        QToolTip.showText(global_pos, tooltip, self.editor.editor)

    def _build_suggestion_tooltip(self, suggestion: GrammarSuggestion) -> str:
        """Build HTML tooltip for suggestion.

        Args:
            suggestion: Grammar suggestion

        Returns:
            HTML string
        """
        html = f"<b>{suggestion.source.value.title()}</b> - "
        html += f"<i>{suggestion.category.value.title()}</i><br><br>"
        html += f"{suggestion.message}<br>"

        if suggestion.replacements:
            html += "<br><b>Suggestions:</b><ul>"
            for i, replacement in enumerate(suggestion.replacements[:3]):
                html += f"<li>{replacement}</li>"
                if i >= 2:  # Limit to 3
                    break
            html += "</ul>"

        return html

    def _find_suggestion_at_position(self, pos: int) -> Optional[GrammarSuggestion]:
        """Find grammar suggestion at text position.

        Args:
            pos: Character position in document

        Returns:
            GrammarSuggestion if found, None otherwise
        """
        for suggestion in self._current_suggestions:
            if suggestion.start <= pos <= suggestion.end:
                return suggestion
        return None

    # ========================================================================
    # CONTEXT MENU
    # ========================================================================

    def show_context_menu(self, position: QPoint):
        """Show context menu with grammar suggestions.

        Args:
            position: Position in editor widget coordinates
        """
        cursor = self.editor.editor.cursorForPosition(position)
        pos = cursor.position()

        suggestion = self._find_suggestion_at_position(pos)
        if not suggestion:
            return

        menu = QMenu(self.editor.editor)

        # Add replacement actions
        if suggestion.replacements:
            for replacement in suggestion.replacements[:5]:
                action = menu.addAction(f"Replace with '{replacement}'")
                action.triggered.connect(
                    lambda checked, s=suggestion, r=replacement: self._apply_fix(s, r)
                )

            menu.addSeparator()

        # Ignore actions
        ignore_action = menu.addAction("Ignore this issue")
        ignore_action.triggered.connect(lambda: self._ignore_suggestion(suggestion))

        if suggestion.rule_id and suggestion.source == GrammarSource.LANGUAGETOOL:
            ignore_rule_action = menu.addAction(f"Ignore rule '{suggestion.rule_id}'")
            ignore_rule_action.triggered.connect(
                lambda: self._ignore_rule(suggestion.rule_id)
            )

        menu.exec(self.editor.editor.mapToGlobal(position))

    def _apply_fix(self, suggestion: GrammarSuggestion, replacement: str):
        """Apply grammar fix to editor.

        Args:
            suggestion: Suggestion with position
            replacement: Replacement text
        """
        cursor = self.editor.editor.textCursor()
        cursor.setPosition(suggestion.start)
        cursor.setPosition(suggestion.end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(replacement)

        logger.info(
            f"Applied fix at [{suggestion.start}:{suggestion.end}]: {replacement}"
        )

        # Re-check will be triggered by text change

    def _ignore_suggestion(self, suggestion: GrammarSuggestion):
        """Ignore a specific suggestion.

        Args:
            suggestion: Suggestion to ignore
        """
        # Remove from current suggestions
        self._current_suggestions = [
            s
            for s in self._current_suggestions
            if not (s.start == suggestion.start and s.end == suggestion.end)
        ]

        # Reapply underlines
        self._apply_underlines(self._current_suggestions)

        logger.info(f"Ignored suggestion at [{suggestion.start}:{suggestion.end}]")

    def _ignore_rule(self, rule_id: str):
        """Ignore a grammar rule permanently.

        Args:
            rule_id: Rule identifier to ignore
        """
        # Tell LanguageTool worker to disable this rule
        self.lt_worker.disable_rule(rule_id)

        # Remove all suggestions with this rule from current display
        self._current_suggestions = [
            s for s in self._current_suggestions if s.rule_id != rule_id
        ]

        # Reapply underlines
        self._apply_underlines(self._current_suggestions)

        logger.info(f"Ignored rule: {rule_id}")

        # Update status
        self._update_status(f"Rule '{rule_id}' disabled", timeout=3000)

    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================

    def _cache_result(self, key: str, result: AggregatedGrammarResult):
        """Cache aggregated result.

        Args:
            key: Cache key (text hash)
            result: Aggregated result
        """
        self._result_cache[key] = result

        # Evict oldest if over capacity
        if len(self._result_cache) > self._cache_max_size:
            oldest_key = next(iter(self._result_cache))
            del self._result_cache[oldest_key]
            logger.debug(f"Cache eviction - size: {len(self._result_cache)}")

    def clear_cache(self):
        """Clear all caches."""
        self._result_cache.clear()
        self.lt_worker.clear_cache()
        logger.info("All caches cleared")

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def _compute_hash(self, text: str) -> str:
        """Compute hash of text for caching.

        Args:
            text: Text to hash

        Returns:
            SHA256 hash hex string
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _update_status(self, message: str, timeout: int = 0):
        """Update status bar message.

        Args:
            message: Status message
            timeout: Timeout in milliseconds (0 = permanent)

        Note:
            This method may be called from worker threads. We emit a signal
            which is automatically queued to run on the main GUI thread.
        """
        try:
            # Emit signal - Qt will queue this to main thread if needed
            self.status_update_requested.emit(message, timeout)
        except Exception as e:
            logger.debug(f"Could not update status: {e}")

    @Slot(bool)
    def _handle_lt_initialization(self, success: bool):
        """Handle LanguageTool initialization result.

        Args:
            success: Whether initialization succeeded
        """
        if success:
            logger.info("LanguageTool initialized successfully")
        else:
            logger.error("LanguageTool initialization failed")
            self._update_status(
                "Grammar checking unavailable (LanguageTool init failed)", timeout=5000
            )

    @Slot(str)
    def _handle_progress_update(self, message: str):
        """Handle progress update from workers.

        Args:
            message: Progress message
        """
        logger.debug(f"Progress: {message}")

    def get_statistics(self) -> Dict:
        """Get statistics from all components.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "languagetool": self.lt_worker.get_statistics(),
            "ollama": self.ollama_worker.get_statistics(),
            "cache_size": len(self._result_cache),
            "current_suggestions": len(self._current_suggestions),
            "enabled": self._enabled,
            "checking_mode": self._checking_mode,
            "performance_profile": self._performance_profile,
        }
        return stats

    # ========================================================================
    # CLEANUP
    # ========================================================================

    def cleanup(self):
        """Clean up resources before shutdown."""
        logger.info("GrammarManager cleanup started")

        try:
            # Disable checking
            self.enable_grammar_checking(False)

            # Stop timers
            self._lt_timer.stop()
            self._ollama_timer.stop()

            # Clean up workers
            self.lt_worker.cleanup()
            self.ollama_worker.cleanup()

            # Stop threads
            self.lt_thread.quit()
            self.ollama_thread.quit()

            # Wait for threads to finish (with timeout)
            self.lt_thread.wait(1000)
            self.ollama_thread.wait(1000)

            logger.info("GrammarManager cleanup complete")

        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)
