import os

import yaml
from colorama import Fore

from utils import load_file, is_valid_email, log_message

with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

max_workers = config['checker']['max_workers']
email_dir = config['checker']['email_dir']
dead_emails_dir = config['checker']['dead_emails_dir']
live_emails_dir = config['checker']['live_emails_dir']
mode = config['checker'].get('mode', 'loose')


class Hotmail:
    def __init__(self):
        self.emails = []

    @staticmethod
    def format_validation(data):
        data = (data.split(":")[0] + ':' + data.split(":")[1].split("|")[0]).strip()
        return data

    def load_local_mailboxes(self):
        my_email_dir = email_dir
        skipped_dead, skipped_live, total_count, valid_count, mailboxes = self.checker_mailboxes(my_email_dir)
        unique_count = len(mailboxes)  # 去重后的条数
        self.log_info(skipped_dead, skipped_live, total_count, unique_count, valid_count)
        return mailboxes

    def load_tg_mailboxes(self, my_email_path):
        # Load dead and live emails
        skipped_dead, skipped_live, total_count, valid_count, mailboxes = self.checker_mailboxes(my_email_path,
                                                                                                 run_mode="tg")
        unique_count = len(mailboxes)
        self.log_info(skipped_dead, skipped_live, total_count, unique_count, valid_count)
        return mailboxes

    @staticmethod
    def log_info(skipped_dead, skipped_live, total_count, unique_count, valid_count):
        # 如果是严格模式
        if mode == 'strict':
            log_message(f"严格模式，只匹配edu", color=Fore.GREEN)
        else:
            log_message(f"宽松模式，匹配所有edu", color=Fore.GREEN)
        log_message(f"读取总条数: {total_count}", color=Fore.YELLOW)
        log_message(f"去重后有效条数: {unique_count}", color=Fore.GREEN)
        log_message(f"无效条数: {total_count - valid_count}", color=Fore.RED)
        log_message(f"跳过的死亡邮箱数量: {skipped_dead}", color=Fore.RED)
        log_message(f"跳过的已检测存活的邮箱数量: {skipped_live}", color=Fore.GREEN)
        log_message(f"MAX_WORKERS: {max_workers}", color=Fore.YELLOW)
        log_message(f"启动成功!", color=Fore.GREEN)

    def checker_mailboxes(self, my_email_path, run_mode="local"):
        total_count = 0
        valid_count = 0
        skipped_dead = 0
        skipped_live = 0
        email_set = set()  # 使用集合来自动去重
        dead_emails = load_file(dead_emails_dir)
        live_emails = load_file(live_emails_dir)
        # 添加所有live 邮箱到集合 重新去重 本地模式是逐条添加 所以没法w 只能r追加模式
        if run_mode != "local":
            email_set = set(live_emails)
            print(len(email_set))
        for dirpath, dirnames, filenames in os.walk(my_email_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', errors='ignore') as file:
                    for line in file:
                        if len(line.strip()) == 0 and len(line) > 50:
                            continue
                        total_count += 1
                        item = line.strip()
                        if item in dead_emails:
                            skipped_dead += 1
                            continue
                        if run_mode == "local" and item in live_emails:
                            skipped_live += 1
                            continue
                        if is_valid_email(item):
                            valid_count += 1
                            email_set.add(self.format_validation(item))
        mailboxes = list(email_set)
        return skipped_dead, skipped_live, total_count, valid_count, mailboxes


if __name__ == '__main__':
    Hotmail()
