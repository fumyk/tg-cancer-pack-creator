# -*- coding: utf-8 -*-
import io
import os

import logging
import asyncio
from random import randint
from itertools import islice

import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from PIL import Image

from tools import box
from words import NameGen

API_TOKEN = os.getenv("API_TOKEN")
generator = NameGen(4, True, "")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def process(photo, chat_id, user_id, title, emoji):
    downloaded = await bot.download_file_by_id(photo[-1].file_id)
    img = Image.open(downloaded)
    x = min(img.size)
    img = img.crop((0, 0, x, x)).resize((2560, 2560), Image.ANTIALIAS)
    pack_name = await generator.generate_() + str(randint(1, 9)) + "_by_" + (await bot.get_me()).username

    b = io.BytesIO()
    img.crop(box[1]).save(b, format="PNG")
    b.seek(0)

    await bot.create_new_sticker_set(user_id=user_id, name=pack_name, title=title, png_sticker=b, emojis=emoji)
    logging.info("Created pack " + pack_name + " with title " + title)
    for k, v in islice(box.items(), 1, None):
        t = io.BytesIO()
        img.crop(v).save(t, format="PNG")
        t.seek(0)
        await bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=t, emojis=emoji)
        logging.info("Uploaded " + str(k))
    return "t.me/addstickers/" + pack_name


@dp.message_handler(content_types=ContentType.PHOTO)
async def photo_handler(message: types.Message):
    e = "😀"
    cap = "Another cancer pack"
    if message.caption:
        cap = "".join([c for c in message.caption if c not in emoji.UNICODE_EMOJI][:64])
        if cap == "":
            cap = "Another cancer pack"
        for c in message.caption:
            if c in emoji.UNICODE_EMOJI:
                e = c
    await message.reply("Секундочку...")
    await message.reply(await process(message.photo, message.chat.id, message.from_user.id, cap, e))
    logging.info("replied to " + str(message.from_user.id))

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nОтправь картинку и я сделаю из неё набор стикеров!\nМожно добавить описание к картинке, чтобы определить название набора.\nЕсли в описание добавить смайлик, он будет соответствовать каждому стикеру из набора.\nЕсли отправить несколько картинок, то я создам столько наборов, сколько было картинок, но названия у них будут стандартные.\n\nАвтор: @fumyk\nhttps://github.com/fumycat/tg-cancer-pack-creator")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
