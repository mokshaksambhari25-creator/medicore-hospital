#!/bin/zsh
cd "$(dirname "$0")"
echo
echo "Starting MediCore website and opening the database…"
echo
/usr/bin/env python3 control.py start-all
echo
echo "----------------------------------------------"
echo "Website:   http://127.0.0.1:5000"
echo "Staff ID:  DOC-1001     Password: 123456"
echo
echo "You can close this window. The server keeps running."
echo "To stop it, double-click  STOP SERVER.command"
echo "----------------------------------------------"
echo
read -k 1 "?Press any key to close this window…"
echo
