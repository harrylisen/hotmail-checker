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


class hotmails:
    def __init__(self):
        self.emails = []
        self.load_emails()

    @staticmethod
    def format_validation(data):
        return data.split(":")[0] + ':' + data.split(":")[1].split(" |")[0]

    def load_emails(self):
        total_count = 0
        valid_count = 0
        skipped_dead = 0
        skipped_live = 0
        email_set = set()  # 使用集合来自动去重

        # Load dead and live emails
        dead_emails = load_file(dead_emails_dir)
        live_emails = load_file(live_emails_dir)

        for filename in os.listdir(email_dir):
            filepath = os.path.join(email_dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as file:
                    for line in file:
                        total_count += 1
                        item = line.strip()
                        if item in dead_emails:
                            skipped_dead += 1
                            continue
                        if item in live_emails:
                            skipped_live += 1
                            continue
                        if is_valid_email(item):
                            valid_count += 1
                            email_set.add(self.format_validation(item))

        self.emails = list(email_set)

        unique_count = len(self.emails)  # 去重后的条数
        log_message(f"读取总条数: {total_count}", color=Fore.YELLOW)
        log_message(f"去重后有效条数: {unique_count}", color=Fore.GREEN)
        log_message(f"无效条数: {total_count - valid_count}", color=Fore.RED)
        log_message(f"跳过的死亡邮箱数量: {skipped_dead}", color=Fore.RED)
        log_message(f"跳过的已检测存活的邮箱数量: {skipped_live}", color=Fore.GREEN)
        log_message(f"MAX_WORKERS: {max_workers}", color=Fore.YELLOW)
        log_message(f"启动成功!", color=Fore.GREEN)

    def get_emails(self):
        return self.emails


if __name__ == '__main__':
    hotmails()
