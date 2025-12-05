# Performance Guide

**v2.1.0** | Optimization tips and profiling

---

## Current Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Startup | 0.27s | <1.0s ✅ |
| Preview (small) | 150-200ms | <200ms ✅ |
| Preview (large) | 600-750ms | <500ms |
| Auto-complete | 20-40ms | <50ms ✅ |
| Memory | 100-200MB | <200MB ✅ |

---

## Optimization Features

| Feature | Benefit |
|---------|---------|
| GPU acceleration | 10-50x faster rendering |
| Incremental rendering | Only re-render changed blocks |
| Adaptive debouncing | Fast for small docs, efficient for large |
| Block caching | LRU cache (100 blocks) |

---

## User Tips

**Editing:**
- Keep documents <100KB for best performance
- Split large documents into chapters
- Disable preview for large files: Ctrl+P

**Memory:**
- Restart after 2+ hours of editing
- Clear recent files periodically
- Check: 200MB normal, >500MB restart

---

## Developer Profiling

```bash
# Run benchmarks
python scripts/benchmarking/benchmark_performance.py

# Profile specific test
python -m cProfile -o profile.stats -m pytest tests/test_file.py

# Check import time
python3 -c "import time; start=time.time(); from asciidoc_artisan.ui.main_window import AsciiDocEditor; print(f'{(time.time()-start)*1000:.0f}ms')"
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Preview lag | Close other apps, reduce doc size |
| High memory | Restart app, clear cache |
| Slow startup | Clear: `rm -rf ~/.cache/asciidoc_artisan/` |
| No GPU | Works on CPU (auto-fallback) |

---

*v2.1.0 | Dec 5, 2025*
