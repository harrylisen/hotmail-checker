# 🔥 Hotmail Checker

This project is a powerful email checker, mainly used to verify the validity of Hotmail accounts and detect .edu email addresses. 🚀

## 🌟 Features

- 🕵️ Check if Hotmail email addresses are valid
- 🎓 Detect .edu email addresses
- 💾 Save checked emails
- 📢 Support multiple notification methods (Bark, Push Plus, Server Chan)
- 🚀 Use proxies for checking, improving efficiency
- ⚙️ Support custom thread count to speed up checking
- 📊 Provide detailed statistics
- 🐳 Support Docker deployment

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

3. Launch:

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

push:
  type: bark  # Notification type, options: bark, pushplus, serverchan
  token: # Notification token
```

## 📂 Project Structure 

```txt
├── Dockerfile          # Docker configuration file
├── LICENSE             # Project license file
├── README.md           # Project documentation
├── build.sh            # Docker build script
├── check.py            # Core logic for email checking
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
└── utils.py            # Utility functions module
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
└── emails/
    └── your_email_lists.txt
```

3. Run the Docker container:

```bash
docker run --name hotmail-checker -d \
   -v /root/hotmail-checker/config:/hotmail-checker/config \
   -v /root/hotmail-checker/emails:/hotmail-checker/emails \
   -v /root/hotmail-checker/out:/hotmail-checker/out \
   ghcr.io/rickhqh/hotmail-checker:latest
```



## 📝 License

This project is licensed under the [MIT License](LICENSE).

If you have any questions or suggestions, feel free to ask! 🎉
