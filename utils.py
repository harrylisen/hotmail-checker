import os
from colorama import Fore, Style
from datetime import datetime


def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return {line.strip() for line in file}
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
        microsoft_domains = ['outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'microsoft.com']
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
