#!/bin/zsh
cd "$(dirname "$0")"
echo
echo "Opening MediCore database…"
echo
/usr/bin/env python3 control.py database
echo
echo "----------------------------------------------"
echo "MySQL:  medicore @ 127.0.0.1"
echo "User:   medicore     Password: MediCore24"
echo "Dump:   ../BACKUP/medicore.sql"
echo "A table view just opened in Brave."
echo "----------------------------------------------"
echo
read -k 1 "?Press any key to close this window…"
echo
