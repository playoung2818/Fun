# starter.ps1
# Windows launcher for the Hakuna Matata animation + audio.
# - Starts audio (ffplay if available; else play_audio.py)
# - Runs animate.py (curses) ATTACHED to this console (visible)
# - Stops audio when the animation exits or on error

param(
    [int]$Seconds = 0,           # forward to animate.py as --seconds
    [switch]$NoSound,            # disable audio
    [string]$Python = "python"   # path to Python (or just "python" if in PATH)
)

$ErrorActionPreference = "Stop"

function Info($msg)  { Write-Host "[info]  $msg" }
function Warn($msg)  { Write-Host "[warn]  $msg" -ForegroundColor Yellow }
function ErrorMsg($m){ Write-Host "[error] $m" -ForegroundColor Red }

# Resolve repo-relative paths
$Repo     = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Repo
$mp3      = Join-Path $Repo "assets\Hakuna_matata.mp3"
$anim     = Join-Path $Repo "animate.py"
$fallback = Join-Path $Repo "play_audio.py"

if (-not (Test-Path $anim)) {
    ErrorMsg "animate.py not found at: $anim"
    exit 1
}

# Build arguments for animate.py
$animArgs = @($anim)
if ($Seconds -gt 0) { $animArgs += @("--seconds", $Seconds.ToString()) }

# --- Start audio (capture process so we can kill it later) ---
$pAudio = $null
if (-not $NoSound) {
    if (Test-Path $mp3) {
        $ffplayExists = $false
        try { Get-Command ffplay -ErrorAction Stop | Out-Null; $ffplayExists = $true } catch { $ffplayExists = $false }

        if ($ffplayExists) {
            Info "Starting audio with ffplay"
            $pAudio = Start-Process -WindowStyle Hidden -FilePath "ffplay" `
                -ArgumentList @("-nodisp","-autoexit","-loglevel","quiet",$mp3) `
                -PassThru
        } elseif (Test-Path $fallback) {
            Info "Starting audio with Python fallback: $fallback"
            $pAudio = Start-Process -WindowStyle Hidden -FilePath $Python `
                -ArgumentList @($fallback, $mp3) `
                -PassThru
        } else {
            Warn "No audio backend (ffplay) and no fallback script found. Continuing without sound."
        }
    } else {
        Info "No MP3 found at $mp3 - animation only."
    }
} else {
    Info "Audio disabled via -NoSound."
}

# --- Run animation ATTACHED to this window (VISIBLE) ---
try {
    $pyPath = (Get-Command $Python -ErrorAction Stop).Source
    Info ("Using Python at: {0}" -f $pyPath)
    Info ("Launching animation (attached): {0} {1}" -f $Python, ($animArgs -join ' '))
    & $Python @animArgs          # <- call operator: runs in this console
    $exitCode = $LASTEXITCODE
}
catch {
    ErrorMsg ("Launch failed: {0}" -f $_.Exception.Message)
    $exitCode = 1
}
finally {
    # --- After animation exits (or on error), stop audio if it's still playing ---
    if ($pAudio -and -not $pAudio.HasExited) {
        Info "Stopping audio..."
        try { Stop-Process -Id $pAudio.Id -Force } catch {}
    }
}

Info "Done."
exit $exitCode

