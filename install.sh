#!/bin/bash

APP_NAME="LeafBrowser"
# ОБОВ'ЯЗКОВО ДОДАЄМО / НА ПОЧАТКУ
INSTALL_DIR="/opt/$APP_NAME"
BIN_PATH="/usr/bin/$APP_NAME"
DESKTOP_PATH="/usr/share/applications/$APP_NAME.desktop"

echo "🌿 Installing $APP_NAME for real this time..."

# 1. Створюємо системну папку (sudo обов'язково)
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r . "$INSTALL_DIR"

# 2. Створюємо запускний файл у системній директорії
echo "#!/bin/bash
python3 $INSTALL_DIR/LF.py \"\$@\"" | sudo tee "$BIN_PATH" > /dev/null
sudo chmod +x "$BIN_PATH"

# 3. Створюємо ярлик для GNOME/KDE/Hyprland
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=LeafBrowser
Comment=Custom browser by GLEAF
Exec=$APP_NAME
Icon=$INSTALL_DIR/LeafBrowser.png
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true" | sudo tee "$DESKTOP_PATH" > /dev/null

# 4. Оновлюємо кеш меню
sudo update-desktop-database

# 5. Прибираємо "сміття", яке створилося помилково раніше
rm -rf opt/ usr/ 2>/dev/null

echo "🚀 Now it is REALLY installed in the system!"
