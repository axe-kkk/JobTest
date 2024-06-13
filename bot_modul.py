import asyncio
import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandStart
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from parser import JobVacancy, DATABASE_URL
import os
import pytz

API_TOKEN = '7376816276:AAFOukskNNeo3cJ22kI6lHjj7vpyCS_-G4M'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
user_timezone = pytz.timezone('Europe/Kiev')


def create_report():
    today = datetime.now(user_timezone).strftime('%Y-%m-%d')
    today_start = datetime.strptime(today, '%Y-%m-%d')

    jobs = session.query(JobVacancy).filter(JobVacancy.datatime >= today_start).all()

    data = {
        "datatime": [job.datatime.strftime('%Y-%m-%d %H:%M:%S') for job in jobs],
        "vacancy_count": [job.vacancy_count for job in jobs],
    }

    if len(jobs) > 0:
        change = [0] + [jobs[i].vacancy_count - jobs[i - 1].vacancy_count for i in range(1, len(jobs))]
    else:
        change = []

    data["change"] = change

    df = pd.DataFrame(data)
    file_path = f"job_vacancies_{today}.xlsx"
    df.to_excel(file_path, index=False)
    return os.path.abspath(file_path)


@dp.message(CommandStart())
async def cmd_help(message: Message):
    await message.answer("Hello! Use /get_today_statistic to get today's job vacancies report.")


@dp.message(Command('get_today_statistic'))
async def send_statistic(message: Message):
    file_path = create_report()
    await message.reply_document(FSInputFile(file_path))


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')
