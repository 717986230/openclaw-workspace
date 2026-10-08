# tmux wrapper for Windows - calls WSL tmux
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$wslArgs = @("-d", "Ubuntu", "-e", "tmux") + $Args
$process = Start-Process -FilePath "wsl" -ArgumentList $wslArgs -NoNewWindow -Wait -PassThru
exit $process.ExitCode