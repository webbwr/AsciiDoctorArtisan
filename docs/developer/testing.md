# Testing Guide

**v2.1.0** | 5,139 tests (95% coverage)

---

## Quick Start

```bash
make test              # All tests + coverage
pytest tests/unit/     # Unit only
pytest tests/e2e/      # E2E only
pytest -k "test_name"  # Specific test
```

---

## Test Structure

```
tests/
├── unit/           # 70% - Fast, isolated
│   ├── core/       # Settings, GPU, file ops
│   ├── ui/         # Managers, dialogs
│   └── workers/    # Git, Pandoc, preview
├── e2e/            # 10% - Full workflows
└── conftest.py     # Shared fixtures
```

---

## Markers

```python
@pytest.mark.slow           # >1 second
@pytest.mark.live_api       # Requires Ollama
@pytest.mark.requires_gpu   # GPU hardware
```

Skip markers: `pytest -m "not live_api"`

---

## Qt Testing

```python
def test_widget(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)  # Auto cleanup
    qtbot.mouseClick(widget.button, Qt.LeftButton)
    assert widget.clicked

# Wait for signals
with qtbot.waitSignal(worker.finished, timeout=5000):
    worker.start()
```

### MockParentWidget

PySide6 rejects MagicMock parents. Use real widget:

```python
# tests/unit/ui/conftest.py
@pytest.fixture
def mock_parent_widget(qtbot):
    widget = MockParentWidget()
    qtbot.addWidget(widget)
    yield widget
```

---

## Coverage

```bash
pytest --cov=src/asciidoc_artisan --cov-report=html
```

**Targets:** Core 99%, UI 95%, Workers 93%

**Note:** Qt threading limits coverage.py tracking in QThread.run()

---

## Best Practices

**DO:**
- Descriptive test names: `test_file_manager_saves_atomically`
- One assertion per test
- Use fixtures for setup
- Mock external deps

**DON'T:**
- Test Qt internals
- Use `time.sleep()` — use `qtbot.waitSignal()`
- Skip tests without documented reason

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tests hang | Add timeout: `qtbot.waitSignal(..., timeout=5000)` |
| ImportError | `pip install -e .` or set PYTHONPATH |
| Qt platform error | `export QT_QPA_PLATFORM=offscreen` |

---

*v2.1.0 | Dec 5, 2025*
