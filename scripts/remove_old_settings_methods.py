#!/usr/bin/env python3
"""
Script to remove old settings methods from main_window.py after extraction to SettingsManager.
"""

import re
from pathlib import Path

def remove_old_methods():
    """Remove deprecated settings methods from main_window.py"""
    file_path = Path("asciidoc_artisan/ui/main_window.py")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Methods to remove (by signature)
    methods_to_remove = [
        "def _set_default_settings(self)",
        "def _get_settings_path(self)",
        "def _load_settings(self)",
        "def _save_settings(self)",
        "def _restore_ui_settings(self)",
        "def _get_ai_conversion_preference(self)",
    ]

    new_lines = []
    skip_until_next_method = False
    current_indent = None

    for i, line in enumerate(lines):
        # Check if this is a method we want to remove
        is_target_method = any(method_sig in line for method_sig in methods_to_remove)

        if is_target_method and line.strip().startswith("def "):
            # Start skipping
            skip_until_next_method = True
            current_indent = len(line) - len(line.lstrip())
            print(f"Removing method at line {i+1}: {line.strip()}")
            continue

        if skip_until_next_method:
            # Check if we've reached the next method at the same or lower indentation
            if line.strip() and not line.strip().startswith("#"):
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= current_indent and (line.strip().startswith("def ") or line.strip().startswith("class ")):
                    skip_until_next_method = False
                    current_indent = None
                elif line_indent <= current_indent and not line.strip():
                    # Empty line at same indent might signal end
                    pass
                else:
                    # Still inside the method being removed
                    continue

        # If not skipping, keep the line
        if not skip_until_next_method:
            new_lines.append(line)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\nRemoved {len(lines) - len(new_lines)} lines")
    print(f"Old: {len(lines)} lines, New: {len(new_lines)} lines")

if __name__ == "__main__":
    remove_old_methods()
