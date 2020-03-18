from urllib.request import urlopen, Request
import json
import requests

from bs4 import BeautifulSoup


URL = 'https://www.mebelshara.ru/contacts'
URL_API_CITIES = 'https://www.tui.ru/api/office/cities/'


def parse_website(url):
    res = urlopen(url).read()
    soup = BeautifulSoup(res, "html.parser")

    result = []
    for city_data in soup.find_all('div', 'city-item'):
        city = city_data.find('h4', 'js-city-name').string
        for data in city_data.find_all('div', 'shop-list-item'):
            shop_name = data.find('div', 'shop-name').string
            shop_address = data.find('div', 'shop-address').string
            shop_weekends = data.find('div', 'shop-weekends').string[14:]
            latitude = data.get('data-shop-latitude')
            longitude = data.get('data-shop-longitude')
            data_shop = {
                "address": city + '. ' + shop_address,
                "latlon": [latitude, longitude],
                "name": shop_name, 
                "phones": ["8 800 551 06 10"],
                "working_hours": [shop_weekends]
            }
            result.append(data_shop)

    return result


def get_cities_id(url_api_cities):
    res = requests.get(url_api_cities)
    data_cities = res.json()

    cities_id = []
    for data_city in data_cities:
        city_id = data_city['cityId']
        cities_id.append(city_id)

    return cities_id


days_of_week_data = [{'json_key': 'workdays','ru_abbreviation': 'пн-пт'},
{'json_key': 'saturday', 'ru_abbreviation': 'сб'},
{'json_key': 'sunday', 'ru_abbreviation': 'вс'}]


def get_working_hours(tui_data, working_item):
    working_data = get_working_data(tui_data, working_item['json_key'])
    abreviation = working_item['ru_abbreviation']
    if working_data['isDayOff']:
        return f'{abreviation}: выходной'
    start_work = working_data['startStr']
    end_work = working_data['endStr']
    return f'{abreviation}: {start_work}-{end_work}'


def get_working_data(tui_data, day_of_week_key):
    return tui_data['hoursOfOperation'][day_of_week_key]


def get_data_tui(cities_id):
    result_data = []
    for city_id in cities_id:
        url_api_tui = f'https://www.tui.ru/api/office/list/?cityId={city_id}&subwayId=&hoursFrom=&hoursTo=&serviceIds=all&toBeOpenOnHolidays=false%EF%F0%E8%F7%E5%EC'
        res = requests.get(url_api_tui)
        data = res.json()
        for tui_data in data:
            address = tui_data['address']
            latlon = [tui_data['latitude'], tui_data['longitude']]
            tui_name = tui_data['name']
            first_phone = tui_data['phones'][0]['phone']
            phones = [first_phone]
            if len(tui_data['phones']) == 2:
                second_phone = tui_data['phones'][1]['phone']
                phones.append(second_phone)

            working_hours = []
            for days_of_week_item in days_of_week_data:
                working_hours.append(get_working_hours(tui_data, days_of_week_item))
            
            data_tui = {
                "address": address,
                "latlon": latlon,
                "name": tui_name, 
                "phones": phones,
                "working_hours": working_hours
            }
            result_data.append(data_tui)
    
    return result_data


def write_json(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def output_json(filename):
    with open(filename) as f:
        data = json.load(f)
    print(f'***{filename}', data)
#--------------------------------------task 1----------

data_parser = parse_website(URL)
write_json('task1.json', data_parser)
# output_json('task1.json')

#-------------------------------------task 2-----------

cities_id = get_cities_id(URL_API_CITIES)
data_tui = get_data_tui(cities_id)
write_json('task2.json', data_tui)
# output_json('task2.json')
