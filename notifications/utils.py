import asyncio
from telegram import Bot
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

def send_telegram_notification(appointment, action):
    doctor_message = f"You have an appointment with {appointment.patient.username} on {appointment.date_time}."
    patient_message = f"Your appointment with Dr. {appointment.doctor.username} on {appointment.date_time} has been {action}."

    chat_id = 1806940376 

    asyncio.run(bot.send_message(chat_id=chat_id, text=doctor_message))
    asyncio.run(bot.send_message(chat_id=chat_id, text=patient_message))
