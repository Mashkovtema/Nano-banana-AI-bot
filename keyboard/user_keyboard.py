from aiogram import types


async def main_buttons():
    markup = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    btn1 = types.KeyboardButton(text='🎨 Генерация/Generation')
    btn2 = types.KeyboardButton(text='💳 Пополнить/Top up balance')
    btn3 = types.KeyboardButton(text='💡 Идеи и промпты/Ideas and Prompts')
    btn4 = types.KeyboardButton(text='ℹ️ Помощь/help')
    btn5 = types.KeyboardButton(text='👤 Реферальная программа/referal')
    markup.keyboard.append([btn1, btn2])
    markup.keyboard.append([btn3, btn4])
    markup.keyboard.append([btn5])
    return markup


async def select_type():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_create_photo = types.InlineKeyboardButton(text='📝 Текст -> Фото/text -> photo', callback_data='select-type_generate-photo')
    btn_create_video = types.InlineKeyboardButton(text='📝 Текст -> Видео/text -> video', callback_data='select-type_generate-video')
    btn_redact_photo = types.InlineKeyboardButton(text='🖼 Фото -> Фото/photo -> photo', callback_data='select-type_edit-photo')
    markup.inline_keyboard.append([btn_create_photo])
    markup.inline_keyboard.append([btn_create_video])
    markup.inline_keyboard.append([btn_redact_photo])
    return markup


async def select_model_photo():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_1 = types.InlineKeyboardButton(text='Nano Banana (Gemini 2.5 Flash Image)', callback_data='select-model_google/gemini-2.5-flash-image')
    btn_2 = types.InlineKeyboardButton(text='Nano Banana 2 (Gemini 3.1 Flash Image Preview)', callback_data='select-model_google/gemini-3.1-flash-image-preview')
    btn_3 = types.InlineKeyboardButton(text='Nano Banana Pro (Gemini 3 Pro Image Preview)', callback_data='select-model_google/gemini-3-pro-image-preview')
    btn = types.InlineKeyboardButton(text='Назад/back', callback_data='back-generate_type', style='danger')
    markup.inline_keyboard.append([btn_1])
    markup.inline_keyboard.append([btn_2])
    markup.inline_keyboard.append([btn_3])
    markup.inline_keyboard.append([btn])
    return markup


async def select_model_video():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_1 = types.InlineKeyboardButton(text='Google: Veo 3.1 Fast (7р/сек)', callback_data='select-model_google/veo-3.1-fast')
    btn_3 = types.InlineKeyboardButton(text='Google: Veo 3.1 Lite (3р/сек)', callback_data='select-model_google/veo-3.1-lite')
    btn_4 = types.InlineKeyboardButton(text='Kling: Video v3.0 Pro (12р/сек)', callback_data='select-model_kwaivgi/kling-v3.0-pro')
    btn_5 = types.InlineKeyboardButton(text='Kling: Video v3.0 Standard (10р/сек)' , callback_data='select-model_kwaivgi/kling-v3.0-std')
    btn = types.InlineKeyboardButton(text='Назад/back', callback_data='back-generate_type', style='danger')
    markup.inline_keyboard.append([btn_1])
    markup.inline_keyboard.append([btn_3])
    markup.inline_keyboard.append([btn_4])
    markup.inline_keyboard.append([btn_5])
    markup.inline_keyboard.append([btn])
    return markup


async def back_button(callback: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Назад/back', callback_data=callback, style='danger')
    markup.inline_keyboard.append([btn])
    return markup


async def generate_settings_buttons(quality: str, format: str, type: str, long: int, model: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])

    format_dict = {
        '1:1': '1:1',
        '16:9': '16:9',
        '9:16': '9:16',
        '4:3': '4:3',
        '3:4': '3:4'
    }

    quality_dict = {
        '1k': '1k',
        '2k': '2k',
        '4k': '4k'
    }


    long_dict = {
        5: "5 сек",
        10: "10 сек",
        15: "15 сек",

        4: "4 сек",
        6: "6 сек",
        8: "8 сек"
    }

    format_dict[format] += '✅'
    long_dict[long] += '✅'
    quality_dict[quality] += '✅'

    btn_1_1 = types.InlineKeyboardButton(text=format_dict['1:1'], callback_data='select-settings_format_1:1')
    btn_16_9 = types.InlineKeyboardButton(text=format_dict['16:9'], callback_data='select-settings_format_16:9')
    btn_9_16 = types.InlineKeyboardButton(text=format_dict['9:16'], callback_data='select-settings_format_9:16')
    btn_4_3 = types.InlineKeyboardButton(text=format_dict['4:3'], callback_data='select-settings_format_4:3')
    btn_3_4 = types.InlineKeyboardButton(text=format_dict['3:4'], callback_data='select-settings_format_3:4')

    btn_1k = types.InlineKeyboardButton(text=quality_dict['1k'], callback_data='select-settings_quality_1k')
    btn_2k = types.InlineKeyboardButton(text=quality_dict['2k'], callback_data='select-settings_quality_2k')
    btn_4k = types.InlineKeyboardButton(text=quality_dict['4k'], callback_data='select-settings_quality_4k')

    markup.inline_keyboard.append([btn_1_1, btn_16_9, btn_9_16])
    markup.inline_keyboard.append([btn_4_3, btn_3_4])


    if type == 'generate-video':
        if 'veo' in model:
            btn_5_sec = types.InlineKeyboardButton(text=long_dict[4], callback_data='select-settings_long_4')
            btn_10_sec = types.InlineKeyboardButton(text=long_dict[6], callback_data='select-settings_long_6')
            btn_15_sec = types.InlineKeyboardButton(text=long_dict[8], callback_data='select-settings_long_8')
        else:
            btn_5_sec = types.InlineKeyboardButton(text=long_dict[5], callback_data='select-settings_long_5')
            btn_10_sec = types.InlineKeyboardButton(text=long_dict[10], callback_data='select-settings_long_10')
            btn_15_sec = types.InlineKeyboardButton(text=long_dict[15], callback_data='select-settings_long_15')

        markup.inline_keyboard.append([btn_5_sec, btn_10_sec, btn_15_sec])

    else:
        markup.inline_keyboard.append([btn_1k, btn_2k, btn_4k])

    btn_generate = types.InlineKeyboardButton(text='Генерировать/generate', callback_data='start-generate', style='primary')
    btn_back = types.InlineKeyboardButton(text='Назад/back', callback_data='back-generate_prompt', style='danger')

    markup.inline_keyboard.append([btn_generate])
    markup.inline_keyboard.append([btn_back])

    return markup


async def pagination_buttons(page: int, data: list):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])

    btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'pagination-user-ideas_{page - 1}')
    btn_page = types.InlineKeyboardButton(text=f'Стр./page {page + 1}/{len(data)}', callback_data=f'---')
    btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'pagination-user-ideas_{page + 1}')
    markup.inline_keyboard.append([btn_back, btn_page, btn_forward])
    return markup


async def money_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn100 = types.InlineKeyboardButton(text='100 💎', callback_data='select-money_100')
    btn200 = types.InlineKeyboardButton(text='300 💎', callback_data='select-money_300')
    btn500 = types.InlineKeyboardButton(text='500 💎', callback_data='select-money_500')
    btn1000 = types.InlineKeyboardButton(text='1000 💎', callback_data='select-money_1000')
    btn2000 = types.InlineKeyboardButton(text='2000 💎', callback_data='select-money_2000')
    btn5000 = types.InlineKeyboardButton(text='5000 💎', callback_data='select-money_5000')
    btn_another = types.InlineKeyboardButton(text='Другая сумма/another summ', callback_data='select-money_another')
    markup.inline_keyboard.append([btn100, btn200])
    markup.inline_keyboard.append([btn500, btn1000])
    markup.inline_keyboard.append([btn2000, btn5000])
    markup.inline_keyboard.append([btn_another])
    return markup


async def select_currency(amount: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_rub = types.InlineKeyboardButton(text='Рубль/Rub', callback_data='select-currency_RUB')
    btn_usd = types.InlineKeyboardButton(text='Доллар/Usd', callback_data='select-currency_USD')
    btn_eur = types.InlineKeyboardButton(text='Евро/Eur', callback_data='select-currency_EUR')
    btn_back = types.InlineKeyboardButton(text='Назад/back', callback_data='back-to-select-summ', style='danger')

    markup.inline_keyboard.append([btn_rub])

    if amount > 300:
        markup.inline_keyboard.append([btn_usd])
        markup.inline_keyboard.append([btn_eur])

    markup.inline_keyboard.append([btn_back])

    return markup


async def pay_button(url: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Оплатить/pay', url=url)
    markup.inline_keyboard.append([btn])
    return markup


async def go_to_pay_button():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_pay = types.InlineKeyboardButton(text='Оплатить/pay 💵', callback_data='back-to-select-summ')
    btn_back = types.InlineKeyboardButton(text='Назад/back', callback_data='back-generate_settings', style='danger')
    markup.inline_keyboard.append([btn_pay])
    markup.inline_keyboard.append([btn_back])
    return markup



















