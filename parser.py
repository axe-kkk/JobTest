from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import asyncio
import pytz


Base = declarative_base()

user_timezone = pytz.timezone('Europe/Kiev')


class JobVacancy(Base):
    __tablename__ = 'job_vacancies'
    id = Column(Integer, primary_key=True)
    vacancy_count = Column(Integer)
    datatime = Column(DateTime, default=lambda: datetime.now(user_timezone))

DATABASE_URL = "sqlite:///jobs.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

async def fetch_vacancies():
    while True:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get('https://robota.ua/zapros/junior/ukraine')
        try:
            vacancies_element = driver.find_element(By.XPATH, '//div[contains(text(), "ваканс")]')
            temp = vacancies_element.text.split(' ')
            vacancies_count = int(''.join(temp[:len(temp) - 1]))

            new_entry = JobVacancy(vacancy_count=int(vacancies_count))
            session.add(new_entry)
            session.commit()
            print(f"Fetched {int(vacancies_count)} vacancies at "
                  f"{datetime.now(user_timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Failed to fetch vacancies: {e}")
        finally:
            driver.quit()
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(fetch_vacancies())
