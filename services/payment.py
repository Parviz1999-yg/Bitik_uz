import config
from database.users_repo import update_balance, get_user_balance, add_payment

class PaymentService:
    @staticmethod
    def format_amount_to_tiyin(amount_uzs: int) -> int:
        return int(amount_uzs * 100)

    @staticmethod
    def format_amount_to_sum(amount_tiyin: int) -> float:
        return amount_tiyin / 100

    @staticmethod
    def generate_click_pay_url(amount: float, transaction_param: str) -> str:
        formatted_amount = f"{amount:.2f}"
        url = (
            f"https://my.click.uz/services/pay/?"
            f"service_id={config.CLICK_SERVICE_ID}&"
            f"merchant_id={config.CLICK_MERCHANT_ID}&"
            f"merchant_user_id={getattr(config, 'CLICK_MERCHANT_USER_ID', 4)}&"
            f"amount={formatted_amount}&"
            f"transaction_param={transaction_param}&"
            f"card_type=uzcard"
        )
        return url

    @staticmethod
    async def process_successful_payment(user_id: int, amount_uzs: float) -> float:
        """
        To'lov muvaffaqiyatli bo'lganda bazadagi balansni yangilaydi,
        payments tarixiga yozadi va foydalanuvchining joriy umumiy balansini qaytaradi.
        """
        # Bazaga to'lov summasini qo'shish
        update_balance(user_id, amount_uzs)
        
        # Payments tarixiga yozib qo'yish
        add_payment(user_id, amount_uzs)
        
        # Yangi balansni bazadan o'qib olish
        current_balance = get_user_balance(user_id)
        
        return current_balance