from telebot import TeleBot
from db import *
from time import *

TOKEN = '6406395449:AAGNuBiFfG958ut30AbF-zkJLF6Sff8f5fI'
bot = TeleBot(TOKEN)

game = False
night = False

@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играть')
    bot.send_message(message.from_user.id, 'вы добавлены в игру')
    insert_player(message.from_user.id, username=message.from_user.first_name)

@bot.message_handler(commands=["game"])
def game_start(message):
    global game
    players = players_amount()
    if players >= 5 and not game:
        set_rules(players)
        players_rules = get_players_roles()
        mafia_usernames = get_mafia_usernames()
        for players_id, role in players_rules:
            bot.send_message(players_id, text=role)
            if role == 'mafia':
                bot.send_message(players_id, text=f'Все члены мафии:\n{mafia_usernames}')
        game = True
        bot.send_message(message.chat.id, text='Игра началась!')
        return
    
    bot.send_message(message.chat.id, text='недостаточно людей!')

@bot.message_handler(commands=['kill'])
def kill(message):
    username = message.text[6:]
    users_alive = all_alive()
    spisok_mafiozi = get_mafia_usernames()
    if night == True and message.from_user.first_name in spisok_mafiozi:
        if not username in users_alive:
            bot.send_message(message.chat.id, "Такого играока нет в списке выживших")
            return

        golosovanie = vote("mafia_vote", username, message.from_user.id)

        if golosovanie:
            bot.send_message(message.chat.id, "Ваш голос учтен")

        bot.send_message(message.chat.id, "Вы больше не голосовать")
        return
    
    bot.send.message(message.chat.id, "Сейчас день. Мафия не умеет голосовать днём")

@bot.message_handler(commands=['kick'])
def kick(message):
    username = message.text[6:]
    users_alive = all_alive()
    if night == False:
        if not username in users_alive:
            bot.send_message(message.chat.id, "Такого играока нет в списке выживших")
            return

        golosovanie = vote("citizen_vote", username, message.from_user.id)

        if golosovanie:
            bot.send_message(message.chat.id, "Ваш голос учтен")

        bot.send_message(message.chat.id, "Вы больше не голосовать")
        return
    
    bot.send.message(message.chat.id, "Сейчас ночь. Мирные не умеет голосовать ночью")


def get_killed(night):
    if not night:
        username_killed = citizens_kill()
        return f'Горожане выгнали: {username_killed}'
    username_killed = mafia_kill()
    return f'Мафию убила: {username_killed}'

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, "ДОбро пожаловать в игру! Вам даётся 1 минута, чтобы познакомится")
    sleep(60)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(message.chat.id, "Город засыпает, мафия просыпается. Наступила ночь")
        else:
            bot.send_message(message.chat.id, "Город просыпается, наступило утро")

        winner = check_winner()
        if winner == 'Мафия' or winner == "Мирные":
            game = False
            bot.send_message(message.chat.id, text=f"Игра окончена победили: {winner}")
            return
        
        night = not night
        alive = all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, text=f"В игре:\n{alive}")
        sleep(60)


if __name__ == "__main__":
    bot.polling(none_stop=True)