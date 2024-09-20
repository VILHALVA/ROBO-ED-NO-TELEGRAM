import telebot
import json
import sys
import os
from TOKEN import *

bot = telebot.TeleBot(TOKEN)

def load_responses():
    with open("./WORD.json", "r", encoding="utf-8") as file:
        return json.load(file)

responses = load_responses()

def load_config():
    with open("./CONFIG.json", "r", encoding="utf-8") as file:
        return json.load(file)

config = load_config()

def check_always_respond():
    return config.get("SEMPRE", "OFF") == "ON"

def should_respond(message):
    if message.chat.type == "private":
        return True
    if check_always_respond():
        return True

    criar_enabled = config.get("CRIAR", "OFF") == "ON"
    erro_enabled = config.get("ERRO", "OFF") == "ON"

    return criar_enabled and erro_enabled or bot.get_me().username.upper() in message.text.upper()

def save_response_to_file(word, response):
    word = word.lower()
    response = response.lower()
    try:
        with open("./WORD.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    data[word] = response

    with open("./WORD.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def handle_error_mode(message):
    criar_enabled = config.get("CRIAR", "OFF") == "ON"
    erro_enabled = config.get("ERRO", "OFF") == "ON"

    if criar_enabled and erro_enabled:
        if ':' in message.text:
            word, response = map(str.strip, message.text.split(":", 1))
            save_response_to_file(word, response)
            bot.send_chat_action(message.chat.id, "typing")
            bot.reply_to(message, "😃Nova resposta adicionada com sucesso!")
            print("BOT REINICIADO!")
            bot.stop_polling()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            bot.send_chat_action(message.chat.id, "typing")
            bot.reply_to(message, "🤔Parece que essa frase não está no meu banco de dados. Por favor, envie a frase seguindo esse modelo: 'PALAVRA CHAVE': 'RESPOSTA'")
    elif not criar_enabled and erro_enabled:
        bot.send_chat_action(message.chat.id, "typing")
        bot.reply_to(message, "🤬Infelizmente, não entendo o que dizes!")

def get_start_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="🧑‍💻CRIADOR", url="https://t.me/VILHALVA100")
    button2 = telebot.types.InlineKeyboardButton(text="📢CANAL", url="https://t.me/VILHALVA100_CANAL")
    markup.add(button1, button2)
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_chat_action(message.chat.id, "typing")
    response = "😃Olá! Eu sou o ROBÔ ED!\n\n" \
               "🌚Você pode me fazer perguntas como:\n" \
               "- qual é o seu nome?\n" \
               "- como você está?\n" \
               "- o que você pode fazer?\n" \
               "- tchau..."
    
    bot.send_message(message.chat.id, response, reply_markup=get_start_markup())

@bot.message_handler(func=lambda message: should_respond(message))
def handle_message(message):
    bot.send_chat_action(message.chat.id, "typing")
    input_text = message.text.lower()
    input_text = input_text.replace(f"@{bot.get_me().username}", "", 1).strip()
    
    keyword_found = False
    for keyword, response in responses.items():
        if keyword in input_text:
            bot.reply_to(message, response)
            keyword_found = True
            break
    if keyword_found:
        return
        
    response = responses.get(input_text, "🥵Desculpe, não entendi. Tente outra pergunta!")
    if response == "🥵Desculpe, não entendi. Tente outra pergunta!":
        handle_error_mode(message)
    else:
        bot.reply_to(message, response)

@bot.my_chat_member_handler(func=lambda message: message.chat.type in ["group", "supergroup"])
def handle_added_to_group(message):
    if message.chat.type in ["group", "supergroup"]:
        handle_start(message)

if __name__ == '__main__':
    print("BOT EM EXECUÇÃO!")
    bot.infinity_polling(timeout=60)
