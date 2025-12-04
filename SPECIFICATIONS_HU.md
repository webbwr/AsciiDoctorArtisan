# AsciiDoc Artisan Functional Specifications

**v2.1.0** | **Dec 4, 2025** | **Public Release** | **109 FRs (100% implemented)**

> For AI implementation: [SPECIFICATIONS_AI.md](SPECIFICATIONS_AI.md) | Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 44,201 lines / 171 files |
| Unit Tests | 5,254 |
| E2E Tests | 3 |
| Type Coverage | 100% (mypy --strict) |
| Startup | 0.586s |

---

## FR Quick Reference (109 total)

### Core Editing (FR-001–005)
- **001** Text Editor: QPlainTextEdit, syntax highlighting
- **002** Line Numbers: LineNumberArea (8 tests)
- **003** Undo/Redo: Qt stack, Ctrl+Z/Y
- **004** Fonts: Family/size, Monospace 10pt default
- **005** Editor State: Cursor/scroll/selection persistence (12 tests)

### File Operations (FR-006–014)
- **006** Open: .adoc/.asciidoc/.asc/.txt, Ctrl+O
- **007** Save: atomic_save_text(), Ctrl+S (15 tests)
- **008** Save As: Ctrl+Shift+S
- **009** New: Ctrl+N, unsaved prompt
- **010** Recent: Max 10, persistent
- **011** Auto-Save: 5min timer
- **012** Import DOCX: python-docx
- **013** Import PDF: PyMuPDF (3-5x faster)
- **014** Import MD: Pandoc

### Preview (FR-015–020)
- **015** Live Preview: PreviewWorker, <200ms small/<750ms large
- **016** GPU: QWebEngineView, 10-50x faster, 24hr cache
- **017** Scroll Sync: Editor ↔ preview (8 tests)
- **018** Incremental: Block cache, MD5, LRU(100), 3-5x faster
- **019** Debounce: Adaptive 500ms
- **020** Themes: CSS injection

### Export (FR-021–025)
- **021** HTML: asciidoc3, standalone
- **022** PDF: wkhtmltopdf
- **023** DOCX: Pandoc + Ollama optional
- **024** Markdown: Pandoc
- **025** AI Export: Ollama enhancement

### Git (FR-026–033)
- **026** Select Repo: .git validation, persistent
- **027** Commit: GitWorker, shell=False, Ctrl+G
- **028** Pull: GitWorker.pull_changes() (8 tests)
- **029** Push: GitWorker.push_changes()
- **030** Status Bar: ✓(green)/#(yellow)/⚠(red), 5s refresh
- **031** Status Dialog: 3 tabs, Ctrl+Shift+G
- **032** Quick Commit: Ctrl+G/Enter/Esc
- **033** Cancel: Long ops cancelable

### GitHub CLI (FR-034–038)
- **034** Create PR: gh pr create
- **035** List PRs: Filter open/closed/merged
- **036** Create Issue: Title/body/labels
- **037** List Issues: Filter open/closed
- **038** Repo Info: Stars/forks/branch

### AI/Ollama (FR-039–044)
- **039** Ollama: improve-grammar/llama2/mistral/codellama (82 tests)
- **040** Chat Panel: ChatPanelWidget
- **041** Context Modes: Doc Q&A/Syntax/General/Editing
- **042** History: Max 100, persistent
- **043** Model Switch: Dropdown, validation
- **044** Toggle: Tools menu

### Find & Replace (FR-045–049)
- **045** Find: SearchEngine, Ctrl+F, 50ms/10K lines (33 tests)
- **046** Find Bar: VSCode-style (21 tests)
- **047** Next/Prev: F3/Shift+F3
- **048** Replace: Ctrl+H
- **049** Confirm All: Count shown

### Spell Check (FR-050–054)
- **050** Real-Time: pyspellchecker, 500ms debounce
- **051** Manager: F7 toggle
- **052** Context Menu: 5 suggestions
- **053** Custom Dict: Persistent
- **054** Multi-Lang: en/es/fr/de

### UI/UX (FR-055–061)
- **055** Themes: Dark/light, F11
- **056** Status Bar: Version/Words/Grade/Git/AI
- **057** Metrics: Word count, Flesch-Kincaid
- **058** Window Title: {APP} - {file}*
- **059** Splitter: 3 widgets, persistent
- **060** Toolbar: Icons
- **061** Menu Bar: File/Edit/View/Tools/Git/Help

### Performance (FR-062–067c)
- **062** Startup: 0.586s, -OO flag
- **063** Worker Pool: CPU*2 threads
- **064** Memory: <100MB idle/<500MB large
- **065** Async I/O: aiofiles
- **066** Block Detection: 10-14% faster
- **067** Cache: LRU(100), 76% hit rate
- **067a** Incremental: 10-50x speedup
- **067b** Predictive: 28% latency reduction
- **067c** Priority: Visible blocks first

### Security (FR-068–072)
- **068** Path Sanitization: sanitize_path()
- **069** Atomic Writes: temp+rename
- **070** Subprocess: shell=False only
- **071** Credentials: OS keyring
- **072** HTTPS: SSL verified

### Additional (FR-073–084)
- **073** Telemetry: Opt-in, no PII
- **074** Settings: JSON, Pydantic
- **075** Types: 100% mypy --strict
- **076** Tests: 96.4% coverage
- **077** Pre-commit: ruff/whitespace/YAML
- **078** Docs: Grade 5.0
- **079** Accessibility: Keyboard shortcuts
- **080** Crash Recovery: Auto-save
- **081** Version Display: Auto-extract
- **082** Resource Monitor: psutil
- **083** Large Files: 10MB chunked
- **084** LRU Cache: 100 blocks

### Auto-Complete (FR-085–090)
- **085** Syntax: Ctrl+Space, 20-40ms
- **086** Attributes: : or { trigger
- **087** Cross-Refs: << trigger
- **088** Includes: include:: trigger
- **089** Snippets: table3x3/codeblock/etc
- **090** Fuzzy: 0.3 threshold

### Syntax Check (FR-091–099)
- **091** Real-Time: 500ms debounce, <100ms/1K lines
- **092** Errors: E001-E099
- **093** Semantic: E100-E199
- **094** Warnings: W001-W099
- **095** Style: I001-I099
- **096** Hover: QToolTip
- **097** Quick Fixes: Lightbulb
- **098** Navigation: F2/Shift+F2
- **099** Toggle: F8

### Templates (FR-100–107)
- **100** Built-In: 6 types (Article/Book/ManPage/Report/README/General)
- **101** Variables: {{var}} syntax
- **102** Browser: Ctrl+Shift+N
- **103** Form: Type-specific inputs
- **104** Custom: CRUD, import/export
- **105** Categories: 5 types
- **106** Preview: 300ms debounce
- **107** Instantiation: <200ms

### Standards (FR-108–109)
- **108** MA Principle: <400 lines/file, focused modules
- **109** LSP Server: Completion, diagnostics, hover, symbols (54 tests)

---

*109 FRs | 100% implemented | v2.1.0 Public Release*
