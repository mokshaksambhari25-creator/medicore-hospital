#!/bin/zsh
cd "$(dirname "$0")"
/bin/zsh ./ensure_mysql.sh
open "mysql://medicore:MediCore24@127.0.0.1:3306/medicore" 2>/dev/null || true
for app in "Sequel Ace" "Sequel Pro" "TablePlus" "MySQLWorkbench" "DBeaver"; do
  if [ -d "/Applications/${app}.app" ]; then
    open -a "$app"
    break
  fi
done
open "../BACKUP"
echo
echo "Connect in any MySQL app on this Mac:"
echo "  Host:     127.0.0.1"
echo "  Port:     3306"
echo "  User:     medicore"
echo "  Password: MediCore24"
echo "  Database: medicore"
echo
echo "Or double-click  BACKUP/medicore.sql"
echo
read -k 1 "?Press any key to close this window…"
echo
