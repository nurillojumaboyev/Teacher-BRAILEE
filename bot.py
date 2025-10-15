from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import random
import re

# ======================= TOKEN =======================
TOKEN = "7962957365:AAHDjVkK-3FsmziQ1neeiHGFxCBKMsWslrs"  # Replace with your actual bot token from BotFather

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ======================= Braille kodlar =======================
kodlar = {
     'A': '1', 'B': '1-2', 'D': '1-4-5', 'E': '1-5',
    'F': '1-2-4', 'G': '1-2-4-5', 'H': '1-3-4-6', 'I': '2-4', 'J': '2-4-5',
    'K': '1-3', 'L': '1-2-3', 'M': '1-3-4', 'N': '1-3-4-5', 'O': '1-3-5',
    'P': '1-2-3-4', 'Q': '1-3-4-5-6', 'R': '1-2-3-5', 'S': '2-3-4', 'T': '2-3-4-5',
    'U': '1-2-6', 'V': '2-4-5-6', 'X': '1-2-5',
    'Y': '1-2-3-4-6', 'Z': '1-3-5-6', "G'": '1-2-4-5-6', "CH": '1-2-3-4-5',
    "SH": '1-5-6', "O'": '1-2-3-6', "NG": '1-3-4-5-1-2-4-5',
}
raqamdan_harfga = {v: k for k, v in kodlar.items()}

# Yozish rejimida oyna usuli uchun mapping (faqat murakkab holatlar uchun ishlatilmaydi)
WRITE_TO_READ = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
READ_TO_WRITE = {v: k for k, v in WRITE_TO_READ.items()}

# ======================= Tarjima funktsiyalar =======================
def tarjima_oqish(matn: str) -> str:
    matn = matn.upper()
    natija = []
    i = 0
    while i < len(matn):
        if matn[i:i+2] in ["G'", "O'", "CH", "SH", "NG"]:
            harf = matn[i:i+2]
            i += 2
        else:
            harf = matn[i]
            i += 1
        if harf == ' ':
            natija.append('/')
        elif harf in kodlar:
            natija.append(kodlar[harf])
        else:
            natija.append('?')
    return ', '.join(natija)

def tarjima_yozish(matn: str) -> str:
    def almash(kod: str):
        parts = kod.split('-')
        swapped = [str(READ_TO_WRITE.get(int(p), int(p))) for p in parts]
        return '-'.join(swapped)
    matn = matn.upper()
    natija = []
    i = 0
    while i < len(matn):
        if matn[i:i+2] in ["G'", "O'", "CH", "SH", "NG"]:
            harf = matn[i:i+2]
            i += 2
        else:
            harf = matn[i]
            i += 1
        if harf == ' ':
            natija.append('/')
        elif harf in kodlar:
            natija.append(almash(kodlar[harf]))
        else:
            natija.append('?')
    return ', '.join(natija)

def raqamni_harfga(raqamli_matn: str, mode: str = "read") -> str:
    natija = []
    qismlar = re.split(r"[,\s]+", raqamli_matn.strip())
    for token in qismlar:
        if token == '/':
            natija.append(' ')
            continue
        if token in raqamdan_harfga:
            natija.append(raqamdan_harfga[token])
            continue
        parts = re.split(r"[-\s]+", token)
        mapped_parts = []
        ok = True
        for p in parts:
            if not p.isdigit():
                ok = False
                break
            d = int(p)
            mapped = WRITE_TO_READ.get(d, d) if mode == "write" else d
            mapped_parts.append(str(mapped))
        if not ok:
            natija.append('?')
            continue
        mapped_token = '-'.join(mapped_parts)
        if mapped_token in raqamdan_harfga:
            natija.append(raqamdan_harfga[mapped_token])
        else:
            natija.append('?')
    return ''.join(natija)

# ======================= Foydalanuvchi holati =======================
user_state = {}

# ======================= Asosiy menyu =======================
main_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔁 Matn ↔ Braille (Tarjima)", callback_data="translate"),
    InlineKeyboardButton("📚 O‘qishni o‘rganamiz", callback_data="learn_read"),
    InlineKeyboardButton("✏️ Yozishni o‘rganamiz", callback_data="learn_write"),
    InlineKeyboardButton("🎲 O‘qish o‘yini", callback_data="play_read_game"),
    InlineKeyboardButton("🎲 Yozish o‘yini", callback_data="play_write_game"),
    InlineKeyboardButton("🎓 Tiflopedagogika darslari", callback_data="menu_tiflopedagogika"),
    InlineKeyboardButton("📗 Tiflografiya darslari", callback_data="menu_tiflografiya"),
)

# ======================= Tiflopedagogika darslari (5 ta) =======================
tiflopedagogika_lessons = {
    1: {
        "title": "1-dars: Maxsus pedagogika haqida ma'lumot",
        "text": (
            "Maxsus pedagogika — bu nogironligi bo‘lgan bolalar va kattalar ta’lim-tarbiyasi bilan shug‘ullanadigan fan. "
            "U turli nuqson turlariga qarab bo‘linadi: tiflopedagogika (ko‘zi ojizlar), surdopedagogika (eshitish nuqsoni), "
            "oligofrenopedagogika (aqliy rivojlanishi bilan chegaralanganlar) va boshqalar. \n\n"
            "Maxsus pedagogika vazifalari:\n"
            "- maxsus ta’lim muhitini yaratish;\n"
            "- o‘quv metodlarini moslashtirish;\n"
            "- ijtimoiy moslashuv va kasbga yo‘naltirish;\n"
            "- psixologik yordam ko‘rsatish;\n"
            "- oila bilan hamkorlik qilish;\n"
            "- inklyuziv ta’limni rivojlantirish;\n"
            "- individual rivojlanish rejasini tuzish;\n"
            "- sensoriy qobiliyatlarni oshirish;\n"
            "- texnologik vositalarni joriy etish;\n"
            "- monitoring va baholash.\n\n"
            "Amaliy misol: ko‘rish nuqsoni bo‘lgan o‘quvchilar uchun Braille yoki audio materiallar."
        ),
        "tests": [
            ("Maxsus pedagogika kimlar bilan shug‘ullanadi?", ["Sportchilar", "Nogironligi bo‘lganlar", "O‘qituvchilar"], "Nogironligi bo‘lganlar"),
            ("Quyidagilardan qaysi biri maxsus pedagogikaga kiradi?", ["Tiflopedagogika", "Fizika", "Adabiyot"], "Tiflopedagogika")
        ]
    },
    2: {
        "title": "2-dars: Tiflopedagogika usullari",
        "text": (
            "Tiflopedagogika ko‘zi ojiz bolalar uchun maxsus usullarni qo‘llaydi:\n"
            "- Braille yozuvi o‘qitish;\n"
            "- Audio darslar;\n"
            "- Sensoriy mashqlar;\n"
            "- Taktil vositalar (teginish orqali o‘rganish);\n"
            "- Ovozli yordamchilar (screen readers);\n"
            "- Mobilite mashqlari (harakatlanish);\n"
            "- Individual audio materiallar;\n"
            "- Guruhli terapiya seanslari;\n"
            "- Kompyuter dasturlari (JAWS kabi);\n"
            "- O‘yin orqali o‘qitish.\n\n"
            "Maqsad: ko‘rish imkoniyatlarini kompensatsiya qilish va mustaqillikni oshirish."
        ),
        "tests": [
            ("Tiflopedagogikada qanday usul ishlatiladi?", ["Braille", "Matematika", "Chizmachilik"], "Braille"),
            ("Maqsad nima?", ["Mustaqillik", "Tezlik", "Dam olish"], "Mustaqillik")
        ]
    },
    3: {
        "title": "3-dars: O‘quv jarayonini moslashtirish",
        "text": (
            "O‘quv jarayonini moslashtirish uchun:\n"
            "- Individual rejalashtirish;\n"
            "- Maxsus jihozlar (Braille printerlar);\n"
            "- O‘qituvchi yordami;\n"
            "- Audio kitoblar va materiallar;\n"
            "- Taktil diagrammalar va xaritalar;\n"
            "- Vaqtni uzaytirish (qo'shimcha vaqt);\n"
            "- Sensoriy integratsiya mashqlari;\n"
            "- Inklyuziv sinf muhiti;\n"
            "- Psixologik qo‘llab-quvvatlash;\n"
            "- Monitoring tizimi.\n\n"
            "Bu ko‘zi ojiz o‘quvchilar uchun muhimdir."
        ),
        "tests": [
            ("Moslashtirishda nima kerak?", ["Individual reja", "Guruh ishi", "Hech nima"], "Individual reja"),
            ("Maxsus jihoz nima?", ["Braille printer", "Telefon", "Kitob"], "Braille printer")
        ]
    },
    4: {
        "title": "4-dars: Ijtimoiy integratsiya",
        "text": (
            "Ijtimoiy integratsiya uchun:\n"
            "- Guruhli mashqlar;\n"
            "- Madaniy tadbirlar;\n"
            "- Do‘stlik munosabatlari rivojlantirish;\n"
            "- Jamiyat tadbirlari (festivalar);\n"
            "- Sport va o‘yinlar (goalball);\n"
            "- Volonterlik dasturlari;\n"
            "- Oila va maktab hamkorligi;\n"
            "- Anti-diskriminatsiya treninglari;\n"
            "- Onlayn ijtimoiy tarmoqlar;\n"
            "- Kasbiy orientatsiya.\n\n"
            "Ko‘zi ojiz bolalar uchun jamiyatga moslashish muhim."
        ),
        "tests": [
            ("Ijtimoiy integratsiyada nima muhim?", ["Guruhli mashq", "Yolg‘iz ishlash", "Uxlash"], "Guruhli mashq"),
            ("Do‘stlik nima uchun?", ["Moslashish", "Tezlik", "Hech nima"], "Moslashish")
        ]
    },
    5: {
        "title": "5-dars: Texnologiyalar va yordam vositalari",
        "text": (
            "Texnologiyalar:\n"
            "- Braille displey;\n"
            "- Ekran o‘qituvchisi dasturlari;\n"
            "- Audio kitoblar;\n"
            "- Smartfon ilovalari (Seeing AI);\n"
            "- Optik tanish qurilmalar (OCR);\n"
            "- GPS navigatsiya (BlindSquare);\n"
            "- Elektron Braille mashinkalari;\n"
            "- Virtual reallik treninglari;\n"
            "- AI asosidagi yordamchilar;\n"
            "- Portativ scannerlar.\n\n"
            "Bu vositalar o‘quvchilarning o‘qish va yozishni osonlashtiradi."
        ),
        "tests": [
            ("Qanday texnologiya ishlatiladi?", ["Braille displey", "Telefon", "Kompyuter o‘yinlari"], "Braille displey"),
            ("Audio kitob nima uchun?", ["O‘qishni osonlashtirish", "Dam olish", "Yugurish"], "O‘qishni osonlashtirish")
        ]
    }
}

# ======================= Tiflografiya darslari (5 ta) =======================
tiflografiya_lessons = {
    1: {
        "title": "1-dars: Lui Brail va Brail yozuvi tarixi",
        "text": (
            "Louis Braille (1809–1852) Fransiyada tug‘ilgan. U ko‘rishni yo‘qotgan va Braille tizimini yaratdi. \n\n"
            "Brail tizimi 6 nuqtali modul asosida qurilgan. 1829 yilda nashr etildi.\n\n"
            "<b>Qo‘shimcha ma’lumot:</b> \n"
            "- Louis Braille tizimi harbiy shifrlashdan ilhomlangan;\n"
            "- U 3 yoshida jarohat oldi;\n"
            "- 15 yoshida tizimni tugatdi;\n"
            "- Fransiya institutida o‘qituvchi bo‘ldi;\n"
            "- Tizim 1854 yilda rasman qabul qilindi;\n"
            "- Hozir 200+ tilga moslashtirilgan;\n"
            "- UNESCO merosi;\n"
            "- Brail kuni 4 yanvar;\n"
            "- Ilk kitob 1837 yilda chop etildi;\n"
            "- O‘zbekistonda 1990-yillarda joriy etildi."
        ),
        "tests": [
            ("Louis Brail qachon yashagan?", ["XIX asr", "XX asr", "XVII asr"], "XIX asr"),
            ("Brail necha nuqtadan tashkil topgan?", ["6", "4", "8"], "6")
        ]
    },
    2: {
        "title": "2-dars: Brail tizimining asoslari",
        "text": (
            "Brail tizimi 6 nuqta (1-6) bilan harflarni ifodalaydi:\n"
            "- Har bir harf maxsus kombinatsiya;\n"
            "- Nuqtalar ikki ustunli (chap 1-3, o‘ng 4-6);\n"
            "- 64 ta mumkin bo‘lgan kombinatsiya;\n"
            "- Raqamlar harflar bilan boshlanadi;\n"
            "- Punktuatsiya belgilari mavjud;\n"
            "- Qisqartmalar (grade 2 Braille);\n"
            "- Musiqa notalari uchun alohida;\n"
            "- Matematika belgilari;\n"
            "- Kompyuter kodlari (Unicode);\n"
            "- O‘lchami standart (2.5mm nuqta).\n\n"
            "Bu tizim ko‘zi ojizlar uchun o‘qish va yozishni osonlashtiradi."
        ),
        "tests": [
            ("Brailda necha nuqta bor?", ["6", "4", "8"], "6"),
            ("Nuqtalar qanday joylashgan?", ["Ikki ustun", "Bitta qator", "Uch qator"], "Ikki ustun")
        ]
    },
    3: {
        "title": "3-dars: Harflar va raqamlar",
        "text": (
            "Brailda harflar va raqamlar maxsus kodlar bilan yoziladi:\n"
            "- A = 1;\n"
            "- B = 1-2;\n"
            "- 1 = 1 bilan boshlanadi;\n"
            "- Lotin alifbosi asosida;\n"
            "- O‘zbek harflari qo‘shimcha kodlar (masalan, O‘ = 1-2-3-6);\n"
            "- Raqam belgisi # oldindan qo‘yiladi;\n"
            "- Katta harf belgisi 6-nuqtadan oldin;\n"
            "- 26 harf + qo‘shimcha belgilar;\n"
            "- Kirill alifbosi varianti;\n"
            "- Unicode da U+2800 dan boshlanadi.\n\n"
            "Kodlarni o‘rganish muhimdir."
        ),
        "tests": [
            ("A harfi qanday?", ["1", "1-2", "1-4"], "1"),
            ("1 raqami qanday boshlanadi?", ["1", "2", "4"], "1")
        ]
    },
    4: {
        "title": "4-dars: Maxsus belgilari",
        "text": (
            "Brailda maxsus belgilar mavjud:\n"
            "- Bo‘sh joy = /;\n"
            "- Kapital harf = 6-ni qo‘shish;\n"
            "- Belgilar kombinatsiyasi;\n"
            "- Vergul = 2;\n"
            "- Nuqta = 2-5-6;\n"
            "- Savol belgisi = 2-3-6;\n"
            "- Tirnoq = 2-3-5;\n"
            "- Raqam belgisi # = 3-4-5-6;\n"
            "- Valyuta belgisi (masalan, $ = 1-2-4);\n"
            "- Matn formatlari (bold, italic).\n\n"
            "Bu tizimni murakkab matnlarda ishlatishga yordam beradi."
        ),
        "tests": [
            ("Bo‘sh joy qanday?", ["/", "1", "1-2"], "/"),
            ("Kapital harf uchun nima kerak?", ["6", "1", "4"], "6")
        ]
    },
    5: {
        "title": "5-dars: Brailni amaliy qo‘llash",
        "text": (
            "Brailni qo‘llash:\n"
            "- Kitoblar va qo‘llanmalar;\n"
            "- Belgilash (eshiklar, tugmalar);\n"
            "- Kompyuter dasturlari;\n"
            "- Lift tugmalari va menyu;\n"
            "- Dorilar qadoqlari;\n"
            "- Restoran menyulari;\n"
            "- Banknotlarda (ba'zi mamlakatlarda);\n"
            "- Teatr va muzeylar uchun;\n"
            "- Mobil ilovalar integratsiyasi;\n"
            "- O‘quv materiallari chop etish.\n\n"
            "Bu ko‘zi ojizlar uchun hayotni osonlashtiradi."
        ),
        "tests": [
            ("Brail qayerda ishlatiladi?", ["Kitoblar", "O‘yinlar", "Ovqat"], "Kitoblar"),
            ("Belgilash uchun nima?", ["Brail", "Ranglar", "Raqamlar"], "Brail")
        ]
    }
}

# ======================= /start handler =======================
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Salom! Men <b>Nurillo Teacherman</b>.\n"
        "Braille, o‘qish/yozishni va maxsus darslarni o‘rganamiz.\n\n"
        "Quyidagi menyudan tanlang:",
        reply_markup=main_menu
    )

# ======================= /stats handler =======================
@dp.message_handler(Command("stats"))
async def cmd_stats(message: types.Message):
    uid = message.from_user.id
    score = user_state.get(uid, {}).get("score", 0)
    correct = user_state.get(uid, {}).get("correct_answers", 0)
    wrong = user_state.get(uid, {}).get("wrong_answers", 0)
    await message.answer(
        f"📊 Statistikangiz:\n"
        f"Ballar: {score}\n"
        f"To‘g‘ri javoblar: {correct}\n"
        f"Xato javoblar: {wrong}",
        reply_markup=main_menu
    )

# ======================= Translate handler =======================
@dp.callback_query_handler(lambda c: c.data == "translate")
async def cb_translate(c: CallbackQuery):
    user_state[c.from_user.id] = {"mode": "translate"}
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Menyuga qaytish", callback_data="back_to_menu"))
    await c.message.answer(
        "🔁 Matn yuboring: matnni Braille kodiga aylantiraman;\n"
        "yoki raqamli Braille kodi yuboring (masalan, `1-2-4, /, 1-5`) — matnga aylantiraman.",
        reply_markup=kb
    )
    await c.answer()

@dp.message_handler()
async def cb_handle_text(message: types.Message):
    text = message.text.strip()
    state = user_state.get(message.from_user.id)
    if state and state.get("mode") == "translate":
        if re.fullmatch(r"[0-9,\-/\s]+", text):
            natija = raqamni_harfga(text, mode="read")
            await message.answer(f"<b>Matnga tarjima:</b>\n{natija}", reply_markup=main_menu)
        else:
            natija = tarjima_oqish(text)
            await message.answer(f"<b>Braille kodi (o‘qish):</b>\n{natija}", reply_markup=main_menu)
        return
    await message.answer("Quyidan menyudan tanlang:", reply_markup=main_menu)

# ======================= Learn read/write =======================
async def send_task(message: types.Message, user_id: int, mode: str = "read"):
    harf = random.choice(list(kodlar.keys()))
    expected = sorted([int(x) for x in kodlar[harf].split('-')])
    braille_code = kodlar[harf]

    user_state[user_id] = user_state.get(user_id, {})
    user_state[user_id].update({
        "mode": mode,
        "current_letter": harf,
        "expected": expected,
        "raw_answers": []
    })

    kb = InlineKeyboardMarkup(row_width=2)
    if mode == "read":
        kb.row(InlineKeyboardButton("🟦1", callback_data="dot_1"), InlineKeyboardButton("🟦4", callback_data="dot_4"))
        kb.row(InlineKeyboardButton("🟦2", callback_data="dot_2"), InlineKeyboardButton("🟦5", callback_data="dot_5"))
        kb.row(InlineKeyboardButton("🟦3", callback_data="dot_3"), InlineKeyboardButton("🟦6", callback_data="dot_6"))
        await message.answer(
            f"📚 <b>{harf}</b> harfini o‘qing (Braille kodi: {braille_code}).\n"
            f"Kerakli nuqtalarni tanlang:",
            reply_markup=kb
        )
    else:
        kb.row(InlineKeyboardButton("🟦4", callback_data="dot_4"), InlineKeyboardButton("🟦1", callback_data="dot_1"))
        kb.row(InlineKeyboardButton("🟦5", callback_data="dot_5"), InlineKeyboardButton("🟦2", callback_data="dot_2"))
        kb.row(InlineKeyboardButton("🟦6", callback_data="dot_6"), InlineKeyboardButton("🟦3", callback_data="dot_3"))
        await message.answer(
            f"✏️ <b>{harf}</b> harfini yozing (Braille kodi: {braille_code}).\n"
            f"Kerakli nuqtalarni tanlang (o‘ng tarafdan):",
            reply_markup=kb
        )
    kb.add(InlineKeyboardButton("◀️ Menyuga qaytish", callback_data="back_to_menu"))

@dp.callback_query_handler(lambda c: c.data == "learn_read")
async def cb_learn_read(c: CallbackQuery):
    await c.answer()
    await send_task(c.message, c.from_user.id, mode="read")

@dp.callback_query_handler(lambda c: c.data == "learn_write")
async def cb_learn_write(c: CallbackQuery):
    await c.answer()
    await send_task(c.message, c.from_user.id, mode="write")

# ======================= Game functions =======================
async def send_game_task(message: types.Message, user_id: int, mode: str):
    harf = random.choice(list(kodlar.keys()))
    expected = sorted([int(x) for x in kodlar[harf].split('-')])

    user_state[user_id] = user_state.get(user_id, {
        "score": 0,
        "correct_answers": 0,
        "wrong_answers": 0
    })
    user_state[user_id].update({
        "mode": mode,
        "current_letter": harf,
        "expected": expected,
        "raw_answers": []
    })

    kb = InlineKeyboardMarkup(row_width=2)
    if mode == "play_read_game":
        kb.row(InlineKeyboardButton("🟦1", callback_data="dot_1"), InlineKeyboardButton("🟦4", callback_data="dot_4"))
        kb.row(InlineKeyboardButton("🟦2", callback_data="dot_2"), InlineKeyboardButton("🟦5", callback_data="dot_5"))
        kb.row(InlineKeyboardButton("🟦3", callback_data="dot_3"), InlineKeyboardButton("🟦6", callback_data="dot_6"))
    else:
        kb.row(InlineKeyboardButton("🟦4", callback_data="dot_4"), InlineKeyboardButton("🟦1", callback_data="dot_1"))
        kb.row(InlineKeyboardButton("🟦5", callback_data="dot_5"), InlineKeyboardButton("🟦2", callback_data="dot_2"))
        kb.row(InlineKeyboardButton("🟦6", callback_data="dot_6"), InlineKeyboardButton("🟦3", callback_data="dot_3"))
    kb.add(InlineKeyboardButton("◀️ Menyuga qaytish", callback_data="back_to_menu"))

    await message.answer(
        f"🎲 <b>{harf}</b> harfining Braille kodini toping.\n"
        f"Kerakli nuqtalarni tanlang:",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "play_read_game")
async def cb_play_read_game(c: CallbackQuery):
    await c.answer()
    await send_game_task(c.message, c.from_user.id, mode="play_read_game")

@dp.callback_query_handler(lambda c: c.data == "play_write_game")
async def cb_play_write_game(c: CallbackQuery):
    await c.answer()
    await send_game_task(c.message, c.from_user.id, mode="play_write_game")

# ======================= Dot button handler =======================
@dp.callback_query_handler(lambda c: c.data.startswith("dot_"))
async def cb_dot(c: CallbackQuery):
    uid = c.from_user.id
    state = user_state.get(uid)
    if not state:
        await c.answer("Iltimos, rejimni tanlang.", show_alert=True)
        return

    raw_dot = int(c.data.split("_")[1])
    if raw_dot not in state["raw_answers"]:
        state["raw_answers"].append(raw_dot)

    raw_set = set(state["raw_answers"])
    expected_set = set(state["expected"])
    is_write_mode = state["mode"] in ["learn_write", "play_write_game"]

    # Har ikkala rejimda ham original expected ni tekshirish
    if raw_set == expected_set:
        if state["mode"].startswith("play_"):
            state["score"] = state.get("score", 0) + 10
            state["correct_answers"] = state.get("correct_answers", 0) + 1
            await c.answer()
            await bot.send_message(uid, f"✅ To‘g‘ri! Bu <b>{state['current_letter']}</b> harfi. (+10 ball, Jami: {state['score']})")
            await send_game_task(c.message, uid, state["mode"])
        else:
            await c.answer()
            await bot.send_message(uid, f"✅ To‘g‘ri! Bu <b>{state['current_letter']}</b> harfi.")
            await send_task(c.message, uid, state["mode"])
        return

    if len(state["raw_answers"]) >= len(state["expected"]):
        expected_str = '-'.join(map(str, state["expected"]))
        if state["mode"].startswith("play_"):
            state["wrong_answers"] = state.get("wrong_answers", 0) + 1
            await c.answer()
            await bot.send_message(
                uid,
                f"❌ Xato. To‘g‘ri javob: {expected_str} (Bu <b>{state['current_letter']}</b> harfi). Jami ball: {state.get('score', 0)}"
            )
            await send_game_task(c.message, uid, state["mode"])
        else:
            await c.answer()
            await bot.send_message(uid, f"❌ Xato. To‘g‘ri javob: {expected_str}")
            await send_task(c.message, uid, state["mode"])
        return

    await c.answer("🔹 Davom eting...")

# ======================= Darslar va testlar =======================
@dp.callback_query_handler(lambda c: c.data in ["menu_tiflopedagogika", "menu_tiflografiya"])
async def cb_lessons_menu(c: CallbackQuery):
    if c.data == "menu_tiflopedagogika":
        lessons = tiflopedagogika_lessons
        title = "🎓 Tiflopedagogika darslari"
        prefix = "ped"
    else:
        lessons = tiflografiya_lessons
        title = "📗 Tiflografiya darslari"
        prefix = "graf"
    kb = InlineKeyboardMarkup(row_width=1)
    for i in sorted(lessons.keys()):
        kb.add(InlineKeyboardButton(f"{i}. {lessons[i]['title']}", callback_data=f"lesson_{prefix}_{i}"))
    kb.add(InlineKeyboardButton("◀️ Menyuga qaytish", callback_data="back_to_menu"))
    await c.message.answer(title, reply_markup=kb)
    await c.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("lesson_"))
async def cb_show_lesson(c: CallbackQuery):
    parts = c.data.split("_")
    prefix, idx = parts[1], int(parts[2])
    lessons = tiflopedagogika_lessons if prefix == "ped" else tiflografiya_lessons
    lesson = lessons[idx]
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("📝 Testni boshlash", callback_data=f"test_{prefix}_{idx}_0"))
    kb.add(InlineKeyboardButton("◀️ Darslar menyusiga qaytish", callback_data=f"menu_{prefix}"))
    await c.message.answer(f"<b>{lesson['title']}</b>\n\n{lesson['text']}", reply_markup=kb)
    await c.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def cb_start_test(c: CallbackQuery):
    parts = c.data.split("_")
    prefix, idx, qn = parts[1], int(parts[2]), int(parts[3])
    lessons = tiflopedagogika_lessons if prefix == "ped" else tiflografiya_lessons
    test_list = lessons[idx]["tests"]
    if qn >= len(test_list):
        await c.message.answer("✅ Test tugadi! Asosiy yoki darslar menyusiga qayting.", reply_markup=main_menu)
        await c.answer()
        return
    question, options, correct = test_list[qn]
    kb = InlineKeyboardMarkup(row_width=1)
    for opt in options:
        kb.add(InlineKeyboardButton(opt, callback_data=f"answer_{prefix}_{idx}_{qn}_{opt}"))
    await c.message.answer(f"❓ {question}", reply_markup=kb)
    await c.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def cb_check_answer(c: CallbackQuery):
    parts = c.data.split("_", 4)
    prefix, idx, qn, chosen = parts[1], int(parts[2]), int(parts[3]), parts[4]
    lessons = tiflopedagogika_lessons if prefix == "ped" else tiflografiya_lessons
    question, options, correct = lessons[idx]["tests"][qn]
    if chosen == correct:
        await c.answer("✅ To‘g‘ri!", show_alert=True)
        await c.message.answer(f"✅ To‘g‘ri javob: {correct}")
    else:
        await c.answer("❌ Noto‘g‘ri.", show_alert=True)
        await c.message.answer(f"❌ Xato. To‘g‘ri javob: {correct}")
    await cb_start_test(types.CallbackQuery(id=c.id, from_user=c.from_user, message=c.message, data=f"test_{prefix}_{idx}_{qn+1}"))

# ======================= Back to menu =======================
@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def cb_back_to_menu(c: CallbackQuery):
    user_state.pop(c.from_user.id, None)
    await c.message.answer("Asosiy menyu:", reply_markup=main_menu)
    await c.answer()

# ======================= Run bot =======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)