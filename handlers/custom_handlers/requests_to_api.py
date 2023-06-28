from typing import Dict
import json
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
        if response.status_code == requests.codes.ok:
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
            json=params,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=10
        )

        if response.status_code == requests.codes.ok:
            return response

    except requests.exceptions.Timeout:
        return f"Нет ответ от сервера. Попробуйте повторить запрос"
    except requests.exceptions.RequestException:
        return f"Ошибка запроса. Необходимо повторить запрос"

def city_request(city):
    city_data = api_request(get_id_url, {"q": city, "locale": "ru_RU"}, 'GET')
    cities = dict()
    if city_data["sr"] is not None:
        print(city_data['sr'])
        for city in city_data['sr']:
            if city['type'] == "CITY":
                city_id = city['gaiaId']
                city_name = city['regionNames']['fullName']
                cities[city_name] = city_id
            else:
                continue

        return cities
    else:
        f"Ошибка в названии города. Необходимо повторить запрос"


def get_hotel_list(cust_data):
    """запрос на список отелей"""

    price_choice = "PRICE_LOW_TO_HIGH"

    if cust_data['command'] in ['highprice', 'bestdeal']:
        price_choice = "PRICE_HIGH_TO_LOW"

    params = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {
            "regionId": f"{cust_data['city_id']}"  # id из первого запроса
        },
        "checkInDate": {
            "day": int(cust_data['check_in'][:2]),
            "month": int(cust_data['check_in'][3:5]),
            "year": int(cust_data['check_in'][-4:])
        },
        "checkOutDate": {
            "day": int(cust_data['check_out'][:2]),
            "month": int(cust_data['check_out'][3:5]),
            "year": int(cust_data['check_out'][-4:])
        },
        "rooms": [
            {
                "adults": 1
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": int(cust_data['hotel_qty']),
        "sort": price_choice,
        "filters": {
            "availableFilter": "SHOW_AVAILABLE_ONLY"
        }
    }
    if cust_data['command'] == 'bestdeal':
        params = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "destination": {
                "regionId": f"{cust_data['city_id']}"  # id из первого запроса
            },
            "checkInDate": {
                "day": int(cust_data['check_in'][:2]),
                "month": int(cust_data['check_in'][3:5]),
                "year": int(cust_data['check_in'][-4:])
            },
            "checkOutDate": {
                "day": int(cust_data['check_out'][:2]),
                "month": int(cust_data['check_out'][3:5]),
                "year": int(cust_data['check_out'][-4:])
            },
            "rooms": [
                {
                    "adults": 1
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": int(cust_data['hotel_qty']),
            "sort": price_choice,
            "filters": {
                "price": {
                    "max": cust_data['max_price'],
                    "min": cust_data['min_price']
                },
                "availableFilter": "SHOW_AVAILABLE_ONLY"
            }
        }

    hotel_list = api_request(
        method_endswith=req_hotel_prop,
        params=params,
        method_type="POST"
    )
    # print(hotel_list.json())
    return hotel_list.json()

def get_hotel_details(hotel_id):
    """запрос на подробную информацию об отеле"""

    hotel_details = api_request(
        method_endswith=req_hotel_prop_detailed,
        params={
    "currency": "USD",
    "eapid": 1,
    "locale": "ru_RU",
    "siteId": 300000001,
    "propertyId": f"{hotel_id}"
    },
        method_type='POST'
    )
    return hotel_details.json()



get_id_url = "locations/v3/search"
req_hotel_prop = "properties/v2/list"
req_hotel_prop_detailed = "properties/v2/detail"