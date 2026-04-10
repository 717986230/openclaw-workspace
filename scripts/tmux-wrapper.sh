#!/bin/bash
# Wrapper to call tmux via WSL from Windows
exec wsl -d Ubuntu -e tmux "$@"