<#
.SYNOPSIS
    AsciiDoc Artisan - Full Clean Installation Script for Windows 11

.DESCRIPTION
    This script performs a complete installation of AsciiDoc Artisan with all
    dependencies and validates the installation. Requires PowerShell 7.0+.

.PARAMETER PythonCommand
    Python command to use (default: 'python')

.PARAMETER SkipVirtualEnv
    Skip virtual environment creation

.EXAMPLE
    .\Install-AsciiDocArtisan.ps1

.EXAMPLE
    .\Install-AsciiDocArtisan.ps1 -PythonCommand python3

.NOTES
    Author:      AsciiDoc Artisan Team
    Requires:    PowerShell 7.0+, Python 3.11+
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$PythonCommand = "python",

    [Parameter(Mandatory = $false)]
    [switch]$SkipVirtualEnv
)

# Configuration
$PYTHON_MIN_VERSION = "3.11"
$REQUIRED_PACKAGES = @(
    @{ Name = "PySide6";   VersionSpec = ">=6.9.0" }
    @{ Name = "asciidoc3"; VersionSpec = ">=10.2.1" }
    @{ Name = "pypandoc";  VersionSpec = ">=1.13" }
)

# Track validation
$script:Errors = 0
$script:Warnings = 0

# Helper Functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $script:Errors++
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
    $script:Warnings++
}

function Write-InfoMsg {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
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

function Test-CommandExists {
    param([string]$CommandName)
    $commandInfo = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($commandInfo) {
        # Check for Microsoft Store stub
        if (($CommandName -eq 'python' -or $CommandName -eq 'python3') -and
            ($commandInfo.Source -like "*Microsoft\WindowsApps*")) {
            return $false
        }
        return $true
    }
    return $false
}

# Main Installation Process

# Step 1: Check PowerShell Version
Write-Header "Step 1: Checking PowerShell Version"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-ErrorMsg "This script requires PowerShell 7.0 or higher"
    Write-Host "`nCurrent version: $($PSVersionTable.PSVersion)" -ForegroundColor Red
    Write-Host "Download PowerShell 7: https://github.com/PowerShell/PowerShell/releases" -ForegroundColor Yellow
    exit 1
}

Write-Success "PowerShell $($PSVersionTable.PSVersion) detected"

# Step 2: Check Windows Version
Write-Header "Step 2: Checking Windows Version"

$osInfo = Get-CimInstance Win32_OperatingSystem
$osVersion = $osInfo.Caption
Write-Success "$osVersion detected"

if ($osInfo.BuildNumber -lt 22000) {
    Write-WarningMsg "Windows 11 recommended (Build 22000+), detected Build $($osInfo.BuildNumber)"
}

# Step 3: Check Python Installation
Write-Header "Step 3: Checking Python Installation"

$pythonFound = $false
$pythonExecutable = ""
$pythonVersion = ""

# Try the specified Python command first
if (Test-CommandExists $PythonCommand) {
    try {
        $versionOutput = & $PythonCommand --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            $pythonVersion = $matches[1]
            $pythonMajorMinor = $pythonVersion.Substring(0, $pythonVersion.LastIndexOf('.'))

            if (Compare-Version $pythonMajorMinor $PYTHON_MIN_VERSION) {
                $pythonExecutable = (Get-Command $PythonCommand).Source
                $pythonFound = $true
                Write-Success "Found Python $pythonVersion at $pythonExecutable"
            }
            else {
                Write-WarningMsg "Python $pythonVersion is too old (need >= $PYTHON_MIN_VERSION)"
            }
        }
    }
    catch {
        Write-WarningMsg "Could not determine Python version for '$PythonCommand'"
    }
}

# Try alternative Python commands
if (-not $pythonFound) {
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
                        $PythonCommand = $cmd
                        $pythonFound = $true
                        Write-Success "Found Python $pythonVersion at $pythonExecutable"
                        break
                    }
                }
            }
            catch {
                continue
            }
        }
    }
}

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
