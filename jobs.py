import asyncio
import collections
from datetime import datetime

import aiohttp
import dateparser
from bs4 import BeautifulSoup
from tortoise.exceptions import DoesNotExist

from models import Package, Action, User
from settings import ADMIN_CHAT_ID

SELECTED_URL = f'https://webservices.belpost.by/searchRu/'

Row = collections.namedtuple('Row', 'id date action office order_num')


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main(ids):
    tasks = []

    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        for id in ids:
            url = SELECTED_URL + id
            tasks.append(fetch(session, url))
        results = await asyncio.gather(*tasks)
    return results


async def parallel(ids):
    results = await main(ids)
    return results


def parse_page(page):
    page = BeautifulSoup(page, 'lxml')
    rows = []

    id = page.find(id='TxtNumPos').get('value')

    grid_info = page.find(id="GridInfo")

    if grid_info:
        order_num = 0
        for tr in grid_info.find_all("tr"):
            tds = tr.find_all('td')
            if tds:
                order_num += 1
                date = tds[0].get_text()
                date = dateparser.parse(date, date_formats=['%d.%m.%Y']).date()
                action = tds[1].get_text()
                office = tds[2].get_text()
                rows.append(Row(id=id, date=date, action=action, office=office, order_num=order_num))
    else:
        action = page.find(id='Label48').get_text()
        date = datetime.now().date()
        rows.append(Row(id=id, date=date, action=action, office='', order_num=0))

    return rows


async def get_packages_status(ids=None):
    from main import bot

    if ids is None:
        ids = await Package.filter(done=False).all().values_list('id', flat=True)

    print(ids)

    result = await parallel(ids)

    for i in result:
        try:
            rows = parse_page(i)
        except Exception as err:
            await bot.send_message(ADMIN_CHAT_ID, str(err))
            raise err

        for row in rows:
            try:
                await Action.get(package_id=row.id, action=row.action)
                print(f'{row.id} - {row.action} exist')
            except DoesNotExist:
                action = await Action.create(package_id=row.id, action=row.action,
                                             date=row.date, office=row.office, order_num=row.order_num)
                user = await User.get(packages__id=row.id)
                print(f'{row.id} - {row.action} created')

                package = await action.package

                message = f'Update status for <code>{row.id}</code>\n{package.description}\nstatus {row.action} \noffice {row.office} \ndate {row.date}'
                await bot.send_message(user.id, message)

                if row.action == 'Вручено':
                    package.done = True
                    await package.save()

