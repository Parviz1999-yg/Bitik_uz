import json
import os
from typing import Dict

class LocalizationService:
    def __init__(self, locales_dir: str = "locales", default_lang: str = "uz"):
        self.locales_dir = locales_dir
        self.default_lang = default_lang
        # Endi tuzilma: self.translations[lang_code][filename_without_ext][key]
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self._load_all_locales()

    def _load_all_locales(self):
        if not os.path.exists(self.locales_dir):
            return

        for lang_code in os.listdir(self.locales_dir):
            lang_path = os.path.join(self.locales_dir, lang_code)
            if os.path.isdir(lang_path):
                self.translations[lang_code] = {}
                
                for filename in os.listdir(lang_path):
                    if filename.endswith(".json"):
                        file_key = filename.replace(".json", "") # "cv" yoki "message"
                        file_path = os.path.join(lang_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                self.translations[lang_code][file_key] = data
                        except Exception as e:
                            print(f"Xatolik {lang_code}/{filename} yuklashda: {e}")

    def t(self, key: str, lang: str = None, file: str = "message") -> str:
        """file parametri orqali aniq fayldan ma'lumot olish"""
        lang = lang or self.default_lang
        
        # Til yoki fayl topilmasa, standart holat
        lang_data = self.translations.get(lang, self.translations.get(self.default_lang, {}))
        file_data = lang_data.get(file, {})
        
        return file_data.get(key, key)

i18n = LocalizationService()