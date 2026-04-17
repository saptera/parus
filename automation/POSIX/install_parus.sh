#!/usr/bin/env bash
set -euo pipefail

# Title and banner
printf "\033]0;PARUS Installer\007"
cat << "EOF"
  __| |_____________________________| |__
 (__   _____________________________   __)
    | |                             | |
    | |  PARUS Installation Script  | |
  __| |_____________________________| |__
 (__   _____________________________   __)
    | |                             | |

EOF


# Resolve paths
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


# Call installation script and set execution scripts
echo "Press any key to start..."
echo
read -r -n 1 -s
echo "----------------------------------------"
cd "$pkg_dir" || exit 1
ist_scp="$pkg_dir/automation/environment/install_parus.py"
"$py_itpr" "$ist_scp"

chmod +x "$scp_dir/parus_trn.sh" \
         "$scp_dir/parus_dat.sh" \
         "$scp_dir/parus_rt.sh"
echo "----------------------------------------"
echo


# Desktop shortcuts prompt
choice="Y"
if read -r -t 5 -p "Create shortcuts on desktop (Y/n)? " input; then
  choice="$input"
fi

if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
  echo "Creating desktop launcher scripts"
  # Check desktop path
  desktop_dir="$HOME/Desktop"
  if [ ! -d "$desktop_dir" ]; then
    mkdir -p "$desktop_dir"
  fi

  for app in trn dat rt; do
    case "$app" in
      trn)
        name="PARUS Train"
        script="$scp_dir/parus_trn.sh"
        icon="$pkg_dir/parus/gui/assets/icon_trn.svg"
        ;;
      dat)
        name="PARUS Data"
        script="$scp_dir/parus_dat.sh"
        icon="$pkg_dir/parus/gui/assets/icon_dat.svg"
        ;;
      rt)
        name="PARUS Real-Time"
        script="$scp_dir/parus_rt.sh"
        icon="$pkg_dir/parus/rt/assets/icon_rt.svg"
        ;;
    esac

    # macOS: clickable script
    if [ "$(uname)" = "Darwin" ]; then
      launcher="$desktop_dir/$name.command"
      cat > "$launcher" <<EOF
#!/usr/bin/env bash
cd "$pkg_dir"
bash "$script"
EOF

    # Unix/Linux: desktop entry
    else
      launcher="$desktop_dir/$name.desktop"
      cat > "$launcher" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
Exec="$script"
Icon="$icon"
Terminal=true
EOF

    fi
    chmod +x "$launcher"
  done
fi


# Finalize
echo
echo "DONE"
read -r -n 1 -s -p "Press any key to exit..."
echo
exit 0
