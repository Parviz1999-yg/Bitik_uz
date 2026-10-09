"""Umumiy FSM: holat va vaqtinchalik ma'lumotlarni xotirada saqlash."""
from typing import Any, Dict, List, Optional
import os


class BaseFSM:
    """CV va Anketa2 uchun umumiy finite-state machine."""

    def __init__(self, questions_flow: List[str], anketa_type: str = "cv"):
        self.anketa_type = anketa_type
        self.QUESTIONS_FLOW = list(questions_flow)
        self.QUESTION_KEYS = {s: f"ask_{s}" for s in self.QUESTIONS_FLOW}
        self._storage: Dict[int, Dict[str, Any]] = {}
        self._states: Dict[int, Optional[str]] = {}

    def set_state(self, user_id: int, state: Optional[str]) -> None:
        self._states[user_id] = state

    def get_state(self, user_id: int) -> Optional[str]:
        return self._states.get(user_id)

    def update_data(self, user_id: int, key: str, value: Any) -> None:
        if user_id not in self._storage:
            self._storage[user_id] = {}
        self._storage[user_id][key] = value

    def get_data(self, user_id: int) -> Dict[str, Any]:
        return self._storage.get(user_id, {})

    def finish(self, user_id: int, cleanup_photo_keys: Optional[List[str]] = None) -> None:
        data = self.get_data(user_id)
        keys = cleanup_photo_keys or ["rasm", "user_photo"]
        for key in keys:
            path = data.get(key)
            if path and isinstance(path, str) and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        self._states.pop(user_id, None)
        self._storage.pop(user_id, None)

    def get_question_key(self, state: Optional[str]) -> str:
        if not state:
            return ""
        return self.QUESTION_KEYS.get(state, "")

    def set_add_button_pressed(self, user_id: int, status: bool) -> None:
        self.update_data(user_id, "is_add_button_pressed", status)

    def is_add_button_pressed(self, user_id: int) -> bool:
        return bool(self.get_data(user_id).get("is_add_button_pressed", False))

    def add_data_to_list(self, user_id: int, key: str, value: Any) -> None:
        data = self.get_data(user_id)
        lst = data.get(key)
        if not isinstance(lst, list):
            lst = []
        lst.append(value)
        self.update_data(user_id, key, lst)

    def process_answer(self, user_id: int, answer: str) -> Optional[str]:
        """Javobni saqlab, keyingi holatni qaytaradi (oxirida None)."""
        current = self.get_state(user_id)
        if not current or current not in self.QUESTIONS_FLOW:
            return None
        idx = self.QUESTIONS_FLOW.index(current)
        self.update_data(user_id, current, answer)
        nxt = idx + 1
        if nxt < len(self.QUESTIONS_FLOW):
            next_state = self.QUESTIONS_FLOW[nxt]
            self.set_state(user_id, next_state)
            return next_state
        return None

    def start_flow(self, user_id: int, lang: str) -> Optional[str]:
        """Flowni boshidan ishga tushiradi, birinchi state ni qaytaradi."""
        if not self.QUESTIONS_FLOW:
            return None
        self.update_data(user_id, "cv_lang", lang)
        self.update_data(user_id, "waiting_for_format", False)
        first = self.QUESTIONS_FLOW[0]
        self.set_state(user_id, first)
        return first
