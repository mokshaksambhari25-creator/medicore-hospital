#!/bin/zsh
cd "$(dirname "$0")"
echo
echo "Stopping MediCore…"
echo
/usr/bin/env python3 control.py stop
echo
read -k 1 "?Press any key to close this window…"
echo
