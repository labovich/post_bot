from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from tortoise.exceptions import DoesNotExist

from models import User


class ACLMiddleware(BaseMiddleware):
    async def setup_user(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):

        try:
            user_obj = await User.get(id=user.id)
        except DoesNotExist:
            user_obj = await User.create(id=user.id, username=user.username, last_name=user.last_name,
                                         first_name=user.first_name, chat_id=user.id)

        data["user"] = user_obj

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_user(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_user(data, query.from_user, query.message.chat if query.message else None)

