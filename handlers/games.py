import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_user_balance, update_balance, add_transaction
from config import GAMES_CONFIG, GAMES_CHANNEL_ID
from bot import bot

router = Router()

# Эмодзи для рулетки
ROULETTE_NUMBERS = {
    0: "🟢", 1: "🔴", 2: "⚫", 3: "🔴", 4: "⚫", 5: "🔴", 6: "⚫", 7: "🔴", 8: "⚫", 9: "🔴", 10: "⚫",
    11: "⚫", 12: "🔴", 13: "⚫", 14: "🔴", 15: "⚫", 16: "🔴", 17: "⚫", 18: "🔴", 19: "🔴", 20: "⚫",
    21: "🔴", 22: "⚫", 23: "🔴", 24: "⚫", 25: "🔴", 26: "⚫", 27: "🔴", 28: "⚫", 29: "⚫", 30: "🔴",
    31: "⚫", 32: "🔴", 33: "⚫", 34: "🔴", 35: "⚫", 36: "🔴"
}

def get_roulette_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Красное", callback_data="roulette_red"),
            InlineKeyboardButton(text="⚫ Черное", callback_data="roulette_black")
        ],
        [
            InlineKeyboardButton(text="🟢 Зеро", callback_data="roulette_zero"),
            InlineKeyboardButton(text="🔢 Число", callback_data="roulette_number")
        ],
        [
            InlineKeyboardButton(text="1-18", callback_data="roulette_low"),
            InlineKeyboardButton(text="19-36", callback_data="roulette_high")
        ],
        [
            InlineKeyboardButton(text="Четное", callback_data="roulette_even"),
            InlineKeyboardButton(text="Нечетное", callback_data="roulette_odd")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_games")]
    ])
    return keyboard

def get_bet_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10", callback_data="bet_10"),
            InlineKeyboardButton(text="50", callback_data="bet_50"),
            InlineKeyboardButton(text="100", callback_data="bet_100")
        ],
        [
            InlineKeyboardButton(text="500", callback_data="bet_500"),
            InlineKeyboardButton(text="1000", callback_data="bet_1000"),
            InlineKeyboardButton(text="Макс", callback_data="bet_max")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="roulette")]
    ])
    return keyboard

@router.message(Command("games"))
async def games_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data="slots"),
            InlineKeyboardButton(text="🎯 Рулетка", callback_data="roulette")
        ],
        [
            InlineKeyboardButton(text="🎲 Кости", callback_data="dice"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ]
    ])
    
    await message.answer(
        "🎮 <b>Игровое меню</b>\n\n"
        "Выберите игру:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "roulette")
async def roulette_menu(callback: CallbackQuery):
    balance = get_user_balance(callback.from_user.id)
    
    await callback.message.edit_text(
        f"🎯 <b>Рулетка</b>\n\n"
        f"💰 Ваш баланс: {balance['main']:.2f} ₽\n\n"
        f"Выберите тип ставки:",
        reply_markup=get_roulette_keyboard()
    )

# Временное хранение данных игры
user_games = {}

@router.callback_query(F.data.startswith("roulette_"))
async def roulette_bet_type(callback: CallbackQuery):
    bet_type = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Сохраняем тип ставки
    if user_id not in user_games:
        user_games[user_id] = {}
    user_games[user_id]['bet_type'] = bet_type
    
    balance = get_user_balance(user_id)
    
    if bet_type == "number":
        await callback.message.edit_text(
            f"🎯 <b>Ставка на число</b>\n\n"
            f"💰 Ваш баланс: {balance['main']:.2f} ₽\n\n"
            f"Напишите число от 0 до 36:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="roulette")]
            ])
        )
        user_games[user_id]['waiting_number'] = True
    else:
        await callback.message.edit_text(
            f"🎯 <b>Рулетка - {get_bet_type_name(bet_type)}</b>\n\n"
            f"💰 Ваш баланс: {balance['main']:.2f} ₽\n\n"
            f"Выберите размер ставки:",
            reply_markup=get_bet_keyboard()
        )

def get_bet_type_name(bet_type):
    names = {
        'red': '🔴 Красное',
        'black': '⚫ Черное',
        'zero': '🟢 Зеро',
        'low': '1-18',
        'high': '19-36',
        'even': 'Четное',
        'odd': 'Нечетное'
    }
    return names.get(bet_type, bet_type)

@router.message(F.text.isdigit())
async def handle_number_bet(message: Message):
    user_id = message.from_user.id
    
    if user_id in user_games and user_games[user_id].get('waiting_number'):
        number = int(message.text)
        if 0 <= number <= 36:
            user_games[user_id]['number'] = number
            user_games[user_id]['waiting_number'] = False
            
            balance = get_user_balance(user_id)
            
            await message.answer(
                f"🎯 <b>Ставка на число {number}</b>\n\n"
                f"💰 Ваш баланс: {balance['main']:.2f} ₽\n\n"
                f"Выберите размер ставки:",
                reply_markup=get_bet_keyboard()
            )
        else:
            await message.answer("❌ Число должно быть от 0 до 36!")

@router.callback_query(F.data.startswith("bet_"))
async def process_bet(callback: CallbackQuery):
    user_id = callback.from_user.id
    bet_amount_str = callback.data.split("_")[1]
    
    balance = get_user_balance(user_id)
    
    if bet_amount_str == "max":
        bet_amount = min(balance['main'], GAMES_CONFIG['roulette']['max_bet'])
    else:
        bet_amount = int(bet_amount_str)
    
    if bet_amount < GAMES_CONFIG['roulette']['min_bet']:
        await callback.answer(f"❌ Минимальная ставка: {GAMES_CONFIG['roulette']['min_bet']} ₽")
        return
    
    if bet_amount > balance['main']:
        await callback.answer("❌ Недостаточно средств!")
        return
    
    if bet_amount > GAMES_CONFIG['roulette']['max_bet']:
        await callback.answer(f"❌ Максимальная ставка: {GAMES_CONFIG['roulette']['max_bet']} ₽")
        return
    
    # Получаем данные игры
    game_data = user_games.get(user_id, {})
    bet_type = game_data.get('bet_type')
    bet_number = game_data.get('number')
    
    if not bet_type:
        await callback.answer("❌ Ошибка! Начните игру заново.")
        return
    
    # Списываем ставку
    update_balance(user_id, -bet_amount, 'main')
    add_transaction(user_id, -bet_amount, 'roulette_bet', f'Ставка в рулетке: {get_bet_type_name(bet_type)}')
    
    # Отправляем информацию о ставке в канал
    await send_bet_to_channel(callback.from_user, bet_type, bet_amount, bet_number)
    
    # Показываем анимацию
    await callback.message.edit_text(
        f"🎯 <b>Рулетка запущена!</b>\n\n"
        f"🎰 Крутим рулетку...",
        reply_markup=None
    )
    
    # Анимация
    for i in range(3):
        await asyncio.sleep(1)
        await callback.message.edit_text(
            f"🎯 <b>Рулетка запущена!</b>\n\n"
            f"🎰 {'.' * (i + 1)}"
        )
    
    # Генерируем результат
    winning_number = random.randint(0, 36)
    winning_color = ROULETTE_NUMBERS[winning_number]
    
    # Проверяем выигрыш
    win_amount = calculate_roulette_win(bet_type, bet_amount, winning_number, bet_number)
    
    # Формируем результат
    if win_amount > 0:
        update_balance(user_id, win_amount, 'main')
        add_transaction(user_id, win_amount, 'roulette_win', f'Выигрыш в рулетке: {winning_number}')
        result_text = f"🎉 <b>ВЫИГРЫШ!</b>"
        result_emoji = "🎉"
    else:
        result_text = f"😔 <b>Проигрыш</b>"
        result_emoji = "😔"
    
    # Отправляем результат пользователю
    user_result_text = (
        f"{result_text}\n\n"
        f"🎯 Выпало: {winning_number} {winning_color}\n"
        f"💰 Ставка: {bet_amount:.2f} ₽\n"
        f"🎲 Тип ставки: {get_bet_type_name(bet_type)}"
    )
    
    if bet_type == 'number':
        user_result_text += f" ({bet_number})"
    
    if win_amount > 0:
        user_result_text += f"\n💵 Выигрыш: {win_amount:.2f} ₽"
    
    new_balance = get_user_balance(user_id)
    user_result_text += f"\n💰 Баланс: {new_balance['main']:.2f} ₽"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Играть еще", callback_data="roulette"),
            InlineKeyboardButton(text="🎮 Игры", callback_data="back_to_games")
        ]
    ])
    
    await callback.message.edit_text(user_result_text, reply_markup=keyboard)
    
    # Отправляем результат в канал
    await send_result_to_channel(callback.from_user, bet_type, bet_amount, bet_number, winning_number, win_amount, result_emoji)
    
    # Очищаем данные игры
    if user_id in user_games:
        del user_games[user_id]

async def send_bet_to_channel(user, bet_type, bet_amount, bet_number=None):
    """Отправляет информацию о ставке в канал"""
    try:
        user_name = user.full_name
        user_link = f"tg://user?id={user.id}"
        
        bet_info = get_bet_type_name(bet_type)
        if bet_type == 'number' and bet_number is not None:
            bet_info += f" ({bet_number})"
        
        channel_text = (
            f"🎯 <b>НОВАЯ СТАВКА В РУЛЕТКЕ</b>\n\n"
            f"👤 Игрок: <a href='{user_link}'>{user_name}</a>\n"
            f"🎲 Ставка: {bet_info}\n"
            f"💰 Сумма: {bet_amount:.2f} ₽\n"
            f"⏰ Ожидаем результат..."
        )
        
        await bot.send_message(GAMES_CHANNEL_ID, channel_text, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка отправки ставки в канал: {e}")

async def send_result_to_channel(user, bet_type, bet_amount, bet_number, winning_number, win_amount, result_emoji):
    """Отправляет результат игры в канал"""
    try:
        user_name = user.full_name
        user_link = f"tg://user?id={user.id}"
        
        bet_info = get_bet_type_name(bet_type)
        if bet_type == 'number' and bet_number is not None:
            bet_info += f" ({bet_number})"
        
        winning_color = ROULETTE_NUMBERS[winning_number]
        
        if win_amount > 0:
            result_text = f"{result_emoji} <b>ВЫИГРЫШ!</b>"
            win_text = f"\n💵 Выигрыш: {win_amount:.2f} ₽"
        else:
            result_text = f"{result_emoji} <b>Проигрыш</b>"
            win_text = ""
        
        channel_text = (
            f"🎯 <b>РЕЗУЛЬТАТ РУЛЕТКИ</b>\n\n"
            f"👤 Игрок: <a href='{user_link}'>{user_name}</a>\n"
            f"🎲 Ставка: {bet_info}\n"
            f"💰 Сумма ставки: {bet_amount:.2f} ₽\n"
            f"🎯 Выпало: {winning_number} {winning_color}\n"
            f"{result_text}{win_text}"
        )
        
        await bot.send_message(GAMES_CHANNEL_ID, channel_text, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка отправки результата в канал: {e}")

def calculate_roulette_win(bet_type, bet_amount, winning_number, bet_number=None):
    """Вычисляет выигрыш в рулетке"""
    if bet_type == 'red':
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        return bet_amount * 2 if winning_number in red_numbers else 0
    
    elif bet_type == 'black':
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        return bet_amount * 2 if winning_number in black_numbers else 0
    
    elif bet_type == 'zero':
        return bet_amount * 36 if winning_number == 0 else 0
    
    elif bet_type == 'low':
        return bet_amount * 2 if 1 <= winning_number <= 18 else 0
    
    elif bet_type == 'high':
        return bet_amount * 2 if 19 <= winning_number <= 36 else 0
    
    elif bet_type == 'even':
        return bet_amount * 2 if winning_number != 0 and winning_number % 2 == 0 else 0
    
    elif bet_type == 'odd':
        return bet_amount * 2 if winning_number % 2 == 1 else 0
    
    elif bet_type == 'number':
        return bet_amount * 36 if winning_number == bet_number else 0
    
    return 0

@router.callback_query(F.data == "slots")
async def slots_game(callback: CallbackQuery):
    balance = get_user_balance(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10", callback_data="slots_bet_10"),
            InlineKeyboardButton(text="50", callback_data="slots_bet_50"),
            InlineKeyboardButton(text="100", callback_data="slots_bet_100")
        ],
        [
            InlineKeyboardButton(text="500", callback_data="slots_bet_500"),
            InlineKeyboardButton(text="1000", callback_data="slots_bet_1000")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_games")]
    ])
    
    await callback.message.edit_text(
        f"🎰 <b>Слоты</b>\n\n"
        f"💰 Ваш баланс: {balance['main']:.2f} ₽\n"
        f"🎯 Выигрыш: x{GAMES_CONFIG['slots']['win_multiplier']}\n\n"
        f"Выберите размер ставки:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("slots_bet_"))
async def play_slots(callback: CallbackQuery):
    bet_amount = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    balance = get_user_balance(user_id)
    
    if bet_amount > balance['main']:
        await callback.answer("❌ Недостаточно средств!")
        return
    
    # Списываем ставку
    update_balance(user_id, -bet_amount, 'main')
    add_transaction(user_id, -bet_amount, 'slots_bet', 'Ставка в слотах')
    
    # Генерируем результат
    symbols = ['🍎', '🍊', '🍋', '🍇', '🍓', '💎', '7️⃣']
    result = [random.choice(symbols) for _ in range(3)]
    
    # Проверяем выигрыш
    if result[0] == result[1] == result[2]:
        win_amount = bet_amount * GAMES_CONFIG['slots']['win_multiplier']
        update_balance(user_id, win_amount, 'main')
        add_transaction(user_id, win_amount, 'slots_win', 'Выигрыш в слотах')
        
        result_text = f"🎉 <b>ДЖЕКПОТ!</b>\n\n"
        result_text += f"🎰 {' '.join(result)}\n\n"
        result_text += f"💰 Ставка: {bet_amount:.2f} ₽\n"
        result_text += f"💵 Выигрыш: {win_amount:.2f} ₽"
    else:
        result_text = f"😔 <b>Не повезло</b>\n\n"
        result_text += f"🎰 {' '.join(result)}\n\n"
        result_text += f"💰 Ставка: {bet_amount:.2f} ₽"
    
    new_balance = get_user_balance(user_id)
    result_text += f"\n💰 Баланс: {new_balance['main']:.2f} ₽"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Играть еще", callback_data="slots"),
            InlineKeyboardButton(text="🎮 Игры", callback_data="back_to_games")
        ]
    ])
    
    await callback.message.edit_text(result_text, reply_markup=keyboard)

@router.callback_query(F.data == "dice")
async def dice_game(callback: CallbackQuery):
    balance = get_user_balance(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10", callback_data="dice_bet_10"),
            InlineKeyboardButton(text="50", callback_data="dice_bet_50"),
            InlineKeyboardButton(text="100", callback_data="dice_bet_100")
        ],
        [
            InlineKeyboardButton(text="500", callback_data="dice_bet_500"),
            InlineKeyboardButton(text="1000", callback_data="dice_bet_1000")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_games")]
    ])
    
    await callback.message.edit_text(
        f"🎲 <b>Кости</b>\n\n"
        f"💰 Ваш баланс: {balance['main']:.2f} ₽\n"
        f"🎯 Выигрыш при 6: x{GAMES_CONFIG['dice']['win_multiplier']}\n\n"
        f"Выберите размер ставки:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("dice_bet_"))
async def play_dice(callback: CallbackQuery):
    bet_amount = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    balance = get_user_balance(user_id)
    
    if bet_amount > balance['main']:
        await callback.answer("❌ Недостаточно средств!")
        return
    
    # Списываем ставку
    update_balance(user_id, -bet_amount, 'main')
    add_transaction(user_id, -bet_amount, 'dice_bet', 'Ставка в костях')
    
    # Отправляем кость
    dice_msg = await callback.message.answer_dice()
    dice_value = dice_msg.dice.value
    
    await asyncio.sleep(4)  # Ждем анимацию кости
    
    # Проверяем выигрыш
    if dice_value == 6:
        win_amount = bet_amount * GAMES_CONFIG['dice']['win_multiplier']
        update_balance(user_id, win_amount, 'main')
        add_transaction(user_id, win_amount, 'dice_win', 'Выигрыш в костях')
        
        result_text = f"🎉 <b>ВЫИГРЫШ!</b>\n\n"
        result_text += f"🎲 Выпало: {dice_value}\n"
        result_text += f"💰 Ставка: {bet_amount:.2f} ₽\n"
        result_text += f"💵 Выигрыш: {win_amount:.2f} ₽"
    else:
        result_text = f"😔 <b>Не повезло</b>\n\n"
        result_text += f"🎲 Выпало: {dice_value}\n"
        result_text += f"💰 Ставка: {bet_amount:.2f} ₽"
    
    new_balance = get_user_balance(user_id)
    result_text += f"\n💰 Баланс: {new_balance['main']:.2f} ₽"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Играть еще", callback_data="dice"),
            InlineKeyboardButton(text="🎮 Игры", callback_data="back_to_games")
        ]
    ])
    
    await callback.message.answer(result_text, reply_markup=keyboard)

@router.callback_query(F.data == "back_to_games")
async def back_to_games(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data="slots"),
            InlineKeyboardButton(text="🎯 Рулетка", callback_data="roulette")
        ],
        [
            InlineKeyboardButton(text="🎲 Кости", callback_data="dice"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ]
    ])
    
    await callback.message.edit_text(
        "🎮 <b>Игровое меню</b>\n\n"
        "Выберите игру:",
        reply_markup=keyboard
    )