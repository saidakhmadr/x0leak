import structlog
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, LabeledPrice, InlineKeyboardMarkup, CallbackQuery, InputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluent.runtime import FluentLocalization
import os
from aiogram.types.input_file import FSInputFile

# Declare router
router = Router()
router.message.filter(F.chat.type == "private")

# Declare logger
logger = structlog.get_logger()

# Constants
PAYMENT_AMOUNT = 399
SUBJECTS = ["Математика", "Физика", "История", "Русский"]

# Helper function to create welcome keyboard
def get_welcome_keyboard(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Файлы", callback_data="show_subjects")
    kb.button(text="ТГ канал", callback_data="show_channel")
    kb.adjust(1)
    return kb.as_markup()

# Helper function to create subjects keyboard
def get_subjects_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for subject in SUBJECTS:
        kb.button(text=subject, callback_data=f"subject_{subject}")
    kb.adjust(2)
    return kb.as_markup()

@router.message(CommandStart())
async def cmd_start(message: Message, l10n: FluentLocalization):
    await message.answer(
        "<b>👋 Добро пожаловать!</b>\n\n"
        "<b>Как пользоваться ботом:</b>\n"
        "1. Для получения файлов используйте одну из команд:\n"
        "   • /math — Математика\n"
        "   • /physics — Физика\n"
        "   • /history — История\n"
        "   • /russian — Русский\n"
        "2. Для получения ссылки на канал используйте команду /channel\n"
        "\nПример: <code>/math</code>\n"
        "\n<b>Сейчас тестовый режим — все материалы выдаются бесплатно!</b>"
    )

@router.callback_query(F.data == "show_subjects")
async def show_subjects(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(
        "Выберите предмет:",
        reply_markup=get_subjects_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "show_channel")
async def show_channel(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(
        l10n.format_value("tg-channel-link")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("subject_"))
async def process_subject_selection(callback: CallbackQuery, l10n: FluentLocalization):
    subject = callback.data.replace("subject_", "")
    
    # Create payment keyboard
    kb = InlineKeyboardBuilder()
    kb.button(
        text=l10n.format_value("payment-button-pay"),
        pay=True
    )
    kb.button(
        text=l10n.format_value("payment-button-cancel"),
        callback_data="cancel_payment"
    )
    kb.adjust(1)

    # Create invoice
    prices = [LabeledPrice(label="XTR", amount=PAYMENT_AMOUNT)]
    
    await callback.message.answer_invoice(
        title=l10n.format_value("payment-title"),
        description=l10n.format_value("payment-description", {"subject": subject}),
        prices=prices,
        provider_token="",  # Empty for Telegram Stars
        payload=f"subject_{subject}",
        currency="XTR",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(
        l10n.format_value("payment-button-cancel")
    )
    await callback.answer()

@router.message(F.successful_payment)
async def process_successful_payment(message: Message, l10n: FluentLocalization):
    subject = message.successful_payment.invoice_payload.replace("subject_", "")
    await message.answer(
        f"<b>✅ Оплата успешно произведена!</b>\nВот ваши материалы по предмету: {subject}",
        message_effect_id="5159385139981059251"
    )
    # Здесь отправьте файлы по предмету
    # Пример:
    # if subject == "Математика":
    #     await message.answer_document(document="file_id_1")
    #     await message.answer_document(document="file_id_2")

@router.message(Command("math"))
async def cmd_math(message: Message, l10n: FluentLocalization):
    prices = [LabeledPrice(label="XTR", amount=PAYMENT_AMOUNT)]
    await message.answer_invoice(
        title="Оплата за Математику",
        description="Оплата за доступ к материалам по математике.",
        prices=prices,
        provider_token="",  # Для Telegram Stars оставить пустым
        payload="subject_math",
        currency="XTR"
    )

@router.message(Command("physics"))
async def cmd_physics(message: Message, l10n: FluentLocalization):
    prices = [LabeledPrice(label="XTR", amount=PAYMENT_AMOUNT)]
    await message.answer_invoice(
        title="Оплата за Физику",
        description="Оплата за доступ к материалам по физике.",
        prices=prices,
        provider_token="",
        payload="subject_physics",
        currency="XTR"
    )

@router.message(Command("history"))
async def cmd_history(message: Message, l10n: FluentLocalization):
    prices = [LabeledPrice(label="XTR", amount=PAYMENT_AMOUNT)]
    await message.answer_invoice(
        title="Оплата за Историю",
        description="Оплата за доступ к материалам по истории.",
        prices=prices,
        provider_token="",
        payload="subject_history",
        currency="XTR"
    )

@router.message(Command("russian"))
async def cmd_russian(message: Message, l10n: FluentLocalization):
    prices = [LabeledPrice(label="XTR", amount=PAYMENT_AMOUNT)]
    await message.answer_invoice(
        title="Оплата за Русский",
        description="Оплата за доступ к материалам по русскому языку.",
        prices=prices,
        provider_token="",
        payload="subject_russian",
        currency="XTR"
    )

@router.message(Command("channel"))
async def cmd_channel(message: Message, l10n: FluentLocalization):
    await message.answer(
        "<b>📢 Наш Telegram канал:</b>\nhttps://t.me/+RaohlL6nhwY2NTYx",
        parse_mode="HTML"
    )

@router.message(Command("proof"))
async def cmd_proof(message: Message, l10n: FluentLocalization):
    await message.answer(
       "Мы не нуждаемся в твоих рублях. Каждый файл подписан нашей цепочкой верификации и сверяется в реальном времени с закрытыми каналами и хэш‑сверками. 🔐\n"
        "Оплата — не за данные, а твой билет в круг, где правда не молчит. 💡\n"
        "Никаких «скачать из интернета» — только гарантии и цифровая подпись.\n"
        "Не хочешь платить — оставайся в тишине.\n"
        "Платишь — вступаешь в реальность, где ложь не проходит проверку.\n"
        "Выбор за тобой. 🚪🔒"
        "Но раз ты настаиваешь, то вот тебе пруфы: "

    )
    folder = "tgbot"
    images = ["img1.png", "img2.png", "img3.png"]
    for img in images:
        path = os.path.join(folder, img)
        if os.path.isfile(path):
            await message.answer_photo(photo=FSInputFile(path))
        else:
            await message.answer(f"Фото не найдено: {img}")

@router.message(Command("help"))
async def cmd_help(message: Message, l10n: FluentLocalization):
    await message.answer(
        "<b>Доступные команды:</b>\n"
        "/start — приветствие и инструкция\n"
        "/help — список команд и помощь\n"
        "/math — получить материалы по математике\n"
        "/physics — получить материалы по физике\n"
        "/history — получить материалы по истории\n"
        "/russian — получить материалы по русскому языку\n"
        "/channel — получить ссылку на Telegram-канал\n"
        "/proof — доказательства и отзывы\n"
        "\n"
        "<b>Как пользоваться:</b>\n"
        "1. Введите нужную команду для получения материалов или информации.\n"
        "2. Для доступа к материалам потребуется оплата (399 звёзд).\n"
        "3. Доступ в телеграм канал (500 звёзд).\n"
        "4. После успешной оплаты вы получите файлы по выбранному предмету.\n"
        "5. Если возникли вопросы — пишите сюда или используйте /help.\n\n"
        "Если у вас возникли трудности, пишите сюда: @x0nHash\n"
        "Удачи."
    
    )

@router.message(Command("refund"))
async def cmd_refund(message: Message, l10n: FluentLocalization):
    await message.answer(
        "Возврат средств невозможен согласно правилам сервиса."
    ) 
    