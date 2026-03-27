#!/bin/bash

APP_NAME="LeafBrowser"
INSTALL_DIR="/opt/$APP_NAME"
BIN_PATH="/usr/bin/$APP_NAME"
DESKTOP_PATH="/usr/share/applications/$APP_NAME.desktop"

echo "🗑️ Uninstalling $APP_NAME from the system..."

# 1. Видаляємо основні файли програми
if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Removing files from $INSTALL_DIR..."
    sudo rm -rf "$INSTALL_DIR"
fi

# 2. Видаляємо команду з термінала
if [ -f "$BIN_PATH" ]; then
    echo "🚀 Removing executable from $BIN_PATH..."
    sudo rm -f "$BIN_PATH"
fi

# 3. Видаляємо ярлик з меню (GNOME/KDE/Hyprland)
if [ -f "$DESKTOP_PATH" ]; then
    echo "🖼️ Removing desktop entry..."
    sudo rm -f "$DESKTOP_PATH"
fi

# 4. Оновлюємо базу даних, щоб іконка зникла з меню МИТТЄВО
sudo update-desktop-database

echo "------------------------------------------"
echo "✅ $APP_NAME has been completely removed."
echo "------------------------------------------"
