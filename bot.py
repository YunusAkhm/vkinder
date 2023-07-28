from keyboard import sender
from main import bot
from vk_api.longpoll import VkEventType
from database import (
    fetchall_user,
    fetchall_seen_user,
    creating_database,
    insert_data_users,
    insert_data_seen_users,
)
from config import offset, line, seen_users, find_list


def max_user(offset):
    offset_user = offset
    fetched_users = fetchall_user()
    for user in fetched_users:
        find_list.append(
            {
                "first_name": user[1],
                "last_name": user[2],
                "vk_id": user[3],
                "vk_link": user[4],
            }
        )
    user_list = bot.find_user(user_id)
    for user in user_list:
        count = 0
        for found_user in find_list:
            if user == found_user:
                count += 1
        if count == 0:
            find_list.append(user)
    fetched_seen_users = fetchall_seen_user()
    for user in fetched_seen_users:
        seen_users.append({"vk_id": user[1], "offset": offset_user})
        offset_user += 1
    return offset_user, seen_users, find_list


def bot_start(offset):
    global user_id
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = str(event.user_id)
            msg = event.text.lower()
            sender(user_id, msg.lower())

            if request == "начать поиск":
                creating_database()
                find_user_list = bot.name(user_id)
                offset_user, seen_users, find_list = max_user(offset_user)
                bot.write_msg(user_id, f'Привет, {find_user_list["first_name"]}')
                bot.write_msg(event.user_id, f'Нашёл для тебя пару, жми на кнопку "Вперёд"')
                find_person = bot.find_persons(user_id, offset, find_list, seen_users)
                while find_person == False:
                    offset += 1
                    find_person = bot.find_persons(user_id, offset, find_list, seen_users)
                seen_users.append({"vk_id": find_person["vk_id"], "offset": offset_user})
                offset_user += 1

            elif request == "вперёд":
                for _ in line:
                    offset += 1
                    if offset >= len(find_person):
                        offset_user, seen_users, find_list = max_user(offset_user)
                    find_person = bot.find_persons(user_id, offset, find_list, seen_users)
                    while find_person == False:
                        offset += 1
                        find_person = bot.find_persons(
                            user_id, offset, find_list, seen_users
                        )
                    seen_users.append(
                        {"vk_id": find_person["vk_id"], "offset": offset_user}
                    )
                    offset_user += 1
                    break
            elif request == "стоп":
                for user in find_list:
                    insert_data_users(
                        user["first_name"],
                        user["last_name"],
                        user["vk_id"],
                        user["vk_link"],
                    )
                for user in seen_users:
                    insert_data_seen_users(user["vk_id"], str(user["offset"]))
                exit()
            else:
                bot.write_msg(event.user_id, "Твоё сообщение непонятно")

bot_start(offset)