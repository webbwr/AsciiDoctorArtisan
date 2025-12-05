# MA (間) Principle

**v2.1.0** | Code organization guide

---

## What is MA?

Japanese aesthetic: **negative space**. In code: intentional simplicity.

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." — Saint-Exupéry

---

## Core Rules

| Rule | Metric |
|------|--------|
| File length | <400 lines |
| Function length | <50 lines |
| Parameters | ≤4 per function |
| Nesting depth | ≤3 levels |
| Comment ratio | 5-15% |

---

## Code Patterns

### DO: Focused functions
```python
def atomic_save(path: str, content: str) -> None:
    """Save file atomically via temp-then-rename."""
    temp = path + ".tmp"
    Path(temp).write_text(content)
    os.replace(temp, path)
```

### DON'T: Over-parameterized
```python
def save_file(path, content, encoding='utf-8', backup=True,
              compress=False, validate=True, notify=True): ...
```

---

## Comments

### DO: Explain "why"
```python
# 24hr cache avoids 100ms GPU detection overhead
@lru_cache(maxsize=1)
def detect_gpu() -> GPUInfo: ...
```

### DON'T: State the obvious
```python
# Increment counter by 1
counter += 1
```

---

## Documentation

- **Concise** — Every word earns its place
- **No redundancy** — Say it once
- **Focus on "why"** — Code shows "how"
- **Strategic whitespace** — Visual breathing room

---

## Review Checklist

- [ ] Can I remove code without losing functionality?
- [ ] Are comments explaining "why," not "what"?
- [ ] Is there whitespace between logical sections?
- [ ] Are functions focused on one thing?

---

*v2.1.0 | Dec 5, 2025*
