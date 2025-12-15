<#
Context:
Windows launcher for the tweet-to-thermal-printer app.

Responsibilities:
- Launch the app from any working directory.
- Prefer launching in Windows Terminal fullscreen when available.
#>

param(
    [switch]$NoFullscreen
)

$scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
$scriptDir = Split-Path -Parent $scriptPath
$repoRoot = Split-Path -Parent $scriptDir
$mainPath = Join-Path -Path $repoRoot -ChildPath 'src\main.py'

if (-not (Test-Path -LiteralPath $mainPath)) {
    Write-Error "Cannot find main.py at: $mainPath. repoRoot='$repoRoot' scriptPath='$scriptPath'"
    exit 1
}

if (-not $NoFullscreen) {
    $wt = Get-Command wt -ErrorAction SilentlyContinue
    if ($null -ne $wt) {
        $args = @(
            '-F',
            'pwsh',
            '-NoExit',
            '-File',
            "`"$scriptPath`"",
            '-NoFullscreen'
        )
        Start-Process -FilePath $wt.Source -ArgumentList $args -WorkingDirectory $repoRoot
        exit 0
    }
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $py) {
    & $py.Source -3 $mainPath
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    Write-Error "Neither 'py' nor 'python' was found on PATH. Install Python or add it to PATH."
    exit 1
}

& $python.Source $mainPath
exit $LASTEXITCODE
