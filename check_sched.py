import sched
import time

import yaml

from check import EmailChecker
from utils import log_message

with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

save_path = config['tg']['save_path']
live_emails_dir = config['checker']['live_emails_dir']


class EmailCheckerSched:
    def __init__(self, interval=28800):  # 默认间隔为1小时（3600秒）
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.interval = interval

    def run(self):
        start_time = time.time()
        live_mailboxes = EmailChecker().run_with_tg(save_path)
        with open(live_emails_dir, 'w') as file:
            for email_pwd in live_mailboxes:
                file.write(email_pwd + '\n')
        end_time = time.time()
        elapsed_time = end_time - start_time
        next_interval = max(0, int(float(self.interval) - elapsed_time))
        self.scheduler.enter(next_interval, 1, self.run)

    def start_scheduler(self):
        self.scheduler.enter(0, 1, self.run)
        log_message("定时任务已启动，每隔{}秒运行一次".format(self.interval))

    def run_scheduler(self):
        self.scheduler.run()

    def initialize(self):
        self.start_scheduler()
        return self.run_scheduler
