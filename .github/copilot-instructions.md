<!-- .github/copilot-instructions.md: guidance for AI coding agents -->
# Copilot instructions — AsciiDoc Artisan

These notes give an AI coding assistant the minimal, actionable context needed to be productive in this repository.

1) Big picture
- Single-file PySide6 desktop app: main UI and logic live in `adp.py` (approx. 1k lines).
- Responsibilities in `adp.py`: UI (Qt widgets), background workers (Git, Pandoc), settings, file I/O, AsciiDoc -> HTML preview.
- External/system integrations: Pandoc (system binary, used via `pypandoc`), Git (via subprocess), `asciidoc3` for preview rendering.

2) Important files and folders
- `adp.py` — the authoritative source for app behavior. Search here for any UI, Git, or conversion logic.
- `README.md` — installation, platform notes, and usage examples (start app with `python adp.py`).
- `requirements.txt` — Python deps (PySide6, asciidoc3, pypandoc).
- `setup.sh`, `verify.sh`, `AsciiDocArtisanVerify.ps1` — platform install/verify flows (Linux/WSL and Windows).
- `asciidoc-verification-summary.md` — Windows troubleshooting details for Pandoc/Python.

3) Developer workflows (how humans run & debug)
- Run the app: `python adp.py` (Windows and Unix). The README contains platform-specific setup steps.
- Verify environment: `./verify.sh` on Linux/WSL, `AsciiDocArtisanVerify.ps1` on Windows.
- Quick syntax check: `python -m py_compile adp.py`.
- No unit tests or CI present; be conservative when changing global behavior in `adp.py`.

4) Project-specific conventions & patterns
- Threading model: long-running work is delegated to QThread workers (`GitWorker`, `PandocWorker`) — use signals (`Signal`) and slots (`@Slot`) to communicate results.
- Git is invoked with `subprocess.run([...])` in the Git worker; error handling maps stderr text to user-friendly messages (see `GitWorker.run_git_command`).
- Pandoc conversions use `pypandoc` in `PandocWorker.run_pandoc_conversion`. DOCX->AsciiDoc prepends TOC directives.
- Settings are persisted as JSON using a platform-appropriate location via `QStandardPaths` (`AsciiDocArtisan.json`).
- UI state is guarded by flags: `_is_processing_git`, `_is_processing_pandoc`, `_is_opening_file` — respect these when adding new operations.

5) Common edits and low-risk changes
- Small UI changes, CSS tweaks, or text edits in `README.md` are safe.
- Add logging: converting `print()` to the `logging` module is low-risk and recommended.
- Add input sanitization for Git commit messages (use `shlex.quote` or pass list args — see `request_git_command.emit(["git","commit","-m", msg], path)`).

6) High-risk areas (review before changing)
- Refactoring `adp.py` into modules affects application startup and QThread lifecycle — preserve `main()` behavior and thread startup/shutdown in `closeEvent`.
- Git subprocess commands and Pandoc invocation are security- and environment-sensitive — validate changes manually on Windows and Linux.
- Settings loading/saving (`_load_settings`, `_save_settings`) — malformed JSON handling and path selection are important for cross-platform behavior.

7) Tests & CI
- None present. When adding tests prefer `pytest` and `pytest-qt` for GUI logic. Keep tests focused and isolated (file I/O, workers) to avoid launching full GUI in CI.

8) Examples (copy/paste ready)
- Start app locally: `python adp.py` (Windows: same command; ensure Python 3.11+ and Pandoc on PATH for DOCX features).
- Convert clipboard HTML to AsciiDoc (runtime behavior): `AsciiDocEditor.convert_and_paste_from_clipboard()` uses `request_pandoc_conversion.emit(..., 'asciidoc','html', 'clipboard conversion')`.

9) Where to look for follow-ups
- If unsure about behavior, search `adp.py` for symbols: `GitWorker`, `PandocWorker`, `_check_pandoc_availability`, `_trigger_git_commit`, `_load_content_into_editor`.
- Use `README.md` and `asciidoc-verification-summary.md` for platform-specific setup notes.

If any section is unclear or you'd like more detailed editing rules (e.g., coding style, preferred refactor plan), tell me which area to expand and I'll update this file.
