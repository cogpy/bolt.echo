# Start the Time Crystal Daemon (Windows)
param(
    [int]$Port = 8377,
    [switch]$SelfTest
)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$daemon = Join-Path $here "..\daemon\time_crystal_daemon.py"
if ($SelfTest) {
    python $daemon --selftest
} else {
    python $daemon --port $Port
}
