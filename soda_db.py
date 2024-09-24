import psycopg2
from config import host, user, password, db_name

print('soda_db in process')  # debugger alt


# create connection
def connect():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
    except Exception as e:
        print(f"Error(connect) {e}")
        return None

    return connection


# create user individual playlist table
def create_table(chat_id):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE soda_chat_{chat_id} (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    time VARCHAR(255),
                    artist VARCHAR(255),
                    album VARCHAR(255)
                ); 
                """
            )
            connection.commit()
            print(f'-----table {chat_id} created-----')
            connection.close()
    except Exception as e:
        print("Error(create_table): ", e)


# save song to tg playlist
def save(res, type, id):
    if type == 'private':
        print('save: private')
    elif type == 'group' or 'supergroup':
        print('save: group/supergroup')
    try:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                    INSERT INTO soda_chat_{str(id)} (name, time, artist, album)
                    VALUES (%s, %s, %s, %s);
                    """, (res[0], res[1], res[2], res[3])
            )
            connection.commit()
            connection.close()
        print('Save was successful')

    except Exception as e:
        print(f"Error(save) {e}")
        return None


# show tg playlist
def display(c_id):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select * from soda_chat_{c_id};
            """
        )
        res = cursor.fetchall()
        connection.close()
    print('-----saves displayed-----')
    return res


# unsave song to tg playlist
def unsave(n):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
                delete from spot_saves
                where id = {n};
                """
        )
        connection.commit()
        connection.close()
    print('unsave made')


# dev command | show reg logs
def regs():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            f"select * from soda_station;"
        )
        res = cursor.fetchall()
        connection.close()
    print('-----regs displayed-----')
    return res


# register user to db
def reg(name, id, type):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                    INSERT INTO soda_station (name, chat_id, chat_type)
                    VALUES (%s, %s, %s);
                    """, (name, id, type)
            )
            connection.commit()
            connection.close()
        print('Registration was successful')
        create_table(str(abs(id)))
        return None
    except Exception as e:
        err = e
        print("Error(reg)", e)

    return err


# adding sp playlist to db
def adding_playlist(id, link):
    if type == 'private':
        print('save_to_pl: private')
    elif type == 'group' or 'supergroup':
        print('save_to_pl: group/supergroup')
    try:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                    INSERT INTO soda_pl_test(chat_id, sp_link)
                    VALUES (%s, %s);
                    """, (id, link)
            )
            connection.commit()
            connection.close()
        print('Save was successful')
    except Exception as e:
        print(f"Error(save) {e}")
        return None


# wip, testing purpose
def get_table():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
                select * from soda_chat_123;
                """
        )
        res = cursor.fetchall()
        connection.close()
    print('-----displayed-----')
    return res
  
