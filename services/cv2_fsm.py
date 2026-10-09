from services.fsm_base import BaseFSM


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


class Anketa2FSMService(BaseFSM):
    def __init__(self):
        flow = [
            Anketa2State.TALIM_MUASSASA,
            Anketa2State.YONALISH,
            Anketa2State.KURS,
            Anketa2State.FAMILIYA,
            Anketa2State.ISM,
            Anketa2State.SHARIF,
            Anketa2State.TUGILGAN,
            Anketa2State.MILLATI,
            Anketa2State.MALUMOTI,
            Anketa2State.OKISHGA_KIRGAN,
            Anketa2State.OKISHGA_KIRGUNCH,
            Anketa2State.OTA_ONA,
            Anketa2State.OTA_ONA_MANZL,
            Anketa2State.OILAVIY,
            Anketa2State.PASPORT,
            Anketa2State.DOIMIY_MANZIL,
            Anketa2State.IJARA,
            Anketa2State.IJARA_SANA,
        ]
        super().__init__(questions_flow=flow, anketa_type="anketa2")

    def finish(self, user_id: int, cleanup_photo_keys=None):
        super().finish(user_id, cleanup_photo_keys=cleanup_photo_keys or ["rasm", "user_photo"])


anketa2_fsm = Anketa2FSMService()
