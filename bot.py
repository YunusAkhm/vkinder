from keyboard import sender
from main import *
from database import *


def max_user(offset):
    offset_user = offset
    fet_users = fetchall_user()
    for i in fet_users:
        find_list.append({'first_name': i[1], 'last_name': i[2], 'vk_id': i[3], 'vk_link': i[4]})
    user_list = bot.find_user(user_id)
    for i in user_list:
        null = 0
        for x in find_list:
            if i == x:
                null += 1
        if null == 0:
            find_list.append(i)
    fetchall_seen_users = fetchall_seen_user()
    for i in fetchall_seen_users:
        seen_users.append({'vk_id': i[1], 'offset': offset_user})
        offset_user += 1
    return offset_user, seen_users, find_list

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())

        if request == 'начать поиск':
            creating_database()
            find_user_list = bot.name(user_id)
            offset_user, seen_users, find_list = max_user(offset_user)
            bot.write_msg(user_id, f'Привет, {find_user_list["first_name"]}')
            bot.write_msg(event.user_id, f'Нашёл для тебя пару, жми на кнопку "Вперёд"')
            find_person = bot.find_persons(user_id, offset, find_list, seen_users)
            while find_person == False:
                offset += 1
                find_person = bot.find_persons(user_id, offset, find_list, seen_users)
            seen_users.append({'vk_id': find_person['vk_id'], 'offset': offset_user})
            offset_user += 1

        elif request == 'вперёд':
            for i in line:
                offset += 1
                if offset >= len(find_person):
                    offset_user, seen_users, find_list = max_user(offset_user)
                find_person = bot.find_persons(user_id, offset, find_list, seen_users)
                while find_person == False:
                    offset += 1
                    find_person = bot.find_persons(user_id, offset, find_list, seen_users)
                seen_users.append({'vk_id': find_person['vk_id'], 'offset': offset_user})
                offset_user += 1
                break
        elif request == 'стоп':
            for i in find_list:
                insert_data_users(i['first_name'], i['last_name'], i['vk_id'], i['vk_link'])
            for i in seen_users:
                insert_data_seen_users(i['vk_id'], str(i['offset']))
            exit()
        else:
            bot.write_msg(event.user_id, 'Твоё сообщение непонятно')