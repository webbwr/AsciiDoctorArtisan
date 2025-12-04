# Scripts

**v2.1.0** | Development utilities

## Structure

```
scripts/
├── benchmarking/     # Performance benchmarks
├── profiling/        # Memory/startup profiling
├── security/         # Security auditing
└── tools/            # Dev utilities
```

## Quick Reference

```bash
# Profiling
python scripts/profiling/measure_startup_time.py
python scripts/profiling/memory_profile.py

# Benchmarking
python scripts/benchmarking/benchmark_performance.py

# Documentation
python scripts/tools/readability_check.py README.md

# Security
python scripts/security/analyze_security_audit.py
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `measure_startup_time.py` | Profile startup |
| `memory_profile.py` | Memory usage |
| `benchmark_performance.py` | Performance metrics |
| `readability_check.py` | Doc readability (Grade 5.0) |

---

*Requires virtual environment activated*
