from typing import Dict, Any, Optional
import os

class Anketa2State:
    TALIM_MUASSASA = "talim_muassasa"
    YONALISH = "yonalish"
    KURS = "kurs"
    FAMILIYA = "familiya"
    ISM = "ism"
    SHARIF = "sharif"
    TUGILGAN = "tugilgan"
    MILLATI = "millati"
    MALUMOTI = "malumoti"
    OKISHGA_KIRGAN = "okishga_kirgan"
    OKISHGA_KIRGUNCH = "okishga_kirgunch"
    OTA_ONA = "ota_ona"
    OTA_ONA_MANZL = "ota_ona_manzl"
    OILAVIY = "oilaviy"
    PASPORT = "pasport"
    DOIMIY_MANZIL = "doimiy_manzil"
    IJARA = "ijara"
    IJARA_SANA = "ijara_sana"
    RASM = "rasm"
    
class Anketa2FSMService:
    def __init__(self):
        self.anketa_type = "anketa2"
        self._storage: Dict[int, Dict[str, Any]] = {}
        self._states: Dict[int, Optional[str]] = {}
        
        self.QUESTIONS_FLOW = [
            Anketa2State.TALIM_MUASSASA, Anketa2State.YONALISH, Anketa2State.KURS, Anketa2State.FAMILIYA, 
            Anketa2State.ISM, Anketa2State.SHARIF, Anketa2State.TUGILGAN, Anketa2State.MILLATI, Anketa2State.MALUMOTI, Anketa2State.OKISHGA_KIRGAN, 
            Anketa2State.OKISHGA_KIRGUNCH, Anketa2State.OTA_ONA, Anketa2State.OTA_ONA_MANZL, Anketa2State.OILAVIY, Anketa2State.PASPORT, 
            Anketa2State.DOIMIY_MANZIL, Anketa2State.IJARA, Anketa2State.IJARA_SANA
        ]
        self.QUESTION_KEYS = {state: f"ask_{state}" for state in self.QUESTIONS_FLOW}

    def set_state(self, user_id: int, state: str):
        self._states[user_id] = state

    def get_state(self, user_id: int) -> Optional[str]:
        return self._states.get(user_id)

    def update_data(self, user_id: int, key: str, value: Any):
        if user_id not in self._storage:
            self._storage[user_id] = {}
        self._storage[user_id][key] = value

    def get_data(self, user_id: int) -> Dict:
        return self._storage.get(user_id, {})

    def finish(self, user_id: int):
        data = self.get_data(user_id)
        photo_path = data.get("user_photo") if data else None
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except Exception:
                pass

        self._states.pop(user_id, None)
        self._storage.pop(user_id, None)

    def get_question_key(self, state: str) -> str:
        return self.QUESTION_KEYS.get(state, "")

    def process_answer(self, user_id: int, answer: str) -> Optional[str]:
        current_state = self.get_state(user_id)
        if not current_state or current_state not in self.QUESTIONS_FLOW:
            return None
            
        current_index = self.QUESTIONS_FLOW.index(current_state)
        self.update_data(user_id, current_state, answer)
        
        next_index = current_index + 1
        if next_index < len(self.QUESTIONS_FLOW):
            next_state = self.QUESTIONS_FLOW[next_index]
            self.set_state(user_id, next_state)
            return next_state
        else:
            return None

    def handle_message(self, user_id: int, text: str) -> Dict[str, Any]:
        next_state = self.process_answer(user_id, text)
        lang = self.get_data(user_id).get("cv_lang", "uz")
        key = self.get_question_key(next_state) if next_state else None
        return {"next_state": next_state, "key": key, "lang": lang}

anketa2_fsm = Anketa2FSMService()