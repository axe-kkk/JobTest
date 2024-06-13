import asyncio
from parser import fetch_vacancies
from bot_modul import main as bot_main


async def main():
    parser_task = asyncio.create_task(fetch_vacancies())
    bot_task = asyncio.create_task(bot_main())

    await asyncio.gather(parser_task, bot_task)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Project stopped')
