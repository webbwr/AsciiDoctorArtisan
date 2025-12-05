# AsciiDoc Artisan Installation Script for Windows
# VERSION: 2.1.0
# Usage: powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1

$ErrorActionPreference = "Stop"
$PYTHON_MIN_VERSION = "3.11"
$ERRORS = 0
$WARNINGS = 0

function Write-Header { param([string]$Message); Write-Host "`n=== $Message ===`n" -ForegroundColor Blue }
function Write-Success { param([string]$Message); Write-Host "[+] $Message" -ForegroundColor Green }
function Write-ErrorMsg { param([string]$Message); Write-Host "[-] $Message" -ForegroundColor Red; $script:ERRORS++ }
function Write-Warning { param([string]$Message); Write-Host "[!] $Message" -ForegroundColor Yellow; $script:WARNINGS++ }
function Write-Info { param([string]$Message); Write-Host "[*] $Message" -ForegroundColor Cyan }

function Compare-Version { param([string]$v1, [string]$v2); [version]$v1 -ge [version]$v2 }

# Step 1: Find Python 3.11+
Write-Header "Checking Python Installation"
$PYTHON_CMD = $null
foreach ($cmd in @("py", "python3.12", "python3.11", "python3", "python")) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -match "Python (\d+\.\d+\.\d+)") {
            $ver = $Matches[1]
            $major_minor = $ver.Substring(0, $ver.LastIndexOf('.'))
            if (Compare-Version $major_minor $PYTHON_MIN_VERSION) {
                $PYTHON_CMD = $cmd
                $pythonPath = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
                Write-Success "Found Python $ver at $pythonPath"
                break
            } else {
                Write-Warning "Found Python $ver (need >= $PYTHON_MIN_VERSION)"
            }
        }
    } catch { continue }
}

if (-not $PYTHON_CMD) {
    Write-ErrorMsg "Python $PYTHON_MIN_VERSION+ not found"
    Write-Host "`nInstall Python from: https://www.python.org/downloads/"
    Write-Host "Or: choco install python312"
    exit 1
}

# Step 2: Verify pip
Write-Header "Checking pip"
try {
    $pipVersion = & $PYTHON_CMD -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $pipVersion -match "pip (\d+\.\d+)") {
        Write-Success "pip $($Matches[1])"
    } else { throw }
} catch {
    Write-Info "Installing pip..."
    & $PYTHON_CMD -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) { Write-ErrorMsg "Failed to install pip"; exit 1 }
    Write-Success "pip installed"
}

# Step 3: Check system dependencies
Write-Header "Checking System Dependencies"

# Pandoc
try {
    $pandocVer = & pandoc --version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0 -and $pandocVer -match "pandoc (\d+\.\d+)") {
        Write-Success "Pandoc $($Matches[1])"
    } else { throw }
} catch {
    Write-Warning "Pandoc not found - Install from: https://pandoc.org/installing.html"
    Write-Host "  Or: choco install pandoc"
}

# wkhtmltopdf
try {
    $null = & wkhtmltopdf --version 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Success "wkhtmltopdf installed" } else { throw }
} catch {
    Write-Warning "wkhtmltopdf not found - PDF export disabled"
    Write-Host "  Install from: https://wkhtmltopdf.org/downloads.html"
    Write-Host "  Or: choco install wkhtmltopdf"
}

# Git
try {
    $gitVer = & git --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $gitVer -match "git version (\S+)") {
        Write-Success "Git $($Matches[1])"
    } else { throw }
} catch {
    Write-Warning "Git not found (optional)"
}

# GitHub CLI
try {
    $null = & gh --version 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Success "GitHub CLI installed" } else { throw }
} catch {
    Write-Info "GitHub CLI not installed (optional: choco install gh)"
}

# Step 4: Virtual environment
Write-Header "Virtual Environment Setup"
$response = Read-Host "Create virtual environment? (recommended) [Y/n]"
if ($response -eq "" -or $response -match "^[Yy]") {
    Write-Info "Creating venv..."
    try {
        & $PYTHON_CMD -m venv venv
        $activateScript = ".\venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
            $PYTHON_CMD = "python"
            Write-Success "Virtual environment created and activated"
        } else { throw "Activate script not found" }
    } catch {
        Write-ErrorMsg "Failed to create venv: $_"
        exit 1
    }
} else {
    Write-Warning "Installing globally (not recommended)"
}

# Step 5: Install Python packages
Write-Header "Installing Python Dependencies"
& $PYTHON_CMD -m pip install --upgrade pip --quiet

if (Test-Path "requirements-prod.txt") {
    Write-Info "Installing from requirements-prod.txt..."
    & $PYTHON_CMD -m pip install -r requirements-prod.txt --quiet
    Write-Success "Production dependencies installed"
} elseif (Test-Path "requirements.txt") {
    Write-Info "Installing from requirements.txt..."
    & $PYTHON_CMD -m pip install -r requirements.txt --quiet
    Write-Success "Dependencies installed"
} else {
    Write-Info "Installing core packages..."
    $packages = @("PySide6>=6.9.0", "asciidoc3>=3.2.0", "pypandoc>=1.11", "pymupdf>=1.26.0", "keyring>=24.0.0", "psutil>=5.9.0")
    foreach ($pkg in $packages) {
        & $PYTHON_CMD -m pip install $pkg --quiet
    }
    Write-Success "Core packages installed"
}

# Step 6: Validate installation
Write-Header "Validating Installation"
$packages = @("PySide6", "asciidoc3", "pypandoc", "fitz", "keyring", "psutil")
foreach ($pkg in $packages) {
    $test = & $PYTHON_CMD -c "import $pkg" 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Success $pkg }
    else { Write-ErrorMsg "$pkg not importable" }
}

# Test application import
$appTest = & $PYTHON_CMD -c "from asciidoc_artisan.ui.main_window import AsciiDocEditor" 2>&1
if ($LASTEXITCODE -eq 0) { Write-Success "Application modules verified" }
else { Write-Warning "Run 'pip install -e .' for editable install" }

# Summary
Write-Header "Installation Summary"
$pyVer = & $PYTHON_CMD --version 2>&1
$pyLoc = (Get-Command $PYTHON_CMD -ErrorAction SilentlyContinue).Source
Write-Host "Python:   $pyVer"
Write-Host "Location: $pyLoc"
Write-Host "Errors:   $ERRORS"
Write-Host "Warnings: $WARNINGS"
Write-Host ""

if ($ERRORS -eq 0) {
    Write-Success "Installation complete!"
    Write-Host ""
    Write-Host "Run the application:"
    Write-Host "  python src\main.py"
    Write-Host ""
    if (Test-Path "venv") {
        Write-Host "Reactivate venv: .\venv\Scripts\Activate.ps1"
    }
    exit 0
} else {
    Write-ErrorMsg "Installation failed with $ERRORS errors"
    exit 1
}
