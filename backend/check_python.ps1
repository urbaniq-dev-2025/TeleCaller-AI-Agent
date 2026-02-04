# PowerShell script to check Python installation and help with setup

Write-Host "=== Python Installation Checker ===" -ForegroundColor Cyan
Write-Host ""

# Check for Python
Write-Host "Checking for Python..." -ForegroundColor Yellow

$pythonFound = $false
$pythonVersion = $null
$pythonPath = $null

# Try different Python commands
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -match "Python") {
            $pythonFound = $true
            $pythonVersion = $result
            $pythonPath = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
            Write-Host "✓ Found Python!" -ForegroundColor Green
            Write-Host "  Command: $cmd" -ForegroundColor White
            Write-Host "  Version: $pythonVersion" -ForegroundColor White
            Write-Host "  Path: $pythonPath" -ForegroundColor White
            break
        }
    } catch {
        # Continue checking
    }
}

if (-not $pythonFound) {
    Write-Host "✗ Python NOT FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python needs to be installed. Here's how:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPTION 1: Download from Python.org (Recommended)" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. Click 'Download Python' button" -ForegroundColor White
    Write-Host "  3. Run the installer" -ForegroundColor White
    Write-Host "  4. IMPORTANT: Check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "  5. Click 'Install Now'" -ForegroundColor White
    Write-Host "  6. Restart this terminal after installation" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPTION 2: Install from Microsoft Store" -ForegroundColor Cyan
    Write-Host "  1. Open Microsoft Store" -ForegroundColor White
    Write-Host "  2. Search for 'Python 3.12'" -ForegroundColor White
    Write-Host "  3. Click Install" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, close and reopen this terminal, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    
    # Offer to open download page
    $response = Read-Host "Would you like to open the Python download page? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process "https://www.python.org/downloads/"
        Write-Host "Download page opened in your browser." -ForegroundColor Green
    }
    
    exit 1
}

# Check pip
Write-Host ""
Write-Host "Checking pip (package manager)..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pip is available" -ForegroundColor Green
        Write-Host "  $pipVersion" -ForegroundColor White
    } else {
        Write-Host "⚠ pip check failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not check pip" -ForegroundColor Yellow
}

# Check Python version compatibility
Write-Host ""
Write-Host "Checking Python version compatibility..." -ForegroundColor Yellow
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -eq 3 -and $minor -ge 10) {
        Write-Host "✓ Python version is compatible (3.10+ required)" -ForegroundColor Green
    } else {
        Write-Host "⚠ Python version may be too old (3.10+ required)" -ForegroundColor Yellow
        Write-Host "  Current: $pythonVersion" -ForegroundColor White
        Write-Host "  Required: Python 3.10 or higher" -ForegroundColor White
    }
}

# Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
if ($pythonFound) {
    Write-Host "✓ Python is installed and ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Navigate to backend folder:" -ForegroundColor White
    Write-Host "   cd `"C:\Users\dev\AI-telecaller Agent\TeleCaller-AI-Agent\backend`"" -ForegroundColor Gray
    Write-Host "2. Create virtual environment:" -ForegroundColor White
    Write-Host "   python -m venv venv" -ForegroundColor Gray
    Write-Host "3. Activate it:" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "4. Install dependencies:" -ForegroundColor White
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
} else {
    Write-Host "✗ Python needs to be installed" -ForegroundColor Red
    Write-Host "  See instructions above" -ForegroundColor Yellow
}

Write-Host ""
