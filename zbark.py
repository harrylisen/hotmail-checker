import requests


class BarkNotify:
    def __init__(self, token):
        self.token = token
        self.base_url = f'https://api.day.app/{token}/'

    def send_msg(self, msg_title, msg_text):
        url = f"{self.base_url}{msg_title}/{msg_text}"
        response = requests.get(url)
        if response.status_code == 200:
            print("Bark notification sent successfully.")
        else:
            print("Failed to send Bark notification.")
        return response.json()


if __name__ == "__main__":
    TOKEN = ''
    print(BarkNotify(TOKEN).send_msg("测试标题", "测试正文"))
