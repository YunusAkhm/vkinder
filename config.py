user_token = '' # токен пользователя
comm_token = '' # токен сообщества

offset = 0 #сдвиг
seen_users = []
find_user_list = []
find_list = []
offset_user = 0
line = range(0, 1000) # последовательность для перебора найденных пользователей

host = '127.0.0.1' 
user = 'postgres'
password = '0000'
db_name = 'vkinder'
