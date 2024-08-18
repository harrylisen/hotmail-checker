import hashlib
import os
import shutil
from datetime import datetime

from colorama import Fore, Style
from telethon import TelegramClient


def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return {line.strip() for line in file if line.strip()}
    except FileNotFoundError:
        # 如果文件不存在，创建文件夹（如果需要）并创建空文件
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            pass  # 创建空文件
            return set()  # 返回空集合


def is_valid_email(item):
    # 简单的电子邮件格式检查，可以根据需要进行扩展 检查是否是 xx@xx.com:xx
    if 'http' in item or 'www' in item:
        return False
    if ':' not in item or '@' not in item:
        return False
    if '@' in item and ':' in item.split('@')[1]:
        email_address = item.split('@')[1].split(':')[0].strip()
        microsoft_domains = ['edu', 'outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'microsoft.com']
        if any(domain in email_address for domain in microsoft_domains):
            return True
        else:
            log_message(f"Skipping {item} - Not a Microsoft domain", color=Fore.WHITE, enable=False)
            return False
    return False


def log_message(message, color=Fore.WHITE, enable: int = 1):
    if enable > 0:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")


async def hook(client: TelegramClient):
    return


def md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def move_files(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)
        try:
            if os.path.isdir(src_item):
                # 如果是目录，递归调用move_files
                move_files(src_item, dst_item)
            else:
                # 如果是文件，复制并删除
                shutil.copy2(src_item, dst_item)
                os.remove(src_item)
        except PermissionError:
            log_message(f"无法删除 {src_item}，文件可能正在被使用。", color=Fore.RED, enable=False)
