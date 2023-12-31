import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from config import user_token, comm_token



class VKBot:
    def __init__(self):
        print("Bot was created")
        self.vk = vk_api.VkApi(token=comm_token)  # АВТОРИЗАЦИЯ СООБЩЕСТВА
        self.longpoll = VkLongPoll(self.vk)  # РАБОТА С СООБЩЕНИЯМИ

    def write_msg(self, user_id, message):
        """МЕТОД ДЛЯ ОТПРАВКИ СООБЩЕНИЙ"""
        self.vk.method(
            "messages.send",
            {"user_id": user_id, "message": message, "random_id": randrange(10**7)},
        )

    def name(self, user_id):
        """ПОЛУЧЕНИЕ ИМЕНИ ПОЛЬЗОВАТЕЛЯ, КОТОРЫЙ НАПИСАЛ БОТУ"""
        url = f"https://api.vk.com/method/users.get"
        params = {
            "access_token": user_token,
            "user_ids": user_id,
            "fields": "sex,bdate,city",
            "v": "5.131",
        }
        repl = requests.get(url, params=params)
        response = repl.json()
        user_information = {}
        try:
            information_list = response["response"]
        except KeyError:
            print(
                user_id,
                "Ошибка получения токена, введите токен в переменную - user_token",
            )

        for i in information_list:
            for key, value in i.items():
                first_name = i.get("first_name")
        user_information["first_name"] = first_name

        # """ПОЛУЧЕНИЕ ПОЛА ПОЛЬЗОВАТЕЛЯ, МЕНЯЕТ НА ПРОТИВОПОЛОЖНЫЙ"""
        for i in information_list:
            if i.get("sex") == 2:
                find_sex = 1
            elif i.get("sex") == 1:
                find_sex = 2
        user_information["find_sex"] = find_sex

        # """ПОЛУЧЕНИЕ ВОЗРАСТА ПОЛЬЗОВАТЕЛЯ ИЛИ НИЖНЕЙ ГРАНИЦЫ ДЛЯ ПОИСКА"""
        # """ПОЛУЧЕНИЕ ВОЗРАСТА ПОЛЬЗОВАТЕЛЯ ИЛИ ВЕРХНЕЙ ГРАНИЦЫ ДЛЯ ПОИСКА"""
        for i in information_list:
            date = i.get("bdate")
        date_list = date.split(".")
        if len(date_list) == 3:
            year = int(date_list[2])
            year_now = int(datetime.date.today().year)
            min_age = year_now - year
        elif len(date_list) == 2 or date not in information_list:
            self.write_msg(user_id, "Введите нижний порог возраста (min - 16): ")
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    min_age = event.text
        user_information["min_age"] = min_age

        # """ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ГОРОДЕ ПОЛЬЗОВАТЕЛЯ"""
        for i in information_list:
            if "city" in i:
                city = i.get("city")
                id = str(city.get("id"))
            elif "city" not in i:
                self.write_msg(user_id, "Введите название вашего города: ")
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city_name = event.text
                        id_city = self.cities(user_id, city_name)
                        if id_city != "" or id_city != None:
                            id = str(id_city)
                        else:
                            break
        user_information["id"] = id
        return user_information

    # @staticmethod
    def cities(self, user_id, city_name):
        """ПОЛУЧЕНИЕ ID ГОРОДА ПОЛЬЗОВАТЕЛЯ ПО НАЗВАНИЮ"""
        url = url = f"https://api.vk.com/method/database.getCities"
        params = {
            "access_token": user_token,
            "country_id": 1,
            "q": f"{city_name}",
            "need_all": 0,
            "count": 1000,
            "v": "5.131",
        }
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response["response"]
        except KeyError:
            print(user_id, "Ошибка получения токена")
        list_cities = information_list["items"]
        for i in list_cities:
            found_city_name = i.get("title")
            if found_city_name == city_name:
                found_city_id = i.get("id")
                return int(found_city_id)

    def find_user(self, user_id):
        """ПОИСК ЧЕЛОВЕКА ПО ПОЛУЧЕННЫМ ДАННЫМ"""
        self.find_user_list = self.name(user_id)
        url = f"https://api.vk.com/method/users.search"
        params = {
            "access_token": user_token,
            "v": "5.131",
            "sex": self.find_user_list["find_sex"],
            "age_from": self.find_user_list["min_age"],
            "age_to": self.find_user_list["min_age"],
            "city": self.find_user_list["id"],
            "fields": "is_closed, id, first_name, last_name",
            "status": "1" or "6",
            "count": 500,
        }
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        try:
            dict_1 = resp_json["response"]
        except KeyError:
            print(user_id, "Ошибка получения токена")
        list_1 = dict_1["items"]
        find_list = []
        for person_dict in list_1:
            if person_dict.get("is_closed") == False:
                first_name = person_dict.get("first_name")
                last_name = person_dict.get("last_name")
                vk_id = str(person_dict.get("id"))
                vk_link = "vk.com/id" + str(person_dict.get("id"))
                user_dict = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "vk_id": vk_id,
                    "vk_link": vk_link,
                }
                find_list.append(user_dict)
            else:
                continue
        return find_list

    def get_photos_id(self, user_id):
        """ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ С РАНЖИРОВАНИЕМ В ОБРАТНОМ ПОРЯДКЕ"""
        url = "https://api.vk.com/method/photos.getAll"
        params = {
            "access_token": user_token,
            "type": "album",
            "owner_id": user_id,
            "extended": 1,
            "count": 25,
            "v": "5.131",
        }
        resp = requests.get(url, params=params)
        dict_photos = dict()
        resp_json = resp.json()
        try:
            dict_1 = resp_json["response"]
        except KeyError:
            print(user_id, "Ошибка получения токена")
        list_1 = dict_1["items"]
        for i in list_1:
            photo_id = str(i.get("id"))
            i_likes = i.get("likes")
            if i_likes.get("count"):
                likes = i_likes.get("count")
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        return list_of_ids

    def get_photo_1(self, user_id):
        """ПОЛУЧЕНИЕ ID ФОТОГРАФИИ № 1"""
        list = self.get_photos_id(user_id)

        item = 1
        photo_list = []
        while item <= 4:
            count = 1
            for i in list:
                count += 1
                if count == item:
                    photo_list.append(i[1])
            item += 1
        return photo_list

    def send_photo_1(self, user_id, offset, id):
        """ОТПРАВКА ПЕРВОЙ ФОТОГРАФИИ"""
        photo_list = self.get_photo_1(id)
        number = 1
        for i in photo_list:
            message = "Фото номер " + str(number)
            self.vk.method(
                "messages.send",
                {
                    "user_id": user_id,
                    "access_token": user_token,
                    "message": message,
                    "attachment": f"photo{id}_{i}",
                    "random_id": 0,
                },
            )
            number += 1

    def find_persons(self, user_id, offset, user_list, seen_users):
        list = user_list
        seen_user = seen_users
        tuple_person = list[offset]
        sum = 0
        for i in seen_user:
            if i["vk_id"] == tuple_person["vk_id"]:
                sum += 1
        if sum == 0:
            self.write_msg(
                user_id,
                f'{tuple_person["first_name"]} {tuple_person["last_name"]}, ссылка - {tuple_person["vk_link"]}',
            )
            if self.get_photo_1(str(tuple_person["vk_id"])) != None:
                self.send_photo_1(user_id, offset, str(tuple_person["vk_id"]))
            else:
                self.write_msg(user_id, f"Больше фотографий нет")
            return tuple_person
        else:
            return False

    def person_id(self, user_list, offset):
        list = user_list
        tuple_person = list[offset]
        return str(tuple_person["vk_id"])


bot = VKBot()
