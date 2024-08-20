import threading

import yaml

from check import EmailChecker
from check_sched import EmailCheckerSched
from tg_down import TGDown

with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

run_mode = config.get('run_mode', 'local') == 'local' and 'local' or 'tg   '
check_interval = config['tg'].get('check_interval', 3600 * 8)


def animate_banner():
    banner = (f"""
.================================================================.
||                    " HOTMAIL CHECKER "                       ||
|'--------------------------------------------------------------'|
||                                     -- BY RICK FOR LINUXDOER ||
|'=============================================================='|
||                                .::::.                        ||
||                              .::::::::.                      ||
||                              :::::::::::                     ||
||                              ':::::::::::..                  ||
||                              .:::::::::::::::'               ||
||                                '::::::::::::::.`             ||
||                                  .::::::::::::::::.'         ||
||                                .::::::::::::..               ||
||                              .::::::::::::::''               ||
||                   .:::.       '::::::::''::::                ||
||                 .::::::::.      ':::::'  '::::               ||
||                .::::':::::::.    :::::    '::::.             ||
||              .:::::' ':::::::::. :::::.     ':::.            ||
||            .:::::'     ':::::::::.::::::.      '::.          ||
||          .::::''         ':::::::::::::::'       '::.        ||
||         .::''              '::::::::::::::'        ::..      ||
||      ..::::                  ':::::::::::'         :'''`     ||
||   ..''''':'                    '::::::.'                     ||
|'=============================================================='|
||                      "  {run_mode}模式  "                          ||
'================================================================'
||                                      administrations@duck.com||
'================================================================'
""")
    import time
    for c in banner:
        time.sleep(0.001)
        print(c, end="")


if __name__ == '__main__':
    animate_banner()
    if run_mode != 'local':
        email_checker_sched = EmailCheckerSched(check_interval)
        run_scheduler = email_checker_sched.initialize()
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.start()
        tg_down = TGDown()
        tg_down.run()
        scheduler_thread.join()
    else:
        checker = EmailChecker()
        checker.run()
