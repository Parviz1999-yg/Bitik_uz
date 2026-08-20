# services/cv_fsm.py
from typing import Dict, Any, Optional

class CVState:
    FAMILIYA = "familiya"
    ISM = "ism"
    NASAB = "nasab"
    BOSHLANGICH_SANA = "boshlangich_sana"
    OLIYGOH = "oliygoh"
    YONALISH = "yonalish"
    TOGILGAN_YILI = "togilgan_yili"
    TOGILGAN_JOYI = "togilgan_joyi"
    MILLATI = "millati"
    PARTIYA = "partiya"
    MALUMOTI = "malmoti"
    TUGATGAN = "tugatgan"
    MUTAXASISLIGI = "mutaxasisligi"
    ILMIY_DARAJASI = "ilmiy_darajasi"
    ILMIY_UNVONI = "ilmiy_unvoni"
    TIL_BILISH = "til_bilish"
    MUKOFOT = "mukofot"
    DEPUTATLIK = "deputatlik"
    FAOLIYATI = "faoliyati"
    QARINDOSHLAR = "qarindosh"
    RASM = "rasm"

class CVFSMService:
    def __init__(self):
        self.anketa_type = "cv"
        self._storage: Dict[int, Dict[str, Any]] = {}
        self._states: Dict[int, Optional[str]] = {}
        
        # RASM bu yerda olib tashlandi, chunki u oxirgi savoldan keyin alohida qabul qilinadi
        self.QUESTIONS_FLOW = [
            CVState.FAMILIYA, CVState.ISM, CVState.NASAB, CVState.BOSHLANGICH_SANA,
            CVState.OLIYGOH, CVState.YONALISH, CVState.TOGILGAN_YILI, CVState.TOGILGAN_JOYI,
            CVState.MILLATI, CVState.PARTIYA, CVState.MALUMOTI, CVState.TUGATGAN,
            CVState.MUTAXASISLIGI, CVState.ILMIY_DARAJASI, CVState.ILMIY_UNVONI,
            CVState.TIL_BILISH, CVState.MUKOFOT, CVState.DEPUTATLIK, CVState.FAOLIYATI,
            CVState.QARINDOSHLAR
        ]
        self.QUESTION_KEYS = {state: f"ask_{state}" for state in self.QUESTIONS_FLOW}

    def set_state(self, user_id: int, state: str):
        self._states[user_id] = state
        if state == CVState.QARINDOSHLAR:
            self.set_add_button_pressed(user_id, True)

    def get_state(self, user_id: int) -> Optional[str]:
        return self._states.get(user_id)

    def update_data(self, user_id: int, key: str, value: Any):
        if user_id not in self._storage:
            self._storage[user_id] = {}
        self._storage[user_id][key] = value

    def get_data(self, user_id: int) -> Dict:
        return self._storage.get(user_id, {})

    def finish(self, user_id: int):
        self._states.pop(user_id, None)
        self._storage.pop(user_id, None)

    def get_question_key(self, state: str) -> str:
        return self.QUESTION_KEYS.get(state, "")

    def set_add_button_pressed(self, user_id: int, status: bool):
        self.update_data(user_id, "is_add_button_pressed", status)

    def is_add_button_pressed(self, user_id: int) -> bool:
        data = self.get_data(user_id)
        return data.get("is_add_button_pressed", False)

    def add_data_to_list(self, user_id: int, key: str, value: Any):
        data = self.get_data(user_id)
        if key not in data:
            data[key] = []
        if isinstance(data[key], list):
            data[key].append(value)
            self.update_data(user_id, key, data[key])

fsm = CVFSMService()