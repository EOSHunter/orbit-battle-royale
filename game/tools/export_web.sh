#!/usr/bin/env bash
# Export the web build and copy the files the custom boot page (web/shell.html)
# loads next to index.html: key art, logo, favicon and fonts.
#
#   GODOT=/path/to/godot game/tools/export_web.sh
set -euo pipefail
GODOT="${GODOT:-godot}"
cd "$(dirname "$0")/.."
mkdir -p build/web/fonts
"$GODOT" --headless --export-release "Web" build/web/index.html
cp assets/ui/menu-art/key-art.jpg build/web/key-art.jpg
cp assets/ui/brand-and-ui/orbit-logo-masters/logo-horizontal.svg build/web/logo.svg
cp assets/ui/brand-and-ui/orbit-logo-masters/favicon.svg build/web/favicon.svg
cp assets/fonts/Archivo-Variable.ttf assets/fonts/IBMPlexSans-Variable.ttf build/web/fonts/
echo "Web build ready in game/build/web"
