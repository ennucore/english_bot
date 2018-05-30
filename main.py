import telebot
import json
from telebot import types
import random


global data
data = {}
st = """
Hello! It is a bot you can learn English with.
"""
with open('dict', 'r') as f:
    dic = json.loads(f.read())
with open('revdict', 'r') as f:
    revdic = json.loads(f.read())
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
    try:
        return revdic[word.lower()]
    except:
        return word.lower()
    
    
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
        bot.send_message(chat, data[str(chat)]['dicts'][int(call.data.split(':')[1])]['name'] + '\n' + str(len(data[str(chat)]['dicts'][int(call.data.split(':')[1])]['words']))+' words', reply_markup=keyboard)
    elif call.data.split(':')[0] == 'train':
        bot.send_message(chat, 'Train mode. Type exit to quit')
        r = random.choice(data[str(chat)]['dicts'][int(call.data.split(':')[1])]['words'])
        bot.send_message(chat, r)
        data[str(chat)]['status'] = 'train:'+ call.data.split(':')[1] + ':'+r
        
        
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
        if eng(msg.text) == data[str(chat)]['status'].split(':')[2]:
            bot.send_message(chat, 'yes')
        else:
            bot.send_message(chat, 'no')
        r = random.choice(data[str(chat)]['dicts'][int(data[str(chat)]['status'].split(':')[1])]['words'])
        bot.send_message(chat, r)
        data[str(chat)]['status'] = 'train:'+ data[str(chat)]['status'].split(':')[1] + ':' +r
    else:
        keyboard=types.InlineKeyboardMarkup()
        [keyboard.add(types.InlineKeyboardButton(text='add to '+dct['name'], callback_data='add:' + str(i) + ':' + eng(msg.text))) for i, dct in enumerate(data[str(msg.chat.id)]['dicts'])]
        try:
            bot.send_message(chat, dic[msg.text.lower()], reply_markup=keyboard)
        except:
            try:
                bot.send_message(chat, revdic[msg.text.lower()], reply_markup=keyboard)
            except:
                bot.send_message(chat, 'Word not found')
                
                
bot.polling()

