from services.cv_fsm import fsm

def add_relative(user_id: int, relative_text: str):
    # Foydalanuvchi kiritgan matnni ro'yxatga qo'shadi
    # Agar format "Ota, Ism, Yil, Kasb, Manzil" bo'lsa, uni ajratib olish mumkin
    parts = [p.strip() for p in relative_text.split(",")]
    
    relative_data = {
        "qarindosh": parts[0] if len(parts) > 0 else "-",
        "qarindosh_ism": parts[1] if len(parts) > 1 else "-",
        "qatr_ty_tj": parts[2] if len(parts) > 2 else "-",
        "qarin_kasb": parts[3] if len(parts) > 3 else "-",
        "qar_manzil": parts[4] if len(parts) > 4 else "-"
    }
    
    # FSM dagi ro'yxatga qo'shish
    fsm.add_data_to_list(user_id, "qarindoshlar_list", relative_data)