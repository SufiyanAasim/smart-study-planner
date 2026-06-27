$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error 'Python launcher (py) was not found.'
    exit 1
}
& py -m pip install --upgrade pyinstaller
& py -m PyInstaller --onefile --noconsole --name "SmartStudyPlanner" --icon "assets/icon.ico" --add-data "assets;assets" --distpath . --workpath .build --specpath . "main.py"
Write-Host 'Executable build complete. Look for SmartStudyPlanner.exe in the project folder.'

