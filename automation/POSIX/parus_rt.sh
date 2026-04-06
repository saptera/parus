#!/usr/bin/env bash
set -euo pipefail

# Title and banner
echo -e "\033]0;PARUS Real-Time System\007"
cat << "EOF"
  __| |__________________________| |__
 (__   __________________________   __)
    | |                          | |
    | |  PARUS Real-Time System  | |
  __| |__________________________| |__
 (__   __________________________   __)
    | |                          | |

EOF


# Resolve path
scp_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pkg_dir="$(cd "$scp_dir/../.." && pwd)"


# Select Python interpreter
if [ -x "$pkg_dir/venv/bin/python3" ]; then
  py_itpr="$pkg_dir/venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  py_itpr="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  py_itpr="$(command -v python)"
else
  echo "Error: Python not installed or not in PATH"
  read -r -n 1 -s -p "Press any key to exit..."
  echo
  exit 1
fi


# Launch application
echo "Starting PARUS Real-Time System..."
echo
echo "Python command line outputs"
echo "----------------------------------------"

cd "$pkg_dir" || exit 1
gui_scp="$pkg_dir/parus/app/pac_rt.py"
"$py_itpr" "$gui_scp"

echo "----------------------------------------"
echo
echo "System GUI has stopped"
read -n 1 -s -r -p "Press any key to exit..."
echo
