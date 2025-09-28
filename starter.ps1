# starter.ps1
# Windows launcher for Hakuna MATTata prank
# Plays the MP3 (if available) and runs the animation.

$Repo   = Split-Path -Parent $MyInvocation.MyCommand.Path
$mp3    = Join-Path $Repo "assets\Hakuna_matata.mp3"
$anim   = Join-Path $Repo "animate.py"
$fallback = Join-Path $Repo "play_audio.py"

# --- Play audio ---
if (Test-Path $mp3) {
    if (Get-Command ffplay -ErrorAction SilentlyContinue) {
        # ffplay from ffmpeg
        Start-Process -WindowStyle Hidden -FilePath "ffplay" -ArgumentList "-nodisp -autoexit `"$mp3`"" -ErrorAction SilentlyContinue
    } elseif (Test-Path $fallback) {
        # Python fallback
        Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList "`"$fallback`" `"$mp3`"" -ErrorAction SilentlyContinue
    } else {
        Write-Host "[warn] No audio backend found. Continuing without sound."
    }
} else {
    Write-Host ("[info] No MP3 found at {0} - animation only." -f $mp3)
}

# --- Run animation ---
# Pass through --seconds 8 for a quick test (remove for full run)
$seconds = $null
#$seconds = 8   # uncomment this line for short auto-exit test

$argList = @()
if ($seconds) { $argList += @("--seconds", "$seconds") }

python $anim @argList
