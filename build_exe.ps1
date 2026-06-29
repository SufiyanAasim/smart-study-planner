$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error 'Python launcher (py) was not found.'
    exit 1
}
& py -m pip install --upgrade pyinstaller
& py -m PyInstaller "SmartStudyPlanner.spec" --distpath . --workpath .build
Write-Host 'Executable build complete. Look for SmartStudyPlanner.exe in the project folder.'

