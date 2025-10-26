<#
################################################################################
# AsciiDoc Artisan - Full Clean Installation Script for Windows
#
# PURPOSE:
#   Automates complete installation of AsciiDoc Artisan on Windows with:
#   - PowerShell 7.0+ verification
#   - Python 3.11+ verification
#   - Virtual environment creation
#   - All dependencies (Python packages + system tools)
#   - Installation validation
#
# USAGE:
#   .\install-asciidoc-artisan.ps1
#   .\install-asciidoc-artisan.ps1 -PythonCommand python3
#   .\install-asciidoc-artisan.ps1 -SkipVirtualEnv
#
# WHAT IT DOES:
#   1. Checks PowerShell version (needs 7.0+)
#   2. Checks Windows version
#   3. Checks Python version (needs 3.11+)
#   4. Verifies pip is installed
#   5. Installs system dependencies (Pandoc, Git)
#   6. Creates virtual environment (optional)
#   7. Installs Python packages
#   8. Runs post-install tasks
#   9. Validates installation
#   10. Shows summary
#
# EXIT CODES:
#   0 = Success
#   1 = Error (missing dependencies or failed installation)
#
# AUTHOR: AsciiDoc Artisan Team
# VERSION: 1.2.0
################################################################################

.SYNOPSIS
    AsciiDoc Artisan - Full Clean Installation Script for Windows

.DESCRIPTION
    This script performs a complete installation of AsciiDoc Artisan with all
    dependencies and validates the installation. Requires PowerShell 7.0+.

.PARAMETER PythonCommand
    Python command to use (default: 'python')
    Examples: 'python', 'python3', 'python3.12', 'py'

.PARAMETER SkipVirtualEnv
    Skip virtual environment creation
    Use this flag to install packages globally instead of in a venv

.EXAMPLE
    .\install-asciidoc-artisan.ps1
    Standard installation with virtual environment

.EXAMPLE
    .\install-asciidoc-artisan.ps1 -PythonCommand python3
    Use specific Python command

.EXAMPLE
    .\install-asciidoc-artisan.ps1 -SkipVirtualEnv
    Install globally without virtual environment

.NOTES
    Author:      AsciiDoc Artisan Team
    Version:     1.2.0
    Requires:    PowerShell 7.0+, Python 3.11+
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    # Python command to use (tries this first, then falls back to alternatives)
    [Parameter(Mandatory = $false)]
    [string]$PythonCommand = "python",

    # Skip virtual environment creation (install globally instead)
    [Parameter(Mandatory = $false)]
    [switch]$SkipVirtualEnv
)

################################################################################
# CONFIGURATION
################################################################################

# Minimum Python version required (Major.Minor)
$PYTHON_MIN_VERSION = "3.11"

# Required Python packages with minimum versions
# These are the core dependencies needed to run AsciiDoc Artisan
$REQUIRED_PACKAGES = @(
    @{ Name = "PySide6";     VersionSpec = ">=6.9.0" }   # Qt GUI framework with GPU support
    @{ Name = "asciidoc3";   VersionSpec = ">=3.2.0" }   # AsciiDoc to HTML conversion
    @{ Name = "pypandoc";    VersionSpec = ">=1.11" }    # Document format conversion wrapper
    @{ Name = "pdfplumber";  VersionSpec = ">=0.10.0" }  # PDF text extraction (legacy fallback)
    @{ Name = "keyring";     VersionSpec = ">=24.0.0" }  # Secure credential storage
    @{ Name = "psutil";      VersionSpec = ">=5.9.0" }   # System and process utilities
)

# Validation counters
# Script-level variables to track issues found during installation
$script:Errors = 0      # Critical issues that prevent installation
$script:Warnings = 0    # Non-critical issues that may affect functionality

################################################################################
# HELPER FUNCTIONS
################################################################################

<#
.SYNOPSIS
    Print a blue header for major installation steps
.PARAMETER Message
    The step description to display
#>
function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

<#
.SYNOPSIS
    Print a success message with green checkmark
.PARAMETER Message
    The success message to display
#>
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

<#
.SYNOPSIS
    Print an error message with red X and increment error counter
.PARAMETER Message
    The error message to display
#>
function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $script:Errors++
}

<#
.SYNOPSIS
    Print a warning message with yellow symbol and increment warning counter
.PARAMETER Message
    The warning message to display
#>
function Write-WarningMsg {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
    $script:Warnings++
}

<#
.SYNOPSIS
    Print an info message with cyan info symbol
.PARAMETER Message
    The info message to display
#>
function Write-InfoMsg {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

<#
.SYNOPSIS
    Compare two version numbers
.DESCRIPTION
    Returns $true if Version1 >= Version2, otherwise $false
.PARAMETER Version1
    First version string (e.g., "3.12.0")
.PARAMETER Version2
    Second version string (e.g., "3.11")
.EXAMPLE
    if (Compare-Version "3.12.0" "3.11") { ... }
#>
function Compare-Version {
    param(
        [string]$Version1,
        [string]$Version2
    )
    # PowerShell [version] type handles version comparison
    $v1 = [version]$Version1
    $v2 = [version]$Version2
    return $v1 -ge $v2
}

<#
.SYNOPSIS
    Test if a command exists and is not a stub
.DESCRIPTION
    Checks if a command is available in PATH
    Also detects and rejects Microsoft Store Python stub on Windows
.PARAMETER CommandName
    Name of the command to check
.EXAMPLE
    if (Test-CommandExists "python") { ... }
#>
function Test-CommandExists {
    param([string]$CommandName)

    # Try to get command info
    $commandInfo = Get-Command $CommandName -ErrorAction SilentlyContinue

    if ($commandInfo) {
        # Special handling for Python commands
        # Microsoft Store installs a stub that opens the Store, not real Python
        if (($CommandName -eq 'python' -or $CommandName -eq 'python3') -and
            ($commandInfo.Source -like "*Microsoft\WindowsApps*")) {
            # This is the Store stub, not real Python
            return $false
        }
        # Command exists and is real
        return $true
    }

    # Command not found
    return $false
}

################################################################################
# MAIN INSTALLATION PROCESS
################################################################################

################################################################################
# STEP 1: CHECK POWERSHELL VERSION
# Requires PowerShell 7.0+ for modern cmdlets and error handling
################################################################################
Write-Header "Step 1: Checking PowerShell Version"

# Check if PowerShell version meets minimum requirement
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-ErrorMsg "This script requires PowerShell 7.0 or higher"
    Write-Host "`nCurrent version: $($PSVersionTable.PSVersion)" -ForegroundColor Red
    Write-Host "Download PowerShell 7: https://github.com/PowerShell/PowerShell/releases" -ForegroundColor Yellow
    exit 1
}

Write-Success "PowerShell $($PSVersionTable.PSVersion) detected"

################################################################################
# STEP 2: CHECK WINDOWS VERSION
# Detects Windows version and warns if not Windows 11
################################################################################
Write-Header "Step 2: Checking Windows Version"

# Get OS information using CIM (Common Information Model)
$osInfo = Get-CimInstance Win32_OperatingSystem
$osVersion = $osInfo.Caption  # e.g., "Microsoft Windows 11 Pro"
Write-Success "$osVersion detected"

# Warn if not Windows 11 (build 22000+)
# App should work on Windows 10, but Windows 11 is recommended
if ($osInfo.BuildNumber -lt 22000) {
    Write-WarningMsg "Windows 11 recommended (Build 22000+), detected Build $($osInfo.BuildNumber)"
}

################################################################################
# STEP 3: CHECK PYTHON INSTALLATION
# Finds suitable Python version (3.11+) and sets $PythonCommand variable
################################################################################
Write-Header "Step 3: Checking Python Installation"

# Variables to track Python discovery
$pythonFound = $false
$pythonExecutable = ""
$pythonVersion = ""

################################################################################
# Try the user-specified Python command first (from -PythonCommand parameter)
################################################################################
if (Test-CommandExists $PythonCommand) {
    try {
        # Get version string (e.g., "Python 3.12.0")
        $versionOutput = & $PythonCommand --version 2>&1

        # Extract version number using regex
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            $pythonVersion = $matches[1]  # e.g., "3.12.0"
            # Get major.minor version (e.g., "3.12")
            $pythonMajorMinor = $pythonVersion.Substring(0, $pythonVersion.LastIndexOf('.'))

            # Check if version meets minimum requirement
            if (Compare-Version $pythonMajorMinor $PYTHON_MIN_VERSION) {
                $pythonExecutable = (Get-Command $PythonCommand).Source
                $pythonFound = $true
                Write-Success "Found Python $pythonVersion at $pythonExecutable"
            }
            else {
                # Found Python but version is too old
                Write-WarningMsg "Python $pythonVersion is too old (need >= $PYTHON_MIN_VERSION)"
            }
        }
    }
    catch {
        # Command failed to execute
        Write-WarningMsg "Could not determine Python version for '$PythonCommand'"
    }
}

################################################################################
# If specified command didn't work, try common Python commands
################################################################################
if (-not $pythonFound) {
    # Try common Python commands in order of preference
    # Prefer specific versions (3.12, 3.11) over generic (python3, py)
    $pythonCommands = @("python3.12", "python3.11", "python3", "py")

    foreach ($cmd in $pythonCommands) {
        if (Test-CommandExists $cmd) {
            try {
                $versionOutput = & $cmd --version 2>&1

                if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
                    $pythonVersion = $matches[1]
                    $pythonMajorMinor = $pythonVersion.Substring(0, $pythonVersion.LastIndexOf('.'))

                    if (Compare-Version $pythonMajorMinor $PYTHON_MIN_VERSION) {
                        $pythonExecutable = (Get-Command $cmd).Source
                        $PythonCommand = $cmd  # Update parameter with working command
                        $pythonFound = $true
                        Write-Success "Found Python $pythonVersion at $pythonExecutable"
                        break  # Found suitable version, stop searching
                    }
                }
            }
            catch {
                # This command didn't work, try next one
                continue
            }
        }
    }
}

################################################################################
# If no suitable Python found, show installation instructions and exit
################################################################################
if (-not $pythonFound) {
    Write-ErrorMsg "Python $PYTHON_MIN_VERSION or higher not found"
    Write-Host "`nInstallation options:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  2. Use Windows Package Manager: winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host "`nMake sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
    exit 1
}

# Step 4: Check pip
Write-Header "Step 4: Checking pip Installation"

try {
    $pipVersion = & $PythonCommand -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        if ($pipVersion -match "pip (\d+\.\d+\.\d+)") {
            Write-Success "pip $($matches[1]) found"
        }
        else {
            Write-Success "pip found"
        }
    }
    else {
        throw "pip not available"
    }
}
catch {
    Write-ErrorMsg "pip not found for $PythonCommand"
    Write-Host "`nInstalling pip..." -ForegroundColor Yellow
    & $PythonCommand -m ensurepip --upgrade

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to install pip"
        exit 1
    }
    Write-Success "pip installed"
}

# Step 5: Check System Dependencies
Write-Header "Step 5: Checking System Dependencies"

# Check Pandoc
if (Test-CommandExists "pandoc") {
    $pandocVersion = (pandoc --version | Select-Object -First 1) -replace "pandoc ", ""
    Write-Success "Pandoc $pandocVersion found"
}
else {
    Write-WarningMsg "Pandoc not found (required for document conversion)"
    Write-Host "`nInstallation options:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://pandoc.org/installing.html" -ForegroundColor Yellow
    Write-Host "  2. Use winget: winget install JohnMacFarlane.Pandoc" -ForegroundColor Yellow
    Write-Host "  3. Use Chocolatey: choco install pandoc" -ForegroundColor Yellow

    $installPandoc = Read-Host "`nAttempt to install Pandoc using winget? [Y/n]"
    if ($installPandoc -ne 'n' -and $installPandoc -ne 'N') {
        if (Test-CommandExists "winget") {
            Write-InfoMsg "Installing Pandoc via winget..."
            winget install --id JohnMacFarlane.Pandoc --silent --accept-package-agreements --accept-source-agreements

            if (Test-CommandExists "pandoc") {
                $pandocVersion = (pandoc --version | Select-Object -First 1) -replace "pandoc ", ""
                Write-Success "Pandoc $pandocVersion installed successfully"
            }
            else {
                Write-WarningMsg "Pandoc installation may require a system restart"
            }
        }
        else {
            Write-WarningMsg "winget not found - please install Pandoc manually"
        }
    }
}

# Check Git
if (Test-CommandExists "git") {
    $gitVersion = (git --version) -replace "git version ", ""
    Write-Success "Git $gitVersion found"
}
else {
    Write-WarningMsg "Git not found (optional - needed for Git integration features)"
    Write-Host "  Install from: https://git-scm.com/downloads" -ForegroundColor Yellow
}

# Step 6: Virtual Environment Setup
Write-Header "Step 6: Virtual Environment Setup"

$useVenv = $true
if ($SkipVirtualEnv) {
    Write-WarningMsg "Skipping virtual environment (installing globally)"
    $useVenv = $false
}
else {
    $venvChoice = Read-Host "Create virtual environment? (recommended) [Y/n]"
    if ($venvChoice -eq 'n' -or $venvChoice -eq 'N') {
        Write-WarningMsg "Skipping virtual environment (installing globally)"
        $useVenv = $false
    }
}

if ($useVenv) {
    Write-InfoMsg "Creating virtual environment in .\venv"
    & $PythonCommand -m venv venv

    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
        Write-Success "Virtual environment created and activated"
        $PythonCommand = "python"  # Use venv python
    }
    else {
        Write-ErrorMsg "Failed to create virtual environment"
        exit 1
    }
}

# Step 7: Install Python Dependencies
Write-Header "Step 7: Installing Python Dependencies"

Write-InfoMsg "Upgrading pip..."
& $PythonCommand -m pip install --upgrade pip --quiet

if (Test-Path "requirements-production.txt") {
    Write-InfoMsg "Installing from requirements-production.txt..."
    & $PythonCommand -m pip install -r requirements-production.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production dependencies installed"
    }
    else {
        Write-ErrorMsg "Failed to install dependencies from requirements-production.txt"
        exit 1
    }
}
elseif (Test-Path "requirements.txt") {
    Write-InfoMsg "Installing from requirements.txt..."
    & $PythonCommand -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed"
    }
    else {
        Write-ErrorMsg "Failed to install dependencies from requirements.txt"
        exit 1
    }
}
else {
    Write-InfoMsg "Installing core packages..."
    foreach ($package in $REQUIRED_PACKAGES) {
        $packageSpec = "$($package.Name)$($package.VersionSpec)"
        Write-InfoMsg "Installing $packageSpec..."
        & $PythonCommand -m pip install $packageSpec --quiet
    }
    Write-Success "Core packages installed"
}

# Step 8: Post-Installation Tasks
Write-Header "Step 8: Post-Installation Tasks"

# Run asciidoc3 post-install if available
if (Test-CommandExists "asciidoc3_postinstall") {
    Write-InfoMsg "Running asciidoc3 post-install..."
    asciidoc3_postinstall 2>&1 | Out-Null
    Write-Success "asciidoc3 configured"
}
else {
    Write-WarningMsg "asciidoc3_postinstall not found in PATH (may require shell restart)"
}

# Step 9: Validation
Write-Header "Step 9: Validating Installation"

# Validate Python packages
Write-InfoMsg "Checking installed packages..."
foreach ($package in $REQUIRED_PACKAGES) {
    $packageName = $package.Name
    $checkImport = $packageName -replace '-', '_'

    $importTest = & $PythonCommand -c "import $checkImport" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $versionOutput = & $PythonCommand -m pip show $packageName 2>&1 | Select-String "Version:"
        if ($versionOutput) {
            $version = ($versionOutput -split ":\s*")[1].Trim()
            Write-Success "$packageName $version"
        }
        else {
            Write-Success "$packageName installed"
        }
    }
    else {
        Write-ErrorMsg "$packageName not found or cannot be imported"
    }
}

# Validate system commands
Write-InfoMsg "Checking system commands..."
$commands = @(
    @{ Name = $PythonCommand; Required = $true }
    @{ Name = "pip"; Required = $true }
    @{ Name = "pandoc"; Required = $false }
    @{ Name = "git"; Required = $false }
)

foreach ($cmd in $commands) {
    if (Test-CommandExists $cmd.Name) {
        $location = (Get-Command $cmd.Name).Source
        Write-Success "$($cmd.Name): $location"
    }
    else {
        if ($cmd.Required) {
            Write-ErrorMsg "$($cmd.Name): not found (required)"
        }
        else {
            Write-WarningMsg "$($cmd.Name): not found (optional)"
        }
    }
}

# Test application import
Write-InfoMsg "Testing application import..."
$importTest = & $PythonCommand -c "from asciidoc_artisan.ui.main_window import AsciiDocEditor" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Application modules can be imported"
}
else {
    Write-WarningMsg "Application modules not yet installed (run: pip install -e .)"
}

# Step 10: Summary
Write-Header "Installation Summary"

$pythonVersionFull = & $PythonCommand --version
$pythonLocation = (Get-Command $PythonCommand).Source
$pipVersionFull = & $PythonCommand -m pip --version

Write-Host "Python Version:    $pythonVersionFull"
Write-Host "Python Location:   $pythonLocation"
Write-Host "Pip Version:       $($pipVersionFull -replace ' from.*', '')"
Write-Host ""
Write-Host "Errors:            $($script:Errors)"
Write-Host "Warnings:          $($script:Warnings)"
Write-Host ""

if ($script:Errors -eq 0) {
    Write-Success "Installation completed successfully!"
    Write-Host "`nNext steps:"
    Write-Host "  1. Launch the application:"
    Write-Host "     .\launch-asciidoc-artisan-gui.bat"
    Write-Host "  2. Or run directly:"
    Write-Host "     $PythonCommand src\main.py"
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
}
else {
    Write-ErrorMsg "Installation completed with $($script:Errors) errors"
    Write-Host "`nPlease resolve the errors above and try again."
    exit 1
}
