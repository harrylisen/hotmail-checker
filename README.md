# 🔥 Hotmail Checker

This project is a powerful email checker, mainly used to verify the validity of Hotmail accounts and detect .edu email
addresses. 🚀

## 🔄 Latest Updates

- 🆕 Support fetching emails from TG channels, scheduled crawling, and message forwarding

## 🌟 Features

- 🕵️ Check if Hotmail email addresses are valid
- 🎓 Detect .edu email addresses
- 💾 Save checked emails
- 📢 Support multiple notification methods (Bark, Push Plus, Server Chan)
- 🚀 Use proxies for checking, improving efficiency
- ⚙️ Support custom thread count to speed up checking
- 📊 Provide detailed statistics
- 🐳 Support Docker deployment

## 📋 How to Use

1. Ensure local directory structure

2. Configure the core options in the config file:

   - `run_mode`: Run mode, either `tg` for TG fetching or `local` for local reading
   - `log_level`: Log level, 1 for important only, 2 for fail logs, 3 for all logs
   - `mode`: Matching mode, either `strict` or `loose`
   - `push`: Notification configuration for Bark, Push Plus, or Server Chan
   - `tg`: Configure TG bot

## 🛠️ Installation

1. Clone the project repository:

```bash
git clone https://github.com/rickhqh/hotmail-checker.git
```

2. Configure project settings:

```bash
vim config/config.yaml
```

Then edit the `config/config.yaml` file according to your needs.

3. Launch the project:

```bash
sh start.sh
```

## 📁 Configuration File

The `config/config.yaml` file contains the following configuration options:

```yaml
checker:
   email_dir: emails # Email list directory
   proxies_dir: config/proxies.txt # Proxy list file
   dead_emails_dir: out/dead.txt # Invalid email save directory
   live_emails_dir: out/live.txt # Valid email save directory
   save_emails_dir: out/mail/ # Directory to save checked emails
   edu_emails_dir: out/edu.txt # .edu email save directory
   log_level: 3 # Log level 1 only important 2 fail log 3 all
   max_workers: 40 # Maximum number of worker threads
   mode: strict # strict or loose

run_mode: tg # tg or local

push:
   type: bark  # Notification type, options: bark, pushplus, serverchan
   token: xxxx # Notification token

tg:
   api_id: xxxx
   api_hash: xxxx
   phone: +86xxxxxxx # Phone number
   channel_list:
      - https://t.me/xxx
   save_path: tg_emails
   my_channel: xxx  # No need to configure
   forward_channel: xxxx # No need to configure
   check_interval: 28800
```

## 📂 Project Structure

```txt
├── Dockerfile          # Docker configuration file
├── LICENSE             # Project license file
├── README.md           # Project documentation
├── build.sh            # Docker build script
├── check.py            # Core logic for email checking
├── check_sched.py      # Email checking scheduler script
├── config              # Configuration directory
│   ├── config.yaml     # Main configuration file
│   └── proxies.txt     # Proxy server list
├── emails              # Directory for email lists to check
├── hotmail.py          # Hotmail-specific operations
├── main.py             # Program entry point
├── out                 # Output directory
│   ├── dead.txt        # List of invalid emails
│   ├── edu.txt         # List of .edu emails
│   ├── live.txt        # List of valid emails
│   ├── mail            # Directory for saved emails
│   └── plus.txt        # List of plus
├── requirements.txt    # Project dependencies
├── start.sh            # Project start script
├── test.session        # TG session file
├── tg_down.py          # Telegram download script
├── tg_emails           # Telegram email directory
│   ├── new
│   └── old
├── utils.py            # Utility functions module
├── zbark.py            # Bark push module
├── zpush.py            # Push module
├── zpushplus.py        # Push Plus module
└── zserverchan.py      # Server Chan module
```

## 🐳 Docker

You can also run this project using Docker:

1. Build the Docker image:

```bash
docker pull ghcr.io/rickhqh/hotmail-checker:latest
```

2. Your local directory structure should look like this:

```
docker_data/
├── config/
│   ├── config.yaml
│   └── proxies.txt
├── out/
│   ├── dead.txt
│   ├── edu.txt
│   ├── live.txt
│   ├── mail/
│   └── plus.txt
├── test.session
├── tg_emails           # Telegram email directory
│   ├── new
│   └── old
└── emails/
    └── your_email_lists.txt
```

3. If using TG mode, you need to manually enter the container to obtain the TG session:

```bash
docker exec -it hotmail-checker /bin/sh
```

```bash
cd /hotmail-checker
python tg_down.py
```

4. Run the Docker container using the following command:

```bash
docker run --name hotmail-checker -d \
   -v /root/hotmail-checker/config:/hotmail-checker/config \
   -v /root/hotmail-checker/emails:/hotmail-checker/emails \
   -v /root/hotmail-checker/out:/hotmail-checker/out \
   -v /root/hotmail-checker/tg_emails:/hotmail-checker/tg_emails \
   -v /root/hotmail-checker/test.session:/hotmail-checker/test.session \
   ghcr.io/rickhqh/hotmail-checker:latest
```

## 📝 License

This project is licensed under the [MIT License](LICENSE).

If you have any questions or suggestions, feel free to ask! 🎉
