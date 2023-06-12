import requests

def api_request(method_endswith, params, method_type):
    """
    функция для запроса к API
    :param method_endswith: конкретный запрос к API
    :param params: параметры запроса - ключи и значения
    :param method_type: метод get или post
    :return: функцию запроса к API - GET/POST
    """
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

    # В зависимости от типа запроса вызываем соответствующую функцию
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    else:
        return post_request(
            url=url,
            params=params
        )


def get_request(url, params):
    """запрос к API для извлечения данных по указанному URL и с нужными параметрами"""
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.Timeout:
        return f"Нет ответ от сервера. Попробуйте повторить запрос"
    except requests.exceptions.RequestException:
        return f"Ошибка запроса. Необходимо повторить запрос"

def post_request(url, params):
    """запрос к API с отправкой данных по указанному URL и с нужными параметрами
    получение данных с сервера"""
    try:
        response = requests.post(
            url,
            params=params,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=10
        )
    except requests.exceptions.Timeout:
        return f"Нет ответ от сервера. Попробуйте повторить запрос"
    except requests.exceptions.RequestException:
        return f"Ошибка запроса. Необходимо повторить запрос"

def city_request(city):
    city_data = api_request("locations/v3/search", {"q": city, "locale": "ru_RU"}, 'GET')
    cities = dict()
    print(city_data['sr'])
    for city in city_data['sr']:
        if city['type'] == "CITY":
            city_id = city['gaiaId']
            city_name = city['regionNames']['fullName']
            cities[city_name] = city_id
        else:
            continue

    return cities

get_id_url = "locations/v3/search"
req_hotel_prop = "properties/v2/list"
req_hotel_prop_detailed = "properties/v2/detail"