from services.fsm_base import BaseFSM


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


class CVFSMService(BaseFSM):
    def __init__(self):
        flow = [
            CVState.FAMILIYA,
            CVState.ISM,
            CVState.NASAB,
            CVState.BOSHLANGICH_SANA,
            CVState.OLIYGOH,
            CVState.YONALISH,
            CVState.TOGILGAN_YILI,
            CVState.TOGILGAN_JOYI,
            CVState.MILLATI,
            CVState.PARTIYA,
            CVState.MALUMOTI,
            CVState.TUGATGAN,
            CVState.MUTAXASISLIGI,
            CVState.ILMIY_DARAJASI,
            CVState.ILMIY_UNVONI,
            CVState.TIL_BILISH,
            CVState.MUKOFOT,
            CVState.DEPUTATLIK,
            CVState.FAOLIYATI,
            CVState.QARINDOSHLAR,
        ]
        super().__init__(questions_flow=flow, anketa_type="cv")

    def set_state(self, user_id: int, state):
        super().set_state(user_id, state)
        if state == CVState.QARINDOSHLAR:
            self.set_add_button_pressed(user_id, True)


fsm = CVFSMService()
