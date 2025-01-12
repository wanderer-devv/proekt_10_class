from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from requests_in_bd import RequestsInBD
from requests_rasp import ClassOfGetRasp
from all_markup import yes_or_no_markup, otmena_markup, return_main_markup
import asyncio

requestsInBD = RequestsInBD()
classOfGetRasp = ClassOfGetRasp()

main_menu_for_error = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Прислать расписание')], 
                                        [KeyboardButton(text='Прислать расписание другого класса')], 
                                        [KeyboardButton(text='Изменить класс'), KeyboardButton(text='что то еще')]])

class user_states(StatesGroup):
    set_grade = State()
    yes_or_no = State()
    other_class = State()
    new_class = State()

token = '7146065095:AAFFF9CDXUhm_uttw5ekm84OWunzVKwSxaU'

bot = Bot(token=token)
dp = Dispatcher()

async def send_main_menu(message, text):
    main_menu = return_main_markup(message.from_user.id)
    if main_menu:
        await message.reply(text, reply_markup=main_menu)

    elif not main_menu:
        await message.reply('Error with func "return_main_markup"\nПожалуста, обратитесь к создателю бота через описание бота!', reply_markup=main_menu_for_error)



@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    check = requestsInBD.check(user_id=message.from_user.id)
    if check:
        await message.reply('Это Telegram-bot для рассылки расписания 5 школы г.Лысково!\nНапиши в каком ты классе...')
        await state.set_state(user_states.set_grade)
    elif not check:
        await send_main_menu(message, 'Ты уже подписан на уведомления,\nтебе незачем эта команда!')

@dp.message(user_states.set_grade)
async def yes_or_no_grade(message: Message, state: FSMContext):
    all_classes = classOfGetRasp.return_all_classes()
    grade = message.text

    try:
        grade = int(grade)
    except:
        None

    if grade in all_classes:
        await state.clear()
        await message.reply(f'Ты в {message.text} классе?', reply_markup=yes_or_no_markup)
        await state.update_data(grade = message.text)
        await state.set_state(user_states.yes_or_no)

    elif grade not in all_classes:
        await message.reply(f'Класса {grade} не существует...\nНапиши класс в котором ты обучаешься!')

@dp.message(user_states.yes_or_no)
async def fin_set_grade(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        data = await state.get_data()
        grade = data.get('grade')
        await state.clear()

        requestsInBD.add_user(user_id=message.from_user.id, grade=grade)

        await send_main_menu(message, f'Ты подписался на рассылку расписания {grade} класса!')

    elif message.text.lower() == 'нет':
        await message.reply('Напиши свой класс еще раз!')
        await state.set_state(user_states.set_grade)

@dp.message(F.text == 'Прислать расписание другого класса')
async def other_class(message: Message, state: FSMContext):
    await message.reply('Напишите в чат класс, расписание которого ты хочешь узнать!', reply_markup=otmena_markup)
    await state.set_state(user_states.other_class)

@dp.message(F.text == 'Отмена')
async def otmena(message: Message, state: FSMContext):
    await state.clear()
    grade = requestsInBD.return_user_grade(user_id=message.from_user.id)

    if grade:
        await send_main_menu(message, classOfGetRasp.return_rasp_for_user(grade=grade))
    
    elif not grade:
        await message.reply('Error with class "RequestsInBD" func "return_user_grade"\nПожалуйста, обратитесь к создателю бота (ссылка в описании бота)', reply_markup=main_menu_for_error)


@dp.message(user_states.other_class)
async def answer_class(message: Message, state: FSMContext):
    await state.clear()
    
    grade = message.text

    rasp = classOfGetRasp.return_rasp_for_user(grade=grade)

    if rasp:
        await send_main_menu(message, rasp)
    
    elif not rasp:
        await send_main_menu(message, 'Такого классе нет!')


@dp.message(F.text == 'Прислать расписание')
async def my_class(message: Message):
    grade_user = requestsInBD.return_user_grade(user_id=message.from_user.id)
    if grade_user:
        rasp_user = classOfGetRasp.return_rasp_for_user(grade=grade_user)

        await send_main_menu(message, rasp_user)
    
    elif not grade_user:
        await message.reply('Error with class "RequestsInBD" func "return_user_grade"\nПожалуйста, обратитесь к создателю бота (ссылка в описании бота)', reply_markup=main_menu_for_error)


@dp.message(F.text == 'Изменить класс')
async def replace_grade(message: Message, state: FSMContext):
    await message.reply('Пришли новый класс в чат!', reply_markup=otmena_markup)
    await state.set_state(user_states.new_class)


@dp.message(F.text == 'Отписаться от уведомлений')
async def unsub_notif(message: Message):
    notif_now = requestsInBD.get_notif(message.from_user.id)
    if notif_now == 1:
        requestsInBD.change_notif(user_id=message.from_user.id, value=2)
        await send_main_menu(message=message, text='Вы отписались от уведомалений!\nУдачи!')


@dp.message(F.text == 'Подписаться на уведомления')
async def unsub_notif(message: Message):
    notif_now = requestsInBD.get_notif(message.from_user.id)
    if notif_now == 2:
        requestsInBD.change_notif(user_id=message.from_user.id, value=1)
        grade_user = requestsInBD.return_user_grade(user_id=message.from_user.id)

        if grade_user:
            rasp = classOfGetRasp.return_rasp_for_user(grade=grade_user)
            await send_main_menu(message=message, text=f'Вы подписались на уведомаления!\n{rasp}')

        elif not grade_user:
            await message.reply('Error with class "RequestsInBD" func "return_user_grade"\nПожалуйста, обратитесь к создателю бота (ссылка в описании бота)', reply_markup=main_menu_for_error)



@dp.message(user_states.new_class)
async def end_of_new_class(message: Message, state: FSMContext):
    all_classes = classOfGetRasp.return_all_classes()

    new_grade = message.text
    try:
        new_grade = int(new_grade)
    except:
        None

    if new_grade in all_classes:
        requestsInBD.new_grade(user_id=message.from_user.id, grade=new_grade)
        await send_main_menu(message, f'Вы подписались на рассылку об изменение расписания {new_grade} класса!')

    elif new_grade not in all_classes:
        await send_main_menu(message, f'Класса {new_grade} не существует...')

    await state.clear()

async def check_of_rasp():
    while True:
        await asyncio.sleep(5)
        new_id = classOfGetRasp.id_file_of_rasp()
        last_id = open('last_id_file.txt', encoding='utf-8').read()
        if last_id != new_id:
            with open('last_id_file.txt', 'w', encoding='utf-8') as file:
                file.write(new_id)
                file.close()

            down_true_false = classOfGetRasp.download_rasp()
            users = requestsInBD.get_users()

            if down_true_false:
                classOfGetRasp.write_all_classes()

            for user in users:
                print(user)
                if down_true_false:
                    if user[2] == 1:
                        rasp = classOfGetRasp.return_rasp_for_user(user[1])
                        await bot.send_message(chat_id = user[0], text = rasp)

                elif not down_true_false:
                    await bot.send_message(chat_id = user[0], text = 'Расписание на завтра уже на сайте!\nЗаходи и смотри каких уроков нет...')


async def dp_polling():
    await dp.start_polling(bot)


async def main():
    task1 = asyncio.create_task(check_of_rasp())
    task2 = asyncio.create_task(dp_polling())

    await task1
    await task2


if __name__ == '__main__':
    asyncio.run(main()) 