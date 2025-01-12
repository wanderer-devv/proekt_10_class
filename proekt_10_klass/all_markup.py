from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from requests_in_bd import RequestsInBD

yes_or_no_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]], resize_keyboard=True, one_time_keyboard=True)

otmena_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True, one_time_keyboard=True)

def return_main_markup(user_id):
    requestsInBD = RequestsInBD()
    notif = requestsInBD.get_notif(user_id=user_id)
    requestsInBD.close_bd()

    if notif:
        if notif == 1:
            sub_or_unsub = 'Отписаться от уведомлений'
        elif notif == 2:
            sub_or_unsub = 'Подписаться на уведомления'

        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Прислать расписание')], 
                                                [KeyboardButton(text='Прислать расписание другого класса')], 
                                                [KeyboardButton(text='Изменить класс'), KeyboardButton(text='что то еще')], 
                                                [KeyboardButton(text=sub_or_unsub)]], resize_keyboard=True)
    elif not notif:
        return False