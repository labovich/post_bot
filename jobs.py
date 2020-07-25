import asyncio
import collections
from datetime import datetime

import aiohttp
import dateparser
from bs4 import BeautifulSoup
from tortoise.exceptions import DoesNotExist

from models import Package, Action, User

SELECTED_URL = f'https://webservices.belpost.by/searchBy/'

Row = collections.namedtuple('Row', 'id date action office')


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
        for tr in grid_info.find_all("tr"):
            tds = tr.find_all('td')
            if tds:
                date = tds[0].get_text()
                date = dateparser.parse(date).date()
                action = tds[1].get_text()
                office = tds[2].get_text()
                rows.append(Row(id=id, date=date, action=action, office=office))
    else:
        action = page.find(id='Label48')
        date = datetime.now().date()
        rows.append(Row(id=id, date=date, action=action, office=''))

    return rows


async def get_packages_status():
    ids = await Package.all().values_list('id', flat=True)
    print(ids)

    result = await parallel(ids)

    for i in result:
        rows = parse_page(i)
        for row in rows:
            try:
                await Action.get(package_id=row.id, action=row.action)
                print(f'{row.id} - {row.action} exist')
            except DoesNotExist:
                await Action.create(package_id=row.id, action=row.action,
                                    date=row.date, office=row.office)
                user = await User.get(packages__id=row.id)
                print(f'{row.id} - {row.action} created')

                from main import bot
                message = f'Update status for <code>{row.id}</code> \nstatus {row.action} \noffice {row.office} \ndate {row.date}'
                await bot.send_message(user.id, message)
