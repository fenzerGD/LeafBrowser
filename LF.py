#!/usr/bin/env python3
import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, 
                             QTabWidget, QPushButton, QDockWidget, QVBoxLayout, 
                             QLabel, QComboBox, QWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QIcon

# --- ДИНАМІЧНІ ШЛЯХИ (Працюють всюди!) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
HOME_HTML = os.path.join(BASE_DIR, "home.html")
# Шлях до твоєї нової ави в папці icons
ICON_PATH = os.path.join(BASE_DIR, "icons", "LeafBrowser.png") 

class TabBar(QTabWidget):
    def __init__(self):
        super().__init__()

    def addTab(self, widget, title):
        index = super().addTab(widget, title)
        btn = QPushButton("✕")
        btn.setFixedSize(16, 16)
        btn.setStyleSheet("""
            QPushButton { background: transparent; color: #888; border: none; font-size: 12px; font-weight: bold; }
            QPushButton:hover { color: #ff5555; background: #333; border-radius: 3px; }
        """)
        btn.clicked.connect(lambda: self.removeTab(self.indexOf(widget)) if self.count() > 1 else None)
        self.tabBar().setTabButton(index, self.tabBar().ButtonPosition.RightSide, btn)
        return index

class LeafBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LeafBrowser Pre-Alpha")
        self.setGeometry(100, 100, 1100, 800)
        
        # Встановлюємо іконку вікна
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            print(f"Попередження: Іконку не знайдено за шляхом: {ICON_PATH}")

        self.tabs = TabBar()
        self.tabs.setTabsClosable(False)
        self.setCentralWidget(self.tabs)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Кнопки навігації
        btn_back = QAction("◀", self)
        btn_back.triggered.connect(lambda: self.tabs.currentWidget().back())
        toolbar.addAction(btn_back)

        btn_forward = QAction("▶", self)
        btn_forward.triggered.connect(lambda: self.tabs.currentWidget().forward())
        toolbar.addAction(btn_forward)

        btn_reload = QAction("↺", self)
        btn_reload.triggered.connect(lambda: self.tabs.currentWidget().reload())
        toolbar.addAction(btn_reload)

        # Адресна строка
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Type or paste a link")
        self.url_bar.returnPressed.connect(self.navigate)
        toolbar.addWidget(self.url_bar)

        # Нова вкладка
        btn_new_tab = QAction("＋", self)
        btn_new_tab.triggered.connect(self.new_tab)
        toolbar.addAction(btn_new_tab)

        # Налаштування
        btn_settings = QAction("☰", self)
        btn_settings.triggered.connect(self.open_settings)
        toolbar.addAction(btn_settings)

        # Завантаження налаштувань та теми
        settings = self.load_settings()
        self.apply_theme(settings.get("theme", "Black"))

        # Відкрити першу вкладку
        self.new_tab()

    def new_tab(self):
        browser = QWebEngineView()
        
        # Перевіряємо, чи є локальна домашня сторінка
        if os.path.exists(HOME_HTML):
            browser.setUrl(QUrl.fromLocalFile(HOME_HTML))
        else:
            browser.setUrl(QUrl("https://www.google.com"))
            
        index = self.tabs.addTab(browser, "Loading...")
        
        # Оновлення заголовка вкладки та адресної строки
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(index, title[:20] + "..."))
        browser.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()) if browser == self.tabs.currentWidget() else None)
        
        self.tabs.setCurrentWidget(browser)

    def navigate(self):
        url = self.url_bar.text().strip()
        if not url: return
        
        if "." not in url or " " in url:
            url = "https://www.google.com/search?q=" + url
        elif not url.startswith("http"):
            url = "https://" + url
            
        self.tabs.currentWidget().setUrl(QUrl(url))

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"theme": "Black"}

    def save_settings(self, settings):
        with open(SETTINGS_PATH, "w", encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    def apply_theme(self, theme_name):
        try:
            from themes import THEMES
            t = THEMES.get(theme_name, THEMES["Black"])
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: {t['main']}; }}
                QToolBar {{ background-color: {t['toolbar']}; border: none; padding: 4px; spacing: 5px; }}
                QLineEdit {{ background-color: {t['button']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 4px 10px; }}
                QTabBar::tab {{ background-color: {t['toolbar']}; color: {t['text']}; padding: 8px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }}
                QTabBar::tab:selected {{ background-color: {t['main']}; border-bottom: 2px solid {t['accent']}; }}
                QPushButton {{ color: {t['text']}; }}
            """)
        except Exception as e:
            print(f"Error applying theme: {e}")

    def open_settings(self):
        try:
            from themes import THEMES
            dock = QDockWidget("Settings", self)
            dock.setMinimumWidth(250)
            widget = QWidget()
            layout = QVBoxLayout()

            layout.addWidget(QLabel("Select theme:"))
            theme_box = QComboBox()
            theme_box.addItems(THEMES.keys())
            
            current_settings = self.load_settings()
            theme_box.setCurrentText(current_settings.get("theme", "Black"))
            layout.addWidget(theme_box)

            btn_save = QPushButton("Save")
            btn_save.clicked.connect(lambda: self.save_and_apply(theme_box.currentText(), dock))
            layout.addWidget(btn_save)

            layout.addStretch()
            widget.setLayout(layout)
            dock.setWidget(widget)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        except Exception as e:
            print(f"Error opening settings: {e}")

    def save_and_apply(self, theme_name, dock):
        settings = self.load_settings()
        settings["theme"] = theme_name
        self.save_settings(settings)
        self.apply_theme(theme_name)
        dock.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LeafBrowser()
    window.show()
    sys.exit(app.exec())

