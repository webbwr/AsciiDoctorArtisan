# Scripts Directory

This directory contains utility scripts for development, profiling, benchmarking, and security auditing.

## Structure

```
scripts/
├── benchmarking/          # Performance benchmarks
├── profiling/             # Memory and startup profiling
├── security/              # Security audit scripts
└── tools/                 # Development utilities
```

## Benchmarking Scripts (`benchmarking/`)

Scripts to measure application performance.

### `benchmark_performance.py`
Benchmarks overall application performance metrics.

**Usage:**
```bash
python scripts/benchmarking/benchmark_performance.py
```

### `benchmark_predictive_rendering.py`
Benchmarks predictive rendering system performance.

**Usage:**
```bash
python scripts/benchmarking/benchmark_predictive_rendering.py
```

## Profiling Scripts (`profiling/`)

Scripts to profile memory usage, startup time, and import performance.

### `memory_profile.py`
Profiles memory usage during operation.

**Usage:**
```bash
python scripts/profiling/memory_profile.py
```

### `measure_startup_time.py`
Measures application startup time.

**Usage:**
```bash
python scripts/profiling/measure_startup_time.py
```

### `measure_import_time.py`
Measures module import times.

**Usage:**
```bash
python scripts/profiling/measure_import_time.py
```

### `profile_block_detection.py`
Profiles block detection performance for incremental rendering.

**Usage:**
```bash
python scripts/profiling/profile_block_detection.py
```

### `performance_profiler.py`
Comprehensive performance profiling script.

**Usage:**
```bash
python scripts/profiling/performance_profiler.py
```

## Security Scripts (`security/`)

Scripts for security auditing and analysis.

### `analyze_security_audit.py`
Analyzes security audit results.

**Usage:**
```bash
python scripts/security/analyze_security_audit.py
```

### `demo_security_audit.py`
Demonstrates security audit capabilities.

**Usage:**
```bash
python scripts/security/demo_security_audit.py
```

### `query_security_audit.sh`
Queries security audit database.

**Usage:**
```bash
bash scripts/security/query_security_audit.sh
```

## Development Tools (`tools/`)

General development and maintenance utilities.

### `readability_check.py`
Checks documentation readability (Flesch-Kincaid Grade Level).

**Usage:**
```bash
python scripts/tools/readability_check.py <file.md>
```

**Target**: Grade 5.0 reading level or lower

### `check_readability.py`
Alternative readability checker.

**Usage:**
```bash
python scripts/tools/check_readability.py <file.md>
```

### `run_coverage.sh`
Runs test coverage and generates reports.

**Usage:**
```bash
bash scripts/tools/run_coverage.sh
```

### `techwriter` / `tw`
Technical writing assistant for documentation.

**Usage:**
```bash
scripts/tools/techwriter <command>
# or shortcut:
scripts/tools/tw <command>
```

## Quick Reference

### Performance Analysis
```bash
# Profile startup time
python scripts/profiling/measure_startup_time.py

# Benchmark rendering
python scripts/benchmarking/benchmark_predictive_rendering.py

# Memory profiling
python scripts/profiling/memory_profile.py
```

### Security Auditing
```bash
# Run security analysis
python scripts/security/analyze_security_audit.py

# Query audit results
bash scripts/security/query_security_audit.sh
```

### Documentation Quality
```bash
# Check readability
python scripts/tools/readability_check.py README.md

# Run coverage
bash scripts/tools/run_coverage.sh
```

## Adding New Scripts

When adding new scripts:

1. Place in appropriate subdirectory by purpose
2. Make executable: `chmod +x script_name.py`
3. Add shebang line: `#!/usr/bin/env python3`
4. Add usage docstring at top of file
5. Update this README with script description

## Notes

- All Python scripts require the virtual environment activated
- Some scripts require `QT_QPA_PLATFORM=offscreen` for headless operation
- Profile scripts may take several minutes to complete
- Benchmark results vary based on system specifications
