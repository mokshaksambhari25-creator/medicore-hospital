#!/bin/zsh
# Opens the hospital site. The server starts by itself at login.
open -a "Brave Browser" "http://127.0.0.1:5000" 2>/dev/null \
  || open "http://127.0.0.1:5000"
