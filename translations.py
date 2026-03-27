UA = {
    "settings": "Налаштування",
    "theme": "Тема:",
    "language": "Мова:",
    "save": "Зберегти",
    "new_tab": "Нова вкладка",
    "search": "Пошук або адреса...",
    "socials": "Мої соціальні мережі",
}

EN = {
    "settings": "Settings",
    "theme": "Theme:",
    "language": "Language:",
    "save": "Save",
    "new_tab": "New tab",
    "search": "Search or enter address...",
    "socials": "My social media",
}

LANGUAGES = {
    "English": EN,
    "Українська": UA,
}

def get_lang(lang_name="English"):
    return LANGUAGES.get(lang_name, EN)
