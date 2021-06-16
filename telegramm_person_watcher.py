from telethon.sync import TelegramClient
from telethon import types
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
import os


def utc_to_local(dt):
    if time.localtime().tm_isdst:
        return dt - timedelta(seconds=time.altzone)
    else:
        return dt - timedelta(seconds=time.timezone)


@dataclass
class LastInfo:
    date_time: datetime
    status_online: bool


class TelegrammPersonWatcher:
    last_info = LastInfo

    def __init__(self, client_phone_number='me'):
        self.client_phone_number = client_phone_number

        dirName = 'telegramm'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        self.save_filename = '{}_{}.csv'.format(self.client_phone_number, datetime.now().strftime('%Y_%m_%d__%H_%M_%S'))
        self.save_filename = os.path.join(dirName, self.save_filename)

        self.last_info.date_time = datetime(1, 1, 1, 0, 0)

        with open('telegramm.info', 'r') as f:
            api_id, api_hash = [line.rstrip() for line in f]
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.client.start()

    def add_info_to_file(self, lastInfo: LastInfo):
        print('{} Update status to {}'.format(lastInfo.date_time.strftime('%Y.%m.%d %H:%M:%S'),
                                              'online' if lastInfo.status_online else 'offline'))

        append_string_1 = '{};{}'.format(lastInfo.date_time.strftime('%Y.%m.%d %H:%M:%S'),
                                         0 if lastInfo.status_online else 1)
        append_string_2 = '{};{}'.format(lastInfo.date_time.strftime('%Y.%m.%d %H:%M:%S'),
                                         1 if lastInfo.status_online else 0)

        with open(self.save_filename, 'a') as file_object:
            file_object.write(append_string_1 + '\n')
            file_object.write(append_string_2 + '\n')

    def check_update_info(self, new_datetime, status_online: bool):
        if new_datetime != self.last_info.date_time:
            self.last_info.date_time = new_datetime
            self.last_info.status_online = status_online
            self.add_info_to_file(self.last_info)

    def watch(self):
        while True:
            user_info = self.client.get_entity(self.client_phone_number)

            if isinstance(user_info.status, types.UserStatusOffline):
                new_datetime = utc_to_local(user_info.status.was_online)
                self.check_update_info(new_datetime, False)
            else:
                new_datetime = utc_to_local(user_info.status.expires) - timedelta(minutes=5)
                self.check_update_info(new_datetime, True)
            time.sleep(0.5)


if __name__ == '__main__':
    print('Run TelegrammPersonWatcher')
    telegrammPersonWatcher = TelegrammPersonWatcher('me')
    telegrammPersonWatcher.watch()
