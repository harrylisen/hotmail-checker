import os
import re
import sys
from asyncio import CancelledError
from typing import Union

import demoji
import yaml
from colorama import Fore
from telethon import TelegramClient, events
from telethon.errors import FileReferenceExpiredError
from telethon.tl import types

from utils import hook, log_message

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

api_id = config['tg']['api_id']
api_hash = config['tg']['api_hash']
phone = config['tg']['phone']
channel_list = config['tg']['channel_list']
save_path = config['tg']['save_path']
my_channel = config['tg']['my_channel']
forward_channel = config['tg']['forward_channel']


class TGDown:
    def __init__(self):
        self.client = None

    async def start_monit(self):
        @self.client.on(events.NewMessage(chats=tuple(channel_list)))
        async def event_handler(event):
            chat_id = event.message.peer_id.channel_id
            channel_title = await self.get_chat_title(chat_id)
            message = event.message
            log_message(f"Message: {message}", color=Fore.LIGHTBLUE_EX)
            if message.media is not None:
                if my_channel is not None and forward_channel is not None and chat_id != my_channel and message.file and message.file.name:
                    allow_domain = ['be', 'br', 'ca', 'ch', 'com', 'cz', 'de', 'es', 'eu', 'europe', 'fr', 'gmail',
                                    'good', 'hotmail', 'it', 'jp', 'live', 'mix', 'microsoft', 'nl', 'ok', 'outlook',
                                    'pl', 'private', 'pt', 'quality', 'uk', 'usa', 'us', 'valid', 'yahoo', 'ru', 'cn',
                                    'in', 'china', 'india', 'united states']
                    black_domain = ['@', 'http', 'channel', 't.me']
                    file_name = self.get_file_name(message).lower().strip()
                    if file_name.endswith('.txt') and any(domain in file_name for domain in allow_domain) and not any(
                            domain in file_name for domain in black_domain):
                        message.message = '✅Fresh Lines Daily Update \n\n🌩#mail_share 💥by_rick'
                        await self.client.send_message(entity=forward_channel, message=message)
                await self.download_file(channel_title, chat_id, message)

    async def get_chat_title(self, chat_id: int) -> Union[str, None]:
        if os.environ.get(str(chat_id)):
            return os.environ.get(str(chat_id))
        entity = await self.client.get_entity(chat_id)
        if isinstance(entity, types.User):
            title = f'{entity.username}({entity.first_name + str(entity.last_name)})'
        elif isinstance(entity, types.Channel):
            title = entity.title
        elif isinstance(entity, types.Chat):
            title = ''
        else:
            return None
        title = re.sub(r'[\\/:*?"<>|]', '', demoji.replace(title, ''))
        return title

    def get_file_name(self, message) -> str:
        if message.file.name:
            return message.file.name
        file_ext = '.jpg' if message.file.ext in ['.jpe', 'jpeg'] else message.file.ext
        if len(message.message) != 0:
            s_name = self.shorten_filename(demoji.replace(message.message, '[emoji]'), 50)
            return re.sub(r'[\\/:*?"<>|]', '_', s_name) + file_ext
        return self.get_file_id(message) + file_ext

    @staticmethod
    def shorten_filename(filename, limit=50):
        filename = filename.replace('\n', ' ')
        if len(filename) <= limit:
            return filename
        else:
            return filename[:int(limit / 2) - 3] + '...' + filename[len(filename) - int(limit / 2):]

    @staticmethod
    def get_file_id(message) -> str:
        _id = 'unknown'
        if hasattr(message.media, 'document'):
            _id = message.media.document.id
        elif hasattr(message.media, 'photo'):
            _id = message.media.photo.id
        return str(_id)

    @staticmethod
    def check_file_name(file_name):
        microsoft_domains = ['outlook', 'hotmail', 'live', 'microsoft', 'us']
        black_domains = ['mix', 'gmail', 'yahoo', 'eu']
        only_name = ['quality', 'valid', 'private', 'good']
        if not file_name.endswith('.txt'):
            return False
        if any(domain in file_name for domain in microsoft_domains):
            return True
        if any(domain in file_name for domain in black_domains):
            return False
        if any(name == file_name for name in only_name):
            return True
        return False

    async def download_file(self, channel_title, channel_id, message, old=False):
        file_name = self.get_file_name(message).lower().strip()

        if self.check_file_name(file_name):
            file_path = os.path.join(save_path + '/new', f'{channel_title}', str(message.id) + file_name)
            file_size = message.file.size
            if file_size < 1024:
                log_message(f"File too small: {file_name}", color=Fore.LIGHTRED_EX)
                return
            if file_size > 600 * 1024:
                log_message(f"File too large: {file_name}", color=Fore.LIGHTRED_EX)
                return
            download_path = file_path + '.downloading'
            log_message(f"Starting download: {file_name}", color=Fore.LIGHTBLUE_EX)
            try:
                await message.download_media(download_path)
            except CancelledError:
                log_message("Download cancelled", color=Fore.LIGHTRED_EX)
                os.remove(download_path)
                sys.exit()
            except FileReferenceExpiredError:
                if old:
                    log_message('Retry failed, exiting download', color=Fore.LIGHTRED_EX)
                    exit(1)
                log_message('Download timed out, retrying', color=Fore.LIGHTYELLOW_EX)
                channel_data = await self.client.get_entity(int(channel_id))
                new_messages = self.client.iter_messages(entity=channel_data, ids=message.id)
                async for newMessage in new_messages:
                    await self.download_file(channel_title, channel_id, newMessage, old=True)
            except Exception as e:
                log_message(f"Download error: {e.__class__.__name__}", color=Fore.LIGHTRED_EX)
                os.remove(download_path)
            else:
                os.rename(download_path, file_path)
                log_message(f"Downloaded: {file_name}", color=Fore.LIGHTGREEN_EX)

    async def show_my_inf(self):
        me = await self.client.get_me()
        log_message('-----****************-----', color=Fore.LIGHTGREEN_EX)
        log_message(f"Name: {me.username}", color=Fore.LIGHTGREEN_EX)
        log_message(f"ID: {me.id}", color=Fore.LIGHTGREEN_EX)
        log_message('-----login successful-----', color=Fore.LIGHTGREEN_EX)

    def run(self):
        self.client = TelegramClient("test", api_id, api_hash)
        with self.client.start(phone=phone):
            self.client.loop.run_until_complete(self.show_my_inf())
            self.client.loop.run_until_complete(hook(self.client))
            self.client.loop.run_until_complete(self.start_monit())
            self.client.run_until_disconnected()


if __name__ == '__main__':
    tg_down = TGDown()
    tg_down.run()
