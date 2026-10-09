# Click Uzbekistan webhook sozlash (bitik.uz)

## 1. Public URL

Railway / server domainingiz:

```text
https://YOUR-APP.up.railway.app/click/webhook
```

Health-check:

```text
GET https://YOUR-APP.up.railway.app/health
→ {"status":"ok","service":"bitik-click"}
```

## 2. Click merchant kabinet

1. [my.click.uz](https://my.click.uz) → Servis sozlamalari
2. **Prepare URL** va **Complete URL** (yoki bitta endpoint):
   - `https://YOUR-APP.up.railway.app/click/webhook`
3. Method: **POST** (form-data)
4. Secret key ni `CLICK_SECRET_KEY` env ga yozing

## 3. Environment variables

| O'zgaruvchi | Tavsif |
|-------------|--------|
| `CLICK_SECRET_KEY` | Merchant secret (imzo) |
| `CLICK_SERVICE_ID` | Servis ID |
| `CLICK_MERCHANT_ID` | Merchant ID |
| `CLICK_MERCHANT_USER_ID` | Merchant user ID |
| `CLICK_PROVIDER_TOKEN` | Telegram Invoice provider token |
| `PAYMENT_TEST_MODE` | `true` = test invoice |
| `DATABASE_URL` | PostgreSQL |
| `PORT` | HTTP port (Railway avto) |

## 4. merchant_trans_id formati

Bot yuboradi:

```text
bitik_user_{telegram_user_id}_{unix_timestamp}
```

Webhook shu formatdan `user_id` ni o'qiydi.

## 5. Imzo (MD5)

**Prepare (action=0):**

```text
md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time)
```

**Complete (action=1):**

```text
md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
```

## 6. Idempotentlik

`payments.click_trans_id` unique — bir xil to'lov ikki marta balansga tushmaydi.

## 7. Xatolik kodlari (Click)

| Kod | Ma'no |
|-----|--------|
| 0 | Success |
| -1 | Imzo xato |
| -3 | Action topilmadi |
| -4 | Allaqachon to'langan |
| -5 | User yo'q |
| -8 | merchant_trans_id xato |
