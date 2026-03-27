#!/usr/bin/env python3
import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, 
                             QTabWidget, QPushButton, QDockWidget, QVBoxLayout, 
                             QLabel, QComboBox, QWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QEvent
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from languages import LANGS

# --- ШЛЯХИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
HOME_HTML = os.path.join(BASE_DIR, "home.html")
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
        self.settings_dock = None 

        self.tabs = TabBar()
        self.setCentralWidget(self.tabs)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL...")
        self.url_bar.returnPressed.connect(self.navigate)

        # --- ГАРЯЧІ КЛАВІШІ ---
        self.act_new_tab = QAction("New Tab", self)
        self.act_new_tab.setShortcut(QKeySequence("Ctrl+T")) 
        self.act_new_tab.triggered.connect(self.new_tab)
        self.addAction(self.act_new_tab)

        self.act_close_tab = QAction("Close Tab", self)
        self.act_close_tab.setShortcut(QKeySequence("Ctrl+W"))
        self.act_close_tab.triggered.connect(self.safe_close_current_tab)
        self.addAction(self.act_close_tab)

        # --- ПАНЕЛЬ ІНСТРУМЕНТІВ ---
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.btn_back = QAction("◀", self)
        self.btn_back.triggered.connect(lambda: self.tabs.currentWidget().back() if self.tabs.currentWidget() else None)
        self.toolbar.addAction(self.btn_back)

        self.btn_forward = QAction("▶", self)
        self.btn_forward.triggered.connect(lambda: self.tabs.currentWidget().forward() if self.tabs.currentWidget() else None)
        self.toolbar.addAction(self.btn_forward)

        self.btn_reload = QAction("↺", self)
        self.btn_reload.triggered.connect(lambda: self.tabs.currentWidget().reload() if self.tabs.currentWidget() else None)
        self.toolbar.addAction(self.btn_reload)

        self.toolbar.addWidget(self.url_bar)

        self.btn_add = QAction("＋", self)
        self.btn_add.triggered.connect(self.new_tab)
        self.toolbar.addAction(self.btn_add)

        self.btn_settings = QAction("☰", self)
        self.btn_settings.triggered.connect(self.open_settings)
        self.toolbar.addAction(self.btn_settings)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        settings = self.load_settings()
        self.apply_theme(settings.get("theme", "Black"))
        self.new_tab()

    def new_tab(self):
        browser = QWebEngineView()
        browser.installEventFilter(self) 
        if os.path.exists(HOME_HTML):
            browser.setUrl(QUrl.fromLocalFile(HOME_HTML))
        else:
            browser.setUrl(QUrl("https://www.google.com"))
            
        index = self.tabs.addTab(browser, "Loading...")
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(index, title[:25] + "..."))
        browser.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()) if browser == self.tabs.currentWidget() else None)
        self.tabs.setCurrentWidget(browser)

    def navigate(self):
        url = self.url_bar.text().strip()
        if not url: return
        if "." not in url or " " in url:
            url = "https://www.google.com/search?q=" + url
        elif not url.startswith("http"):
            url = "https://" + url
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setUrl(QUrl(url))

    def load_settings(self):
        conf = {"theme": "Black", "lang": "🇺🇦 UA"}
        if os.path.exists(SETTINGS_PATH):
             try:
                 with open(SETTINGS_PATH, "r", encoding='utf-8') as f:
                     conf.update(json.load(f))
             except: pass
        return conf

    def save_settings(self, settings):
        with open(SETTINGS_PATH, "w", encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    def apply_theme(self, theme_name):
        try:
            from themes import THEMES
            t = THEMES.get(theme_name, THEMES["Black"])
            
            # Застосовуємо стилі до всього вікна
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: {t['main']}; }}
                QToolBar {{ 
                    background-color: {t['toolbar']}; 
                    border-bottom: 1px solid {t['border']}; 
                    padding: 4px; 
                }}
                QLineEdit {{ 
                    background-color: {t['button']}; 
                    color: {t['text']}; 
                    border: 1px solid {t['border']}; 
                    border-radius: 6px; 
                }}
                QPushButton {{ 
                    background-color: {t['button']}; 
                    color: {t['text']}; 
                    border-radius: 4px;
                    padding: 4px;
                }}
                QLabel {{ color: {t['text']}; }}
            """)
        except Exception as e:
            print(f"Помилка теми: {e}")
         
    def open_settings(self):
        if self.settings_dock:
            self.settings_dock.show()
            return
            
        conf = self.load_settings()
        L = LANGS.get(conf.get("lang", "🇺🇸 EN"), LANGS["🇺🇸 EN"])
        
        self.settings_dock = QDockWidget(L["settings"], self) # Заголовок дока мовою користувача
        container = QWidget()
        layout = QVBoxLayout()

        # --- ВИБІР МОВИ ---
        layout.addWidget(QLabel(L["lang"]))
        lang_box = QComboBox()
        
        # Робимо English першою у списку
        all_langs = list(LANGS.keys())
        en_key = "🇺🇸 EN"
        if en_key in all_langs:
            all_langs.remove(en_key)
            all_langs.insert(0, en_key)
            
        lang_box.addItems(all_langs)
        lang_box.setCurrentText(conf.get("lang", en_key))
        layout.addWidget(lang_box)

        # --- ВИБІР ТЕМИ ---
        layout.addSpacing(10)
        layout.addWidget(QLabel(L["theme"]))
        theme_box = QComboBox()
        theme_box.addItems(["Black", "White"])
        theme_box.setCurrentText(conf.get("theme", "Black"))
        layout.addWidget(theme_box)

        # --- СОЦМЕРЕЖІ ---
        layout.addSpacing(10)
        layout.addWidget(QLabel(L["social"]))
        social = {"Youtube": "https://www.youtube.com/@1NSANE-1NSANE", "Tiktok": "https://www.tiktok.com/@fenz089"}
        for name, url in social.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda ch, u=url: self.open_url(u))
            layout.addWidget(btn)

        # --- КНОПКА ЗБЕРЕГТИ ---
        layout.addSpacing(20)
        btn_save = QPushButton(L["save"])
        btn_save.clicked.connect(lambda: self.save_and_apply_full(lang_box.currentText(), theme_box.currentText(), self.settings_dock))
        layout.addWidget(btn_save)

        layout.addStretch(1)
        container.setLayout(layout)
        self.settings_dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)         

    def save_and_apply_full(self, lang, theme, dock):
        settings = self.load_settings()
        settings["lang"] = lang
        settings["theme"] = theme
        self.save_settings(settings)
        
        # 1. Оновлюємо кольори
        self.apply_theme(theme)
        
        # 2. Оновлюємо тексти інтерфейсу (ОСЬ ТУТ МАГІЯ)
        L = LANGS.get(lang, LANGS["🇺🇸 EN"])
        
        self.url_bar.setPlaceholderText(L["placeholder"]) # Тепер підказка в пошуку міняється!
        self.act_new_tab.setText(L["new_tab"])
        # Якщо у тебе заголовок Settings міняється:
        if dock:
            dock.setWindowTitle(L["settings"])
            dock.close()
            self.settings_dock = None
            
        print(f"LeafBrowser updated: {lang}")

    def safe_close_current_tab(self):
        if self.tabs.count() > 1:
            self.tabs.removeTab(self.tabs.currentIndex())
        else:
            self.close()

    def _reset_settings_dock(self):
        self.settings_dock = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LeafBrowser()
    window.show()
    sys.exit(app.exec())
