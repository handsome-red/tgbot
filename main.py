import telebot
from telebot import types
import psycopg2
from datetime import datetime, date
import config

# Initialize bot
bot = telebot.TeleBot(config.TOKEN)


# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )


# Determine current week type (upper/lower)
def get_current_week_type():
    # You can implement your own logic here
    # For example, let's assume odd week numbers are "upper"
    week_number = datetime.now().isocalendar()[1]
    return "upper" if week_number % 2 == 1 else "lower"


# Create reply keyboard
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Понедельник')
    btn2 = types.KeyboardButton('Вторник')
    btn3 = types.KeyboardButton('Среда')
    btn4 = types.KeyboardButton('Четверг')
    btn5 = types.KeyboardButton('Пятница')
    btn6 = types.KeyboardButton('Расписание на текущую неделю')
    btn7 = types.KeyboardButton('Расписание на следующую неделю')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup


# Get schedule for a specific day
def get_schedule(day, week_type='current'):
    conn = get_db_connection()
    cur = conn.cursor()

    current_week_type = get_current_week_type()

    if week_type == 'current':
        query = """
        SELECT s.name, t.room_numb, t.start_time, te.full_name 
        FROM timetable t
        JOIN subject s ON t.subject = s.name
        LEFT JOIN teacher te ON t.teacher_id = te.id
        WHERE t.day = %s AND (t.week_type = %s OR t.week_type = 'both')
        ORDER BY t.start_time
        """
        cur.execute(query, (day, current_week_type))
    elif week_type == 'next':
        next_week_type = 'lower' if current_week_type == 'upper' else 'upper'
        query = """
        SELECT s.name, t.room_numb, t.start_time, te.full_name 
        FROM timetable t
        JOIN subject s ON t.subject = s.name
        LEFT JOIN teacher te ON t.teacher_id = te.id
        WHERE t.day = %s AND (t.week_type = %s OR t.week_type = 'both')
        ORDER BY t.start_time
        """
        cur.execute(query, (day, next_week_type))
    else:
        return None

    schedule = cur.fetchall()
    cur.close()
    conn.close()
    return schedule


# Get weekly schedule
def get_weekly_schedule(week_type='current'):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    weekly_schedule = {}

    for day in days:
        weekly_schedule[day] = get_schedule(day, week_type)

    return weekly_schedule


# Format schedule for display
def format_schedule(day, schedule):
    if not schedule:
        return f"{day}\n___________\nЗанятий нет\n___________"

    formatted = f"{day}\n___________\n"
    for lesson in schedule:
        subject, room, time, teacher = lesson
        time_str = time.strftime("%H:%M")
        formatted += f"{subject} | {room} | {time_str} | {teacher}\n"
    formatted += "___________"
    return formatted


# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте! Я бот с расписанием занятий. Чем могу помочь?",
        reply_markup=create_main_keyboard()
    )


# Week command handler
@bot.message_handler(commands=['week'])
def send_week_type(message):
    week_type = get_current_week_type()
    week_name = "верхняя" if week_type == "upper" else "нижняя"
    bot.send_message(
        message.chat.id,
        f"Сейчас {week_name} неделя",
        reply_markup=create_main_keyboard()
    )


# KSTU command handler
@bot.message_handler(commands=['kstu'])
def send_kstu_link(message):
    bot.send_message(
        message.chat.id,
        "Официальный сайт КНИТУ: https://www.kstu.ru/",
        reply_markup=create_main_keyboard()
    )


# Help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Я бот с расписанием занятий. Вот что я умею:

Основные команды:
/start - начать работу с ботом
/week - узнать текущую неделю (верхняя/нижняя)
/kstu - получить ссылку на сайт КНИТУ
/help - показать эту справку

Вы можете нажимать на кнопки ниже, чтобы получить расписание на нужный день или неделю.
"""
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=create_main_keyboard()
    )


# Text message handler
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    if text in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
        schedule = get_schedule(text)
        response = format_schedule(text, schedule)
        bot.send_message(message.chat.id, response, reply_markup=create_main_keyboard())

    elif text == 'Расписание на текущую неделю':
        schedule = get_weekly_schedule()
        for day, lessons in schedule.items():
            response = format_schedule(day, lessons)
            bot.send_message(message.chat.id, response, reply_markup=create_main_keyboard())

    elif text == 'Расписание на следующую неделю':
        schedule = get_weekly_schedule('next')
        for day, lessons in schedule.items():
            response = format_schedule(day, lessons)
            bot.send_message(message.chat.id, response, reply_markup=create_main_keyboard())

    else:
        bot.send_message(
            message.chat.id,
            "Извините, я Вас не понял",
            reply_markup=create_main_keyboard()
        )


# Start polling
if __name__ == '__main__':
    bot.polling(none_stop=True)