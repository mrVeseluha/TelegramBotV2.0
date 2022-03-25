import telebot
from telebot import types

from configparser import ConfigParser

import sh

from pytube import YouTube

import soco

SONOS_PLAYERS = list(soco.discover())

def read_ini(key_id):
    config = ConfigParser()
    config.read('bot.ini')
    for section in config.sections():
        for key in config[section]:
            if key == key_id:
                return config[section][key]


API_TOKEN = read_ini('api_token')

bot = telebot.TeleBot(API_TOKEN, parse_mode=None)  # You can set parse_mode by default. HTML or MARKDOWN


@bot.message_handler(commands=['get'])
def download_yuotube_video(message):
    yt = YouTube(message.text)
    st = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    st.download()
    bot.send_message(message.chat.id, f'{st.filesize:,} bytes downloaded!!!')
    video = open(st.get_file_path(), 'rb')
    bot.send_video(message.chat.id, video)
    video.close()


@bot.message_handler(commands=['sh'])
def sh_command(message):
    cmd = message.text.split(' ')[1]
    params = message.text[5 + len(cmd):]
    print(cmd, params)
    if params == '':
        out = sh.Command(cmd)().stdout
    else:
        out = sh.Command(cmd)(params).stdout or 'Done'
    bot.reply_to(message, out)

@bot.message_handler(commands=['sonos', 'soco'])
def sonos_command(message):
    cmd = message.text.split(' ')
    print(cmd, len(cmd))
    if len(cmd) > 2:
        try:
            device, cmd = SONOS_PLAYERS[int(cmd[1])], cmd[2]
        except:
            answer = 'Error!!! Try another time...'
        if cmd == 'info':
            answer = str(device.get_speaker_info())
            answer += str(device.get_current_transport_info())
            answer += str(device.get_current_track_info()['title'])
            answer += str(device.get_current_track_info()['uri'])
        elif cmd == 'play':
            answer = ''
            try:
                device.play()
            except:
                answer += 'Can not start playing!!!\n'
            answer += str(device.get_current_transport_info())
            answer += str(device.get_current_track_info()['title'])
            answer += str(device.get_current_track_info()['uri'])
        elif cmd == 'pause':
            answer = ''
            try:
                device.pause()
            except:
                answer += 'Can not pause playing!!!\n'
            answer += str(device.get_current_transport_info())
            answer += str(device.get_current_track_info()['title'])
            answer += str(device.get_current_track_info()['uri'])
        elif cmd == 'volume':
            volume = device.volume
            try:
                new_volume = int(message.text.split(' ')[3])
            except:
                new_volume = None
                answer = 'Cannot read volume value!!!'
            if new_volume:
                device.volume = new_volume
                answer = f'{device.get_speaker_info()["zone_name"]}\nFormer value of volume was: {volume}'
            else:
                answer +=f'\nActual value of volume is {volume}'
        else:
            answer = 'Command not fount!!!'
    else:
        answer = ''
        for id, zone in enumerate(SONOS_PLAYERS):
            answer += f'{id} - {zone.player_name}\n'
    bot.reply_to(message, answer)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    sender = message.from_user
    print(f'Id: {sender.id}\n'
          f'Is bot: {sender.is_bot}\n'
          f'First name: {sender.first_name}\n'
          f'Last name: {sender.last_name}\n'
          f'Username: {sender.username}\n'
          f'language_code: {sender.language_code}\n'
          f'can_join_groups: {sender.can_join_groups}\n'
          f'can_read_all_group_messages: {sender.can_read_all_group_messages}\n'
          f'supports_inline_queries: {sender.supports_inline_queries}\n')

    markup = types.ReplyKeyboardMarkup()
    buttonA = types.KeyboardButton('A')
    buttonB = types.KeyboardButton('B')
    buttonC = types.KeyboardButton('C')

    markup.row(buttonA, buttonB)
    markup.row(buttonC)

    bot.reply_to(message, "Howdy, how are you doing?", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


print('Bot started!!!')
bot.infinity_polling()
