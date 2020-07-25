from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError

import settings
from jobs import get_packages_status
from middlewares import ACLMiddleware
from models import Package

bot = Bot(token=settings.API_TOKEN, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(ACLMiddleware())

scheduler = AsyncIOScheduler()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm Post Bot!\nPowered by aiogram.")


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['(\/add)\s(\w{2}\d{9}\w{2})\s([\w\s\-\.]+)']))
async def add_package(message: types.Message, user, regexp_command):
    try:
        package_obj = await Package.create(id=regexp_command.group(2),
                                           description=regexp_command.group(3), user=user)
    except IntegrityError:
        package_obj = await Package.get(id=regexp_command.group(2))
        await message.reply(f"Package <code>{package_obj.id}</code> already exist")
        return

    await message.reply(f"You add package <code>{package_obj.id}</code>")


@dp.message_handler(commands=['list'])
async def add_package(message: types.Message, user):
    mess = ''
    id = 1

    packages = await user.packages

    for package in packages:
        action = await package.actions.order_by('-date').first()
        if action:
            mess += f'{id}. <code>{package.id}</code> - {package.description}\n {action.date}: {action.action}'
        id += 1

    await message.reply(mess)


async def on_startup(dp):
    await Tortoise.init(settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()
    scheduler.add_job(get_packages_status, trigger='cron', hour='*/3')
    scheduler.start()


async def on_shutdown(dp):
    scheduler.shutdown()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
