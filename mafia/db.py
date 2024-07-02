import sqlite3
from random import shuffle


def insert_player(player_id, username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}')"
    cur.execute(sql)
    con.commit()
    con.close() 

def players_amount():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_mafia_usernames():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT username FROM PLAYERS where role = 'mafia' "
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names

def all_alive():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT username FROM PLAYERS where dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data

def set_rules(players):
    game_rules = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_rules[i] = 'mafia'
    shuffle (game_rules) 
    con = sqlite3.connect("db.db") 
    cur = con.cursor()
    cur.execute(f"SELECT player_id FROM players")
    id_player = cur.fetchall()
    for rule, rove in zip(game_rules, id_player):
        sql = f"UPDATE players SET rule = '{rule}' WHERE player_id = {rove[0]}"
        cur.execute(sql)
    con.commit()
    con.close()

def get_players_roles():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data

def vote(type, username, player_id):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f'SELECT username FROM players WHERE player_id = {player_id} and dead = 0 and voted = 0')
    can_vote = cur.fetchone()
    if can_vote: 
        cur.execute(f'UPDATE players SET {type} = {type} + 1 WHERE username = "{username}"')
        cur.execute(f'UPDATE players SET voted = 1 WHERE player_id = "{player_id}"')
        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    # Выбираем за кого больше всего голосов отдала мафия
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    # Выбираем кол-во игроков за мафию, которых не убили
    cur.execute(
        f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    # Максимальное кол-во голосов мафии должно быть равно кол-ву мафии
    if max_votes == mafia_alive:
        # Получаем имя пользователя, за которого проголосовали
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        # Делаем update БД, ставим, что игрок мертв
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        con.commit()
    con.close()
    return username_killed

def citizens_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    # Выбираем большинство голосов горожан
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    # Выбираем кол-во живых горожан
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'
    # Проверяем, что только 1 человек с макс. кол-вом голосов
    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        con.commit()
    con.close()
    return username_killed

def check_winner():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    request = "SELECT COUNT(*) FROM players WHERE role = 'mafia' and dead = 0"
    cur.execute(request)
    maf_alive = cur.fetchone()[0]
    con.close()
    if maf_alive == 0:
        return "Мирные"
    
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    request = "SELECT COUNT(*) FROM players WHERE role != 'mafia' and dead = 0"
    cur.execute(request)
    mir_alive = cur.fetchone()[0]
    con.close()
    if maf_alive >= mir_alive:
        return "Мафия"

print(all_alive())