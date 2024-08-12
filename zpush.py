import yaml
from zbark import BarkNotify
from zpushplus import PushPlusNotify
from zserverchan import ServerChanNotify


class Push:
    def __init__(self):
        with open('config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            self.push_type = config['push']['type']
            self.token = config['push']['token']

    def send_message(self, title, message):
        if self.push_type == 'bark':
            BarkNotify(self.token).send_msg(title, message)
        elif self.push_type == 'pushplus':
            PushPlusNotify(self.token).send_msg(title, message)
        elif self.push_type == 'serverchan':
            ServerChanNotify(self.token).send_msg(title, message)
        else:
            print("Invalid push type in config file.")


if __name__ == '__main__':
    push = Push()
    push.send_message("Test Title", "Test Message")
