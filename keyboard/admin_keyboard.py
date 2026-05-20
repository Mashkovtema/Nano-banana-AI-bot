from aiogram import types

async def main_admin_buttons():
    markup = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    btn1 = types.KeyboardButton(text='🎨 Генерация/Generation')
    btn2 = types.KeyboardButton(text='💳 Пополнить/Top up balance')
    btn3 = types.KeyboardButton(text='💡 Идеи и промпты/Ideas and Prompts')
    btn4 = types.KeyboardButton(text='ℹ️ Помощь/help')
    btn5 = types.KeyboardButton(text='👤 Реферальная программа/referal')
    btn6 = types.KeyboardButton(text='📄 База идей и промптов')
    markup.keyboard.append([btn1, btn2])
    markup.keyboard.append([btn3, btn4])
    markup.keyboard.append([btn5])
    markup.keyboard.append([btn6])
    return markup


async def add_or_delete():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_delete = types.InlineKeyboardButton(text='Добавить ➕', callback_data='add-idea')
    btn_add = types.InlineKeyboardButton(text='Удалить ✖️', callback_data='delete-idea')
    markup.inline_keyboard.append([btn_delete, btn_add])
    return markup


async def back_button(callback: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Назад', callback_data=callback, style='danger')
    markup.inline_keyboard.append([btn])
    return markup


async def yes_or_no(callback_prefix: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_yes = types.InlineKeyboardButton(text='Да', callback_data=f'{callback_prefix}_yes', style='success')
    btn_no = types.InlineKeyboardButton(text='Нет', callback_data=f'{callback_prefix}_no', style='danger')
    markup.inline_keyboard.append([btn_yes, btn_no])
    return markup


async def next_button():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Продолжить', callback_data='delete-idea')
    markup.inline_keyboard.append([btn])
    return markup


async def add_another():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Добавить еще', callback_data='add-idea')
    markup.inline_keyboard.append([btn])
    return markup


async def ideas_pagination(data: list, page: int):
    item_cnt = 2  # Кол-во объектов в одном блоке

    if (page < len(data) / item_cnt) and page >= 0:  # Проверка, что страница не последняя

        if len(data) % item_cnt > 0:  # Кол-во страниц
            all_pages = int(len(data) / item_cnt) + 1
        else:
            all_pages = int(len(data) / item_cnt)

        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
        if len(data) <= item_cnt:
            for obj in data:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["description"][:30], callback_data=f'select-idea-delete_{obj["id"]}')
                markup.inline_keyboard.append([btn])
        else:
            for obj in data[item_cnt * page: (item_cnt * page) + item_cnt]:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["description"][:30], callback_data=f'select-idea-delete_{obj["id"]}')
                markup.inline_keyboard.append([btn])

            btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'pagination-ideas_{page - 1}')
            btn_page = types.InlineKeyboardButton(text=f'Стр. {page + 1}/{all_pages}', callback_data=f'---')
            btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'pagination-ideas_{page + 1}')
            markup.inline_keyboard.append([btn_back, btn_page, btn_forward])

        btn_back = types.InlineKeyboardButton(text='Назад', callback_data='back-to-select-admin_select', style='danger')
        markup.inline_keyboard.append([btn_back])

        return markup

    else:
        return None