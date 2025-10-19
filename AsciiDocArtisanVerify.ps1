<#
.SYNOPSIS
    Validates the environment for the AsciiDoc Artisan application (adp.py).
    Checks for Python, pip, required packages, PATH configuration (Python, Pandoc, Git, AsciiDoc3),
    and runs post-install helpers. Attempts to install/upgrade Python packages and
    optionally adds Python Scripts to User PATH.

.DESCRIPTION
    This script performs a comprehensive check of the environment required to run
    the associated adp.py AsciiDoc Artisan application. It verifies:
    1. PowerShell Version: Ensures PowerShell 7.0 or higher is being used.
    2. Python Installation: Checks if Python is installed, accessible via the configured
       command (default: 'python'), and critically, ensures it's not the problematic
       Microsoft Store stub version. Verifies the Python version can be retrieved.
    3. Pip Availability: Confirms that 'pip', the Python package installer, is functional.
    4. Required Python Packages: Checks, installs, or upgrades necessary Python packages
       (PySide6, asciidoc3, pypandoc). Runs 'asciidoc3_postinstall' if needed.
    5. Command Availability in PATH: Verifies that essential commands ('python', 'pip',
       'pandoc', 'asciidoc3', 'git') can be resolved through the system's PATH.
    6. Python User Scripts Path: If 'asciidoc3' command isn't found directly, checks
       if the Python user scripts directory needs to be added to the PATH and prompts
       the user if necessary.

.PARAMETER PythonCommand
    Specifies the command used to invoke the Python interpreter. Defaults to 'python'.
    Other common values might be 'python3' or 'py'.

.NOTES
    Author:      Gemini (Revised by Richard Webb) # <<< UPDATED
    Date:        2025-04-19
    Requires:    PowerShell 7.0+
    Python Compatibility: PySide6 6.9+ generally works well with Python 3.11/3.12.
    Git Requirement: The AsciiDoc Artisan app requires 'git' to be installed and in the
                 PATH for its Git integration features (Commit, Pull, Push). This
                 script checks for 'git' but does not install it. Download from:
                 https://git-scm.com/downloads
    Execution:   Run this script in the environment where you intend to execute adp.py.
    PATH Changes: Modifying the User PATH requires user confirmation. A PowerShell
                 session restart (or system restart) is necessary for PATH changes
                 to take full effect.
    Dependencies: Assumes Python/pip are installed. Relies on internet access for PyPI.
                 Assumes Pandoc and Git are installed separately if needed.

.EXAMPLE
    .\AsciiDocArtisanVerify.ps1
    Runs the script with default settings, checking for the 'python' command.

.EXAMPLE
    .\AsciiDocArtisanVerify.ps1 -PythonCommand py
    Runs the script, specifically looking for the 'py' command (Python Launcher).
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "Command used to invoke Python (e.g., python, python3, py)")]
    [string]$PythonCommand = "python"
)

# --- Configuration ---
Write-Verbose "Defining required Python packages..."
$RequiredPythonPackages = @(
    @{ Name = "PySide6";         VersionSpec = ">=6.9.0" } # Core Qt bindings
    # @{ Name = "PySide6-WebEngine"; VersionSpec = "" } # Not needed for QTextBrowser preview
    @{ Name = "asciidoc3";       VersionSpec = "" }      # For AsciiDoc rendering
    @{ Name = "pypandoc";        VersionSpec = "" }      # For DOCX/Clipboard conversion
)

# --- Helper Functions ---

Function Test-CommandExists { # (Unchanged)
    [CmdletBinding()] param([Parameter(Mandatory = $true)][string]$CommandName)
    Write-Verbose "Entering Test-CommandExists for '$CommandName'"; Write-Host "Checking for command: '$CommandName'..." -ForegroundColor Cyan
    $commandInfo = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($commandInfo) {
        if (($CommandName -eq 'python' -or $CommandName -eq 'python3') -and ($commandInfo.Source -like "*Microsoft\WindowsApps*")) { Write-Host " -> Found '$CommandName' but it points to the MS Store stub ($($commandInfo.Source)). This is NOT a valid installation for scripting." -ForegroundColor Yellow; return $false }
        Write-Host " -> Found: $($commandInfo.Source)" -ForegroundColor Green; return $true
    } else { Write-Host " -> '$CommandName' not found in PATH." -ForegroundColor Yellow; return $false }
}

Function Test-PythonPackage { # (Unchanged)
    [CmdletBinding()] param([Parameter(Mandatory = $true)][string]$PackageName)
    Write-Verbose "Entering Test-PythonPackage for '$PackageName'"; Write-Host "Checking Python package: '$PackageName'..." -ForegroundColor Cyan
    $pipOutput = ""; try {
        $pipArgs = "-m", "pip", "show", $PackageName, "--disable-pip-version-check"; Write-Verbose "Running: $PythonCommand $($pipArgs -join ' ')"
        $pipOutput = & $PythonCommand $pipArgs *>&1
        if ($LASTEXITCODE -eq 0 -and $pipOutput -notmatch "WARNING: Package\(s\) not found") {
            $versionLine = $pipOutput | Select-String -Pattern "^Version:"; $version = if ($versionLine) { ($versionLine -split ":\s*", 2)[1].Trim() } else { "Unknown" }
            Write-Host " -> Found: $PackageName (Version: $version)" -ForegroundColor Green; return $true
        } else { Write-Host " -> Package '$PackageName' not found (or 'pip show' failed)." -ForegroundColor Yellow; Write-Verbose "Pip Show Output for '$PackageName': $($pipOutput -join [Environment]::NewLine)"; return $false }
    } catch { Write-Host " -> Error checking package '$PackageName'. Python/pip might have issues." -ForegroundColor Red; Write-Error ("Failed to execute '$PythonCommand -m pip show $PackageName'. Error: $($_.Exception.Message)"); Write-Verbose "Pip Show Error details: $_"; return $false }
}

Function Install-PythonPackage { # (Unchanged)
    [CmdletBinding()] param([Parameter(Mandatory = $true)][string]$PackageName, [Parameter(Mandatory = $false)][string]$VersionSpec = "")
    Write-Verbose "Entering Install-PythonPackage for '$PackageName' (VersionSpec: '$VersionSpec')"
    $packageNameWithVersion = $PackageName; $logMessage = "Attempting to install/upgrade '$PackageName'"
    if (-not [string]::IsNullOrEmpty($VersionSpec)) { $packageNameWithVersion = "$($PackageName)$($VersionSpec)"; $logMessage += " with version spec '$VersionSpec'" }
    $logMessage += "..."; Write-Host $logMessage -ForegroundColor Cyan
    $pipArgs = @("install", "--upgrade", "--no-input", "--disable-pip-version-check", "--prefer-binary", $packageNameWithVersion)
    try {
        $fullArgumentList = @("-m", "pip") + $pipArgs; Write-Host "Running: $PythonCommand $($fullArgumentList -join ' ')" -ForegroundColor Gray
        $process = Start-Process -FilePath $PythonCommand -ArgumentList $fullArgumentList -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -eq 0) { Write-Host " -> Successfully installed/upgraded '$PackageName'." -ForegroundColor Green; return $true }
        else { Write-Host " -> Failed to install/upgrade '$PackageName'. Pip process exited with code: $($process.ExitCode)." -ForegroundColor Red; Write-Host " -> Potential issues: Network problems, package conflicts, missing dependencies, or permissions." -ForegroundColor Red; Write-Host " -> Try running the command manually for detailed output:" -ForegroundColor Red; Write-Host "    $PythonCommand $($fullArgumentList -join ' ')" -ForegroundColor Red; return $false }
    } catch { Write-Host " -> Error executing the pip command process for '$PackageName'." -ForegroundColor Red; Write-Error ("Failed to start '$PythonCommand $($fullArgumentList -join ' ')'. Error: $($_.Exception.Message)"); Write-Verbose "Start-Process Error details: $_"; return $false }
}

Function Add-UserPath { # (Unchanged)
    [CmdletBinding()] param([Parameter(Mandatory = $true)][string]$DirectoryToAdd)
    Write-Verbose "Entering Add-UserPath for '$DirectoryToAdd'"; Write-Host "Attempting to add '$DirectoryToAdd' to the User PATH." -ForegroundColor Cyan
    if (-not (Test-Path -Path $DirectoryToAdd -PathType Container)) { Write-Warning "The directory '$DirectoryToAdd' does not exist. Cannot add it to PATH."; return $false }
    try {
        $currentUserPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $pathSeparator = [IO.Path]::PathSeparator
        $pathEntries = $currentUserPath -split $pathSeparator | Where-Object { -not [string]::IsNullOrEmpty($_) }
        $foundInPath = $false; foreach ($entry in $pathEntries) { if ($entry -eq $DirectoryToAdd) { $foundInPath = $true; break } }
        if ($foundInPath) { Write-Host " -> Directory '$DirectoryToAdd' is already in the User PATH." -ForegroundColor Green; return $true }
        $confirmation = Read-Host "Add '$DirectoryToAdd' to your User PATH environment variable? (Requires shell restart to take effect everywhere) [y/N]"
        if ($confirmation -ne 'y') { Write-Host " -> PATH modification skipped by user." -ForegroundColor Yellow; return $false }
        $newPath = $currentUserPath; if ($currentUserPath -and (-not $currentUserPath.EndsWith($pathSeparator))) { $newPath += $pathSeparator }; $newPath += $DirectoryToAdd
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        $env:Path = $newPath + $pathSeparator + [Environment]::GetEnvironmentVariable('Path', 'Machine') + $pathSeparator + $env:Path
        Write-Verbose "Current session PATH updated to: $env:Path"
        Write-Host " -> Successfully added '$DirectoryToAdd' to User PATH." -ForegroundColor Green
        Write-Host " -> IMPORTANT: Please RESTART your PowerShell session (or computer) for the change to take full effect in new terminals and applications." -ForegroundColor Magenta
        return $true
    } catch { Write-Host " -> Failed to modify User PATH. Error: $($_.Exception.Message)" -ForegroundColor Red; Write-Error ("Failed to set User PATH environment variable. Error: $($_.Exception.Message)"); Write-Host " -> You may need to add '$DirectoryToAdd' manually via System Properties -> Environment Variables." -ForegroundColor Red; Write-Verbose "Add-UserPath Error details: $_"; return $false }
}


# --- Main Script Logic ---

Write-Host "`nStarting Environment Validation for AsciiDoc Artisan..." -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "Using Python command: '$PythonCommand'" -ForegroundColor Gray
$validationOverallStatus = $true

# Step 1: Check PowerShell Version
Write-Host "`nStep 1: Checking PowerShell Version..." -ForegroundColor White
if ($PSVersionTable.PSVersion.Major -lt 7) { Write-Error "This script requires PowerShell 7+. Aborting."; Exit 1 }
Write-Host " -> PowerShell version $($PSVersionTable.PSVersion) is compatible." -ForegroundColor Green

# Step 2: Check Python Installation
Write-Host "`nStep 2: Checking Python Installation..." -ForegroundColor White
if (-not (Test-CommandExists $PythonCommand)) { Write-Error "Python command '$PythonCommand' not found or is invalid MS Store stub. Install Python correctly and add to PATH. Aborting."; Exit 1 }
try {
    Write-Host " -> Checking Python version execution..." -ForegroundColor Cyan; $pythonVersionArgs = "--version"; Write-Verbose "Running: $PythonCommand $pythonVersionArgs"
    $pythonVersionOutput = & $PythonCommand $pythonVersionArgs 2>&1; if ($LASTEXITCODE -ne 0) { throw "Command '$PythonCommand --version' failed." }; if ($pythonVersionOutput -notmatch "Python \d+\.\d+") { throw "Unexpected version output."}
    Write-Host " -> Python Version Check Output: $($pythonVersionOutput -join ' ')" -ForegroundColor Green
} catch { Write-Error "Failed to get Python version using '$PythonCommand --version'. Check installation/PATH. Error: $($_.Exception.Message) Aborting."; Exit 1 }

# Step 3: Check Pip Availability
Write-Host "`nStep 3: Checking Pip Availability..." -ForegroundColor White
try {
    $pipVersionArgs = @("-m", "pip", "--version", "--disable-pip-version-check"); Write-Verbose "Running: $PythonCommand $($pipVersionArgs -join ' ')"
    $process = Start-Process -FilePath $PythonCommand -ArgumentList $pipVersionArgs -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) { throw "Command '$PythonCommand -m pip --version' failed with exit code $($process.ExitCode)." }
    Write-Host " -> Pip found and accessible via '$PythonCommand -m pip'." -ForegroundColor Green
} catch { $errorMessage = "Failed to run '$PythonCommand -m pip --version'. Pip might not be installed correctly."; if ($_.Exception.Message) { $errorMessage += " Error: $($_.Exception.Message)" }; Write-Error $errorMessage; Exit 1 }

# Step 4: Check and Install/Upgrade Python Packages
Write-Host "`nStep 4: Checking Required Python Packages..." -ForegroundColor White
$allPackagesOk = $true
foreach ($packageInfo in $RequiredPythonPackages) {
    if (-not $packageInfo) { continue }
    $packageName = $packageInfo.Name; $versionSpec = $packageInfo.VersionSpec; $installOrUpgradeSucceeded = $false
    if (-not (Test-PythonPackage -PackageName $packageName)) {
        Write-Host " -> '$packageName' not found, attempting installation..." -ForegroundColor Cyan
        if (Install-PythonPackage -PackageName $packageName -VersionSpec $versionSpec) { $installOrUpgradeSucceeded = $true }
        else { $allPackagesOk = $false; $validationOverallStatus = $false; Write-Host " -> CRITICAL: Halting dependency check due to REQUIRED installation failure for '$packageName'." -ForegroundColor Red; break }
    } else {
        Write-Host " -> '$packageName' found, attempting upgrade (if applicable)..." -ForegroundColor Cyan
         if (Install-PythonPackage -PackageName $packageName -VersionSpec $versionSpec) { $installOrUpgradeSucceeded = $true }
         else { Write-Host " -> WARNING: Failed to *upgrade* '$packageName'. Existing version will be used." -ForegroundColor Yellow; $installOrUpgradeSucceeded = $true }
    }
    if ($installOrUpgradeSucceeded -and $packageName -eq "asciidoc3") {
        Write-Host " -> Checking for and running post-install helper 'asciidoc3_postinstall'..." -ForegroundColor Cyan
        $postInstallCmdInfo = Get-Command asciidoc3_postinstall -ErrorAction SilentlyContinue
        if ($postInstallCmdInfo) {
            Write-Host " -> Found 'asciidoc3_postinstall' at $($postInstallCmdInfo.Source). Executing..." -ForegroundColor Gray; try {
                $postInstallProcess = Start-Process -FilePath "asciidoc3_postinstall" -Wait -PassThru -NoNewWindow -ErrorAction Stop
                if ($postInstallProcess.ExitCode -eq 0) { Write-Host " -> Successfully ran asciidoc3_postinstall." -ForegroundColor Green }
                else { Write-Warning "Command 'asciidoc3_postinstall' finished with non-zero exit code: $($postInstallProcess.ExitCode)." }
            } catch { Write-Warning "Failed to execute 'asciidoc3_postinstall'. Error: $($_.Exception.Message)." }
        } else { Write-Warning "'asciidoc3_postinstall' command not found in PATH immediately. Shell restart might be needed (see Step 6)." }
    }
}
if (-not $allPackagesOk) { Write-Error "One or more required Python packages could not be installed. Review errors above. Aborting."; Exit 1 }
Write-Host " -> All required Python packages seem to be installed/processed." -ForegroundColor Green

# --- Step 5: Verify Essential Commands in PATH ---
Write-Host "`nStep 5: Verifying Essential Commands in PATH..." -ForegroundColor White
$pythonInPath = Test-CommandExists $PythonCommand
$pipInPath = Test-CommandExists "pip"
$pandocInPath = Test-CommandExists "pandoc"
$asciidocInPath = Test-CommandExists "asciidoc3"
$gitInPath = Test-CommandExists "git" # Check for Git

# Update overall status based on critical command checks
if (-not $pythonInPath) { $validationOverallStatus = $false }
if (-not $gitInPath) {
    Write-Host " -> Git command ('git') not found. This is REQUIRED for Git features in AsciiDoc Artisan." -ForegroundColor Red
    Write-Host " -> Please install Git from https://git-scm.com/downloads and ensure it's added to your PATH." -ForegroundColor Red
    $validationOverallStatus = $false
}

# --- Step 6: Check and Offer to Fix Python Scripts Path ---
$pythonScriptsPathAdded = $false
if (-not $asciidocInPath) {
    Write-Host "`nStep 6: Checking Python Scripts Path for 'asciidoc3'..." -ForegroundColor White; Write-Host " -> 'asciidoc3' command not found directly in PATH." -ForegroundColor Yellow
    Write-Host " -> Checking if Python's user scripts directory needs to be added to PATH..." -ForegroundColor Cyan
    try {
        $userScriptsArgs = "-m", "site", "--user-scripts"; Write-Verbose "Running: $PythonCommand $($userScriptsArgs -join ' ')"; $userScriptsPath = (& $PythonCommand $userScriptsArgs).Trim()
        if ($LASTEXITCODE -ne 0) { throw "Failed to get user scripts path." }
        if (-not [string]::IsNullOrEmpty($userScriptsPath) -and (Test-Path -Path $userScriptsPath -PathType Container)) {
            Write-Host " -> Python user scripts directory found: '$userScriptsPath'" -ForegroundColor Gray
            $currentMachinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine'); $currentUserPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $pathSeparator = [IO.Path]::PathSeparator
            $allPathEntries = ($currentMachinePath -split $pathSeparator) + ($currentUserPath -split $pathSeparator) | Where-Object { $_ }
            $foundInPath = $false; foreach ($entry in $allPathEntries) { if ($entry -eq $userScriptsPath) { $foundInPath = $true; break } }
            if (-not $foundInPath) {
                Write-Host " -> Python user scripts directory ('$userScriptsPath') is NOT currently in your User or System PATH." -ForegroundColor Yellow
                if (Add-UserPath -DirectoryToAdd $userScriptsPath) {
                    $pythonScriptsPathAdded = $true; Write-Host " -> Re-checking for 'asciidoc3' in updated current session PATH..." -ForegroundColor Cyan
                    $asciidocInPath = Test-CommandExists "asciidoc3"; if ($asciidocInPath) { Write-Host " -> 'asciidoc3' found after updating current session PATH." -ForegroundColor Green }
                    else { Write-Host " -> 'asciidoc3' still not found in current session PATH, restart might be needed." -ForegroundColor Yellow }
                    if (-not (Get-Command asciidoc3_postinstall -ErrorAction SilentlyContinue)) { Write-Warning "Post-install script 'asciidoc3_postinstall' also not found after PATH update. Restart required." }
                } else { Write-Host " -> User declined or failed to add scripts directory to PATH." -ForegroundColor Yellow; $validationOverallStatus = $false }
            } else {
                Write-Host " -> Python user scripts directory IS already in your User or System PATH." -ForegroundColor Green
                if (-not $asciidocInPath) { Write-Warning "Scripts path is in PATH, but 'asciidoc3' command still not found. Check installation."; $validationOverallStatus = $false }
            }
        } else { Write-Warning "Could not determine valid Python user scripts directory. Cannot check/add PATH."; $validationOverallStatus = $false }
    } catch { Write-Warning "Error checking/adding Python user scripts path: $($_.Exception.Message)"; $validationOverallStatus = $false }
} else { Write-Host "`nStep 6: Python Scripts Path Check skipped ('asciidoc3' already found)." -ForegroundColor Gray }


# --- Step 7: Final Summary ---
Write-Host "`n----------------------------------------" -ForegroundColor White; Write-Host "Environment Validation Summary:" -ForegroundColor White; Write-Host "----------------------------------------"
Function Get-StatusText { param($status) if($status){"OK"}else{"FAILED/MISSING"} }; Function Get-StatusColor { param($status) if($status){"Green"}else{"Red"} }; Function Get-OptionalStatusColor { param($status) if($status){"Green"}else{"Yellow"} }
Write-Host ("PowerShell Version >= 7.0: " + $(Get-StatusText $true)) -ForegroundColor Green
Write-Host ("Python Command ('" + $PythonCommand + "') Found & Valid: " + $(Get-StatusText $pythonInPath)) -ForegroundColor $(Get-StatusColor $pythonInPath)
Write-Host ("Pip Command ('pip') Found Directly: " + $(Get-StatusText $pipInPath)) -ForegroundColor $(Get-OptionalStatusColor $pipInPath)
$configuredPackagesOk = $true; foreach ($pkgInfo in $RequiredPythonPackages) { if ($pkgInfo -and (-not (Test-PythonPackage -PackageName $pkgInfo.Name))) { if ($allPackagesOk) { $configuredPackagesOk = $false; break } } }; if (-not $allPackagesOk) { $configuredPackagesOk = $false }
Write-Host ("Required Python Packages Installed: " + $(Get-StatusText $configuredPackagesOk)) -ForegroundColor $(Get-StatusColor $configuredPackagesOk)
Write-Host ("Pandoc Command ('pandoc') Found: " + $(Get-StatusText $pandocInPath)) -ForegroundColor $(Get-OptionalStatusColor $pandocInPath)
if (-not $pandocInPath) { Write-Host "   (Note: 'pypandoc' package may download Pandoc binaries if needed.)" -ForegroundColor Gray }
Write-Host ("AsciiDoc3 Command ('asciidoc3') Found: " + $(Get-StatusText $asciidocInPath)) -ForegroundColor $(Get-StatusColor $asciidocInPath)
Write-Host ("Git Command ('git') Found: " + $(Get-StatusText $gitInPath)) -ForegroundColor $(Get-StatusColor $gitInPath)

# Final guidance messages
if (-not $asciidocInPath) {
    if ($pythonScriptsPathAdded) { Write-Host "   -> Python Scripts directory added to User PATH. RESTART PowerShell." -ForegroundColor Magenta; $validationOverallStatus = $false }
    else { Write-Host "   -> 'asciidoc3' not found. Ensure Python Scripts directory is in PATH." -ForegroundColor Yellow; $validationOverallStatus = $false }
}
if (-not $gitInPath) {
     Write-Host "   -> 'git' not found. Install from https://git-scm.com/downloads and add to PATH." -ForegroundColor Red
     # $validationOverallStatus is already false from the check above
}
Write-Host "----------------------------------------"
if ($validationOverallStatus) { Write-Host "Environment Validation Successful!" -ForegroundColor Green; Write-Host "All critical checks passed. The environment appears ready." -ForegroundColor Green }
else { Write-Host "Environment Validation Finished with WARNINGS or ERRORS." -ForegroundColor Yellow; Write-Host "Review messages above. Resolve issues and potentially RESTART PowerShell if PATH was modified." -ForegroundColor Yellow }
Write-Host "`nScript finished."
if ($validationOverallStatus) { Exit 0 } else { Exit 1 }

