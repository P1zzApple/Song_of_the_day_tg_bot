# Current version of SotD tg bot
# tg username @P1zzApple
# bot name @Cwcwcw_bot
import telebot
import random as r
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from config import bot_token, sp_client_id, sp_client_secret, sp_username
from config import uri1, uri2, uri3

# bot
bot = telebot.TeleBot(bot_token)
# auth stuff
scc = SpotifyClientCredentials(client_id=sp_client_id, client_secret=sp_client_secret)
redirect_uri = 'https://google.com/'  # idk
token_info = scc.get_access_token()
access_token = token_info['access_token']
sp = Spotify(auth=access_token)
sp_oauth = SpotifyOAuth(sp_client_id, sp_client_secret, redirect_uri, scope="playlist-modify-public", username=sp_username)
# dice
dice_side = {}
thrown = False


# time converter
def timer(time):
    n = round(time / 1000)
    m = n // 60
    s = n % 60
    if m < 10:
        m = '0' + str(m)
    if s < 10:
        s = '0' + str(s)
    return f"{m}:{s}"


# start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, могу кидать рандом песни и сохранять их в плейлисты"
                                      "\nНажми /song чтобы начать")


# register user/chat
@bot.message_handler(commands=['reg'])
def reg(message):
    from soda_db import reg
    from config import log
    type = message.chat.type
    id = message.chat.id
    bot.send_message(log, f"1.type: {type}\nid: {id}")

    if type == 'private':
        name = message.chat.username
        bot.send_message(log, text=f'2. private: {name}')
        register = reg(name, id, type)
        print(f'private reg: {name, id, type}')
        bot.send_message(message.chat.id, "Регистрация прошла успешно")
        if register is not None:
            print('register:', register)
            bot.send_message(message.chat.id, "3. Вы уже зарегистрированы")
    elif type == 'group' or 'supergroup':
        title = message.chat.title
        bot.send_message(log, text=f'2. super/group: {title}')
        register = reg(title, id, type)
        print(f'super/group {title, id, type}')
        bot.send_message(message.chat.id, "Регистрация прошла успешно")
        if register is not None:
            print(register)
            bot.send_message(message.chat.id, "3. Вы уже зарегистрированы")
    else:
        bot.send_message(id, 'idk lol')
        print(type)


@bot.message_handler(commands=['shhh'])
def regs(message):
    from soda_db import regs
    regs = regs()
    print(regs)
    for bit in regs:
        id, name, chat_id, type = bit
        bot.send_message(message.chat.id, f"{name}\n{chat_id}\n{type}")
        print(f"id: {id}\nname: {name}\nchat id: {chat_id}\ntype:{type}")


# get json from Spotify & output to tg
def song_getter(link, message):
    ans = sp.playlist_items(link)
    n = r.randint(0, len(ans['items']))
    song = ans['items'][n]['track']
    time = song['duration_ms']  # song duration
    t = timer(time)
    print(f"{song['name']} | {song['artists'][0]['name']} | {song['album']['name']}", len(ans['items']), t,
          message.chat.id, link)  # temp logs
    # print(f"photo url: {song['album']['images'][0]['url']}")
    # song message
    bot.send_photo(message.chat.id, song['album']['images'][0]['url'],
                   caption=f"Name: {ans['items'][n]['track']['name']}"
                           f"\nDuration: {t}\nArtist(s): {ans['items'][n]['track']['artists'][0]['name']}"
                           f"\nAlbum name: {ans['items'][n]['track']['album']['name']}")
    bot.send_audio(message.chat.id, song['preview_url'], caption='demo')


@bot.message_handler(commands=["song"])
def song(message):
    # random playlist
    uri = r.choice([uri1, uri2, uri3])
    print('song req:', message.chat.id)
    song_getter(uri, message)


# save to db
def msg2db(reply): # CHANGE NAME!
    black_list = ['Name: ', 'Duration: ', 'Artist(s): ', 'Album name: ']
    for i in range(0, 4):
        reply[i] = reply[i].removeprefix(black_list[i])
        print(reply[i])
    return reply


# save songs
@bot.message_handler(commands=["like"])
def like(message):
    from soda_db import save
    if message.reply_to_message:
        reply = message.reply_to_message.caption
        try:
            print('1:', reply)
            print('2:', reply.split('\n'))
            res = msg2db(reply.split('\n'))
            print(f'test:{res}')
            c_id = abs(message.chat.id)
            s = save(res, message.chat.type, c_id)
            if s is None:
                bot.send_message(c_id, 'Вероятно вы не зарегистрировались внутри бота. Нажмите /reg для регистрации')
        except AttributeError as err:
            print("Replied to wrong message\n Error is:", err)
            bot.send_message(message.chat.id, 'Ответь на сообщение с треком, чтобы сохранить его')
        bot.reply_to(message, f"{reply}\nAdded by: @{message.from_user.username}")
    else:
        bot.send_message(message.chat.id, 'Ответь на сообщение с треком, чтобы сохранить его')
    # track = ['']
    # sp.playlist_add_items('2qv0tFFkQZ5GknKkVufx6S', track)


# display saves
@bot.message_handler(commands=['saves'])
def saves(message):
    from soda_db import display
    c_id = message.chat.id
    res = display(abs(c_id))
    c = 0
    print(res)
    song_att = ''
    for song in res:
        c = c + 1
        id, name, time, artist, album = song
        song_att += f"{c}: {name} | {time} \nArtist(s): {artist} | Album name: {album}\n"
    print(song_att)
    bot.send_message(c_id, song_att)
    # bot.send_message(message.chat.id, f"{res}")


# unsave songs
@bot.message_handler(commands=['unlike'])
def unlike(message):
    from soda_db import display
    from soda_db import unsave
    num = message.text[7:]
    print()
    try:
        c_id = abs(message.chat.id)
        res = display(c_id)
        c = 0
        for song in res:
            c = c + 1
            id, name, time, artist, album = song
            print(f"{c}: {id}")
            print(song[0])
            if int(num) == c:
                unsave(id)
            # break
        print('Track deleted')
        bot.reply_to(message, f"Track was deleted")
    except ValueError as err:
        print("User didn't write song id\nError is:", err)
        bot.send_message(message.chat.id, 'Чтобы удалить трек, напиши /unsave "№ трека".\nПример: /unsave 1')


# purely for testing purposes
@bot.message_handler(commands=["test1"])
def test1(message):
    # reply = message.reply_to_message
    bot.send_message(message.chat.id, message)


# purely for testing purposes
@bot.message_handler(commands=["test2"])
def test2(message):
    print('test2')
    # question = "sos"
    # options = ['ye', '1', 'no', 'idk', 'Go']
    # bot.send_poll(chat_id=message.chat.id, question=question, options=options, is_anonymous=False)


@bot.message_handler(commands=["add_playlist"])
def add_playlist(message):
    from soda_db import adding_playlist as ap
    try:
        msg = message.text
        msg_split = msg.split(' ')
        msg2 = msg_split[1]
        print(f'test:{msg2}')
        link = msg2.split('/')
        print(link)
        if link[0] == 'https:' and link[1] == '' and link[2] == 'open.spotify.com' and link[3] == 'playlist':
            c_id = abs(message.chat.id)
            s = ap(c_id, msg2)
            if s is None:
                bot.send_message(c_id, 'Чет ошибка вышла блин')
    except AttributeError as err:
        print("add_playlist, Error is:", err)
        bot.send_message(message.chat.id, 'А3')
    bot.reply_to(message, f"Playlist Added by: @{message.from_user.username}")

    # track = ['']
    # sp.playlist_add_items('2qv0tFFkQZ5GknKkVufx6S', track)


# fix!--------------------------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=["stavka"])
def stavka(message):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    import time
    markup = InlineKeyboardMarkup()
    # Adding buttons
    buttons = [InlineKeyboardButton(str(i), callback_data=f"{i}") for i in range(1, 7)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Голосуем:", reply_markup=markup)
    time.sleep(5)
    d = bot.send_dice(message.chat.id)
    dice_side[message.chat.id] = d.dice.value
    thrown = True


# fix!--------------------------------------------------------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data in [str(i) for i in range(1, 7)])
def callback_query(call):
    user_selection = int(call.data)
    dice_value = dice_side.get(call.message.chat.id)
    while thrown is False:
        if dice_value is not None:
            if user_selection == dice_value:
                bot.answer_callback_query(call.id, f"Поздравляем! Вы угадали число: {dice_value}")
            else:
                bot.answer_callback_query(call.id, f"Увы, вы не угадали. Выпало число: {dice_value}")
        else:
            bot.answer_callback_query(call.id, "Результат кости недоступен.")


# Spotify top songs playlist
@bot.message_handler(commands=['top_songs'])
def top_songs(message):
    p = 'https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=0af1650f4fd04c1e'
    song_getter(p, message)


'''
# Spotify daylist playlist
@bot.message_handler(commands=['daylist'])
def daylist(message):
    p = 'https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=0af1650f4fd04c1e'
    song_getter(p, message)
'''


# help n shi
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "hlep wip")
    dice = bot.send_dice(message.chat.id)
    print(dice.dice.value)  # https://open.spotify.com/playlist/37i9dQZF1DX2sQHbtx0sdt?si=47b3219874af45c9


@bot.message_handler(commands=['dice'])
def dice(message):
    dice = bot.send_dice(message.chat.id)
    print(dice.dice.value)  # https://open.spotify.com/playlist/37i9dQZF1DX2sQHbtx0sdt?si=47b3219874af45c9


'''
@bot.message_handler(commands=["hip_hop", "classic", "rock", "pop", "metal", "lo_fi"])
def rap(message):
    lol = 5
    idk = lol
    bot.send_message(message.chat.id, "wip")
# hip-hop, rock, jazz
'''


bot.polling(none_stop=True)
