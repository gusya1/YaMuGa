import configparser


class Settings:

    def __init__(self):
        self.discord_token = None
        self.yandex_token = None

    def read_settings(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        self.discord_token = config['discord']['token']
        self.yandex_token = config['yandex']['token']
