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

$repoRootCandidates = @(
    (Split-Path -Parent $scriptDir),
    (Join-Path $env:USERPROFILE 'Documents\GitHub\AFD-Thermonuklear'),
    (Join-Path $env:USERPROFILE 'OneDrive\Documents\GitHub\AFD-Thermonuklear'),
    (Join-Path $env:USERPROFILE 'Documents\AFD-Thermonuklear'),
    (Join-Path $env:USERPROFILE 'OneDrive\Documents\AFD-Thermonuklear')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$repoRoot = $null
foreach ($candidate in $repoRootCandidates) {
    $candidateMain = Join-Path -Path $candidate -ChildPath 'src\main.py'
    if (Test-Path -LiteralPath $candidateMain) {
        $repoRoot = $candidate
        break
    }
}

$mainPath = if ($repoRoot) { Join-Path -Path $repoRoot -ChildPath 'src\main.py' } else { $null }

if (-not $mainPath -or -not (Test-Path -LiteralPath $mainPath)) {
    Write-Error "Cannot find main.py. repoRoot='$repoRoot' scriptPath='$scriptPath'"
    exit 1
}

if (-not $NoFullscreen) {
    $wt = Get-Command wt -ErrorAction SilentlyContinue
    if ($null -ne $wt) {
        $shell = if (Get-Command pwsh -ErrorAction SilentlyContinue) { 'pwsh' } else { 'powershell' }
        $args = @(
            '-F',
            $shell,
            '-NoExit',
            '-File',
            "`"$scriptPath`"",
            '-NoFullscreen'
        )
        Start-Process -FilePath $wt.Source -ArgumentList $args -WorkingDirectory $repoRoot
        exit 0
    }
}

$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uv) {
    $uvCandidates = @(
        (Join-Path $env:USERPROFILE '.cargo\bin\uv.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\uv\uv.exe')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

    if ($uvCandidates.Count -gt 0) {
        $uvExe = $uvCandidates[0]
    } else {
        Write-Error "'uv' was not found on PATH (and not found in common install locations). Install uv and try again."
        Write-Error "Install (PowerShell): irm https://astral.sh/uv/install.ps1 | iex"
        exit 1
    }
} else {
    $uvExe = $uv.Source
}

Push-Location $repoRoot
try {
    $lockPath = Join-Path -Path $repoRoot -ChildPath 'uv.lock'
    if (Test-Path -LiteralPath $lockPath) {
        & $uvExe sync --frozen
    } else {
        & $uvExe sync
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & $uvExe run python $mainPath
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
