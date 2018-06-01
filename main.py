import telebot
import json
from telebot import types
import random
from googletrans import Translator
from gtts import gTTS

def say(text):
    gTTS(text=text, lang='en').save('output.mp3')


global data
data = {}
st = """
Hello! It is a bot you can learn English with.
type /dicts to show your dictionaries. Type word to translate. You can add words to dictionaries and train words from dictionary.
"""


class Dic:
    def __init__(self, dest='en'):
        self.tr = Translator()
        self.dest = dest

    def __getitem__(self, item):
        return self.tr.translate(item, dest=self.dest).text
    
    
dic = Dic('ru')
revdic = Dic()
try:
    with open('data.dat', 'r') as f:
        data = json.loads(''.join(f.readlines()))
except:
    pass
def save():
    with open('data.dat', 'w') as f:
        f.write(json.dumps(data))
telebot.apihelper.proxy = {'https':'socks5://swcbbabh:aYEbh6q5gQ@178.32.218.16:3306'}
token="605222877:AAH6RubE3uiuBpneBQuTyWT5zI9GYf6IrvI"
bot=telebot.TeleBot(token)
def eng(word):
    return revdic[word]
    
    
@bot.message_handler(commands=['start'])
def start(msg):
    if data.get(str(msg.chat.id))==None:
        data[str(msg.chat.id)]={'dicts': [], 'status': ''}
    save()
    print('start:', msg.chat.id)
    bot.send_message(msg.chat.id,st)


@bot.message_handler(commands=['dicts'])
def dicts(msg):
    keyboard=types.InlineKeyboardMarkup()
    for i,dct in enumerate(data[str(msg.chat.id)]['dicts']):
        keyboard.add(types.InlineKeyboardButton(text=dct['name'], callback_data='dict:' + str(i)))
    keyboard.add(types.InlineKeyboardButton(text="New dict", callback_data="new_dict"))
    bot.send_message(msg.chat.id, 'Your dictionaries:', reply_markup=keyboard)
    
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat.id
    if call.data == 'new_dict':
        print('new dict creation:', chat)
        bot.send_message(chat, "Let's create new dict. What's its name?")
        data[str(chat)]['status'] = 'new_dict'
    elif call.data.split(':')[0] == 'add':
        data[str(chat)]['dicts'][int(call.data.split(':')[1])]['words'].append(call.data.split(':')[2])
        bot.send_message(chat, 'word added to dict')
    elif call.data.split(':')[0] == 'dict':
        keyboard=types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='train', callback_data='train:' + call.data.split(':')[1]))
        bot.send_message(chat, '<b>' + data[str(chat)]['dicts'][int(call.data.split(':')[1])]['name'] + '</b>\n' + str(len(data[str(chat)]['dicts'][int(call.data.split(':')[1])]['words']))+' words', reply_markup=keyboard, parse_mode='html')
    elif call.data.split(':')[0] == 'train':
        bot.send_message(chat, 'Train mode. Type exit to quit')
        r = random.choice(data[str(chat)]['dicts'][int(call.data.split(':')[1])]['words'])
        rnd = random.randint(1,3)
        if rnd == 1:
            bot.send_message(chat, '<b>' + r.split('\n')[0] + '</b>\n' + ''.join(r.split('\n')[1:]), parse_mode='html')
        elif rnd == 2:
            bot.send_message(chat, '<b>' + revdic[r.split('\n')[0]] + '</b>', parse_mode='html')
        else:
            say(r.split('\n')[0])
            with open('output.mp3', 'rb') as f:
                bot.send_voice(chat, f)
        data[str(chat)]['status'] = 'train:'+ call.data.split(':')[1] + ':' + r.split('\n')[0]
        
        
@bot.message_handler()
def ans(msg):
    chat = msg.chat.id
    if data[str(chat)]['status'] == 'new_dict':
        print('new dict name', chat)
        data[str(chat)]['dicts'].append({'name': msg.text, 'words': []})
        bot.send_message(chat, 'Dict `'+msg.text+'` created')
        data[str(chat)]['status'] = ''
    elif msg.text == 'exit':
        data[str(chat)]['status'] = ''
    elif data[str(chat)]['status'].split(':')[0] == 'train':
        if eng(msg.text).lower() == data[str(chat)]['status'].split(':')[2].lower():
            bot.send_message(chat, 'yes')
        else:
            bot.send_message(chat, 'no')
        r = random.choice(data[str(chat)]['dicts'][int(data[str(chat)]['status'].split(':')[1])]['words'])
        rnd = random.randint(1,3)
        if rnd == 1:
            bot.send_message(chat, '<b>' + r.split('\n')[0] + '</b>\n' + ''.join(r.split('\n')[1:]), parse_mode='html')
        elif rnd == 2:
            bot.send_message(chat, '<b>' + revdic[r.split('\n')[0]] + '</b>', parse_mode='html')
        else:
            say(r.split('\n')[0])
            with open('output.mp3', 'rb') as f:
                bot.send_voice(chat, f)
        data[str(chat)]['status'] = 'train:'+ data[str(chat)]['status'].split(':')[1] + ':' +r.split('\n')[0]
    else:
        keyboard=types.InlineKeyboardMarkup()
        [keyboard.add(types.InlineKeyboardButton(text='add to '+dct['name'], callback_data='add:' + str(i) + ':' + eng(msg.text))) for i, dct in enumerate(data[str(msg.chat.id)]['dicts'])]
        if dic.tr.detect(msg.text).lang == 'en':
            bot.send_message(chat, dic[msg.text.lower().split('\n')[0]], reply_markup=keyboard)
        else:
            bot.send_message(chat, revdic[msg.text.lower().split('\n')[0]], reply_markup=keyboard)
    save()
                
                
bot.polling()

