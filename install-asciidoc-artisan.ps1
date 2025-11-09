################################################################################
# AsciiDoc Artisan - Full Clean Installation Script for Windows (PowerShell)
#
# PURPOSE:
#   Automates complete installation of AsciiDoc Artisan with:
#   - Python 3.11+ verification
#   - Virtual environment creation
#   - All dependencies (Python packages + system tools)
#   - Installation validation
#
# USAGE:
#   powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1
#
# WHAT IT DOES:
#   1. Checks Python version (needs 3.11+)
#   2. Verifies pip is installed
#   3. Checks system dependencies (Pandoc, Git)
#   4. Creates virtual environment (optional)
#   5. Installs Python packages
#   6. Validates installation
#   7. Shows summary
#
# EXIT CODES:
#   0 = Success
#   1 = Error (missing dependencies or failed installation)
#
# AUTHOR: AsciiDoc Artisan Team
# VERSION: 1.0.0
################################################################################

# Enable strict mode for better error handling
$ErrorActionPreference = "Stop"

################################################################################
# CONFIGURATION
################################################################################

# Minimum Python version required (Major.Minor)
$PYTHON_MIN_VERSION = "3.11"

# Required Python packages with minimum versions
$REQUIRED_PYTHON_PACKAGES = @(
    "PySide6>=6.9.0",      # Qt GUI framework with GPU support
    "asciidoc3>=3.2.0",    # AsciiDoc to HTML conversion
    "pypandoc>=1.11",      # Document format conversion wrapper
    "pdfplumber>=0.10.0",  # PDF text extraction (legacy fallback)
    "keyring>=24.0.0",     # Secure credential storage
    "psutil>=5.9.0"        # System and process utilities
)

# Validation counters
$ERRORS = 0
$WARNINGS = 0

################################################################################
# HELPER FUNCTIONS
################################################################################

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[" -NoNewline
    Write-Host "✓" -ForegroundColor Green -NoNewline
    Write-Host "] $Message"
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[" -NoNewline
    Write-Host "✗" -ForegroundColor Red -NoNewline
    Write-Host "] $Message"
    $script:ERRORS++
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[" -NoNewline
    Write-Host "⚠" -ForegroundColor Yellow -NoNewline
    Write-Host "] $Message"
    $script:WARNINGS++
}

function Write-Info {
    param([string]$Message)
    Write-Host "[" -NoNewline
    Write-Host "ℹ" -ForegroundColor Cyan -NoNewline
    Write-Host "] $Message"
}

function Compare-Version {
    param(
        [string]$Version1,
        [string]$Version2
    )
    $v1 = [version]$Version1
    $v2 = [version]$Version2
    return $v1 -ge $v2
}

################################################################################
# STEP 1: CHECK PYTHON INSTALLATION
################################################################################
Write-Header "Step 1: Checking Python Installation"

$PYTHON_CMD = $null
$PYTHON_VERSION_FULL = $null

# Try common Python commands in order of preference
$PythonCommands = @("py", "python3.12", "python3.11", "python3", "python")

foreach ($cmd in $PythonCommands) {
    try {
        # Check if command exists
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            # Extract version string (e.g., "Python 3.12.0")
            $versionMatch = $result -match "Python (\d+\.\d+\.\d+)"
            if ($versionMatch -and $Matches[1]) {
                $PYTHON_VERSION_FULL = $Matches[1]
                $PYTHON_MAJOR_MINOR = $PYTHON_VERSION_FULL.Substring(0, $PYTHON_VERSION_FULL.LastIndexOf('.'))

                # Check if version meets minimum requirement
                if (Compare-Version $PYTHON_MAJOR_MINOR $PYTHON_MIN_VERSION) {
                    $PYTHON_CMD = $cmd
                    $pythonPath = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
                    Write-Success "Found Python $PYTHON_VERSION_FULL at $pythonPath"
                    break
                } else {
                    Write-Warning "Found Python $PYTHON_VERSION_FULL (too old, need >= $PYTHON_MIN_VERSION)"
                }
            }
        }
    } catch {
        # Command not found or error - continue to next
        continue
    }
}

# If no suitable Python found, show installation instructions and exit
if (-not $PYTHON_CMD) {
    Write-ErrorMsg "Python $PYTHON_MIN_VERSION or higher not found"
    Write-Host ""
    Write-Host "Installation instructions:"
    Write-Host "  1. Download Python from: https://www.python.org/downloads/"
    Write-Host "  2. During installation, check 'Add Python to PATH'"
    Write-Host "  3. Restart PowerShell after installation"
    Write-Host ""
    Write-Host "Alternative: Install via Chocolatey:"
    Write-Host "  choco install python312"
    exit 1
}

################################################################################
# STEP 2: CHECK PIP INSTALLATION
################################################################################
Write-Header "Step 2: Checking pip Installation"

try {
    $pipVersion = & $PYTHON_CMD -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $versionMatch = $pipVersion -match "pip (\d+\.\d+\.\d+)"
        if ($versionMatch -and $Matches[1]) {
            Write-Success "pip $($Matches[1]) found"
        } else {
            Write-Success "pip found"
        }
    } else {
        throw "pip not found"
    }
} catch {
    Write-ErrorMsg "pip not found for $PYTHON_CMD"
    Write-Host ""
    Write-Host "Installing pip..."
    try {
        & $PYTHON_CMD -m ensurepip --upgrade
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install pip"
        }
        Write-Success "pip installed successfully"
    } catch {
        Write-ErrorMsg "Failed to install pip"
        exit 1
    }
}

################################################################################
# STEP 3: CHECK SYSTEM DEPENDENCIES
################################################################################
Write-Header "Step 3: Checking System Dependencies"

# Check Pandoc (REQUIRED for document conversion)
try {
    $pandocVersion = & pandoc --version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0 -and $pandocVersion -match "pandoc (\d+\.\d+)") {
        Write-Success "Pandoc $($Matches[1]) found"
    } else {
        throw "Pandoc not found"
    }
} catch {
    Write-Warning "Pandoc not found (required for document conversion)"
    Write-Host ""
    Write-Host "Installation instructions:"
    Write-Host "  Download from: https://pandoc.org/installing.html"
    Write-Host "  Or install via Chocolatey: choco install pandoc"
}

# Check Git (OPTIONAL but recommended for version control features)
try {
    $gitVersion = & git --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $gitVersion -match "git version (\S+)") {
        Write-Success "Git $($Matches[1]) found"
    } else {
        throw "Git not found"
    }
} catch {
    Write-Warning "Git not found (optional - needed for Git integration features)"
    Write-Host "  Download from: https://git-scm.com/downloads"
}

################################################################################
# STEP 4: VIRTUAL ENVIRONMENT SETUP
################################################################################
Write-Header "Step 4: Virtual Environment Setup"

$response = Read-Host "Create virtual environment? (recommended) [Y/n]"
if ($response -eq "" -or $response -match "^[Yy]") {
    Write-Info "Creating virtual environment in .\venv"
    try {
        & $PYTHON_CMD -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create venv"
        }

        # Activate virtual environment
        $activateScript = ".\venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
            Write-Success "Virtual environment created and activated"
            # From now on, use "python" from venv
            $PYTHON_CMD = "python"
        } else {
            throw "Activate script not found"
        }
    } catch {
        Write-ErrorMsg "Failed to create virtual environment: $_"
        exit 1
    }
} else {
    Write-Warning "Skipping virtual environment (installing globally)"
}

################################################################################
# STEP 5: INSTALL PYTHON DEPENDENCIES
################################################################################
Write-Header "Step 5: Installing Python Dependencies"

# First upgrade pip to latest version
Write-Info "Upgrading pip..."
& $PYTHON_CMD -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to upgrade pip (continuing anyway)"
}

# Install packages from requirements file if available
if (Test-Path "requirements-production.txt") {
    Write-Info "Installing from requirements-production.txt..."
    & $PYTHON_CMD -m pip install -r requirements-production.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production dependencies installed"
    } else {
        Write-ErrorMsg "Failed to install from requirements-production.txt"
    }
} elseif (Test-Path "requirements.txt") {
    Write-Info "Installing from requirements.txt..."
    & $PYTHON_CMD -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed"
    } else {
        Write-ErrorMsg "Failed to install from requirements.txt"
    }
} else {
    # No requirements file - install packages from array
    Write-Info "Installing core packages..."
    foreach ($package in $REQUIRED_PYTHON_PACKAGES) {
        Write-Info "Installing $package..."
        & $PYTHON_CMD -m pip install $package --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to install $package"
        }
    }
    Write-Success "Core packages installed"
}

################################################################################
# STEP 6: VALIDATION
################################################################################
Write-Header "Step 6: Validating Installation"

# Validate Python packages
Write-Info "Checking installed packages..."
foreach ($package in $REQUIRED_PYTHON_PACKAGES) {
    $packageName = $package -replace '>=.*$', ''
    $packageNameUnderscore = $packageName -replace '-', '_'

    # Try to import package
    $importTest = & $PYTHON_CMD -c "import $packageName" 2>&1
    $importTestUnderscore = & $PYTHON_CMD -c "import $packageNameUnderscore" 2>&1

    if ($LASTEXITCODE -eq 0 -or $importTest -eq "" -or $importTestUnderscore -eq "") {
        # Get installed version
        $versionOutput = & $PYTHON_CMD -m pip show $packageName 2>$null | Select-String "Version:"
        if ($versionOutput) {
            $version = ($versionOutput -split ": ")[1]
            Write-Success "$packageName $version"
        } else {
            Write-Success "$packageName installed"
        }
    } else {
        Write-ErrorMsg "$packageName not found or cannot be imported"
    }
}

# Validate system commands
Write-Info "Checking system commands..."
$commands = @(
    @{Name="Python"; Cmd=$PYTHON_CMD; Required=$true},
    @{Name="pip"; Cmd="pip"; Required=$true},
    @{Name="pandoc"; Cmd="pandoc"; Required=$false},
    @{Name="git"; Cmd="git"; Required=$false}
)

foreach ($cmdInfo in $commands) {
    try {
        $cmdPath = (Get-Command $cmdInfo.Cmd -ErrorAction SilentlyContinue).Source
        if ($cmdPath) {
            Write-Success "$($cmdInfo.Name): $cmdPath"
        } else {
            throw "Not found"
        }
    } catch {
        if ($cmdInfo.Required) {
            Write-ErrorMsg "$($cmdInfo.Name): not found (required)"
        } else {
            Write-Warning "$($cmdInfo.Name): not found (optional)"
        }
    }
}

# Test application launch
Write-Info "Testing application import..."
$importTest = & $PYTHON_CMD -c "from asciidoc_artisan.ui.main_window import AsciiDocEditor" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Application modules can be imported"
} else {
    Write-Warning "Application modules not yet installed (run: pip install -e .)"
}

################################################################################
# STEP 7: SUMMARY
################################################################################
Write-Header "Installation Summary"

$pythonVersionOutput = & $PYTHON_CMD --version 2>&1
$pythonLocation = (Get-Command $PYTHON_CMD -ErrorAction SilentlyContinue).Source
$pipVersionOutput = & $PYTHON_CMD -m pip --version 2>&1

Write-Host "Python Version:    $pythonVersionOutput"
Write-Host "Python Location:   $pythonLocation"
Write-Host "Pip Version:       $pipVersionOutput"
Write-Host ""
Write-Host "Errors:            $ERRORS"
Write-Host "Warnings:          $WARNINGS"
Write-Host ""

if ($ERRORS -eq 0) {
    Write-Success "Installation completed successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Launch the application:"
    Write-Host "     python src\main.py"
    Write-Host ""
    if (Test-Path "venv") {
        Write-Host "  Note: Virtual environment is active. To deactivate:"
        Write-Host "     deactivate"
        Write-Host ""
        Write-Host "  To reactivate later:"
        Write-Host "     .\venv\Scripts\Activate.ps1"
        Write-Host ""
    }
    exit 0
} else {
    Write-ErrorMsg "Installation completed with $ERRORS errors"
    Write-Host ""
    Write-Host "Please resolve the errors above and try again."
    exit 1
}
