import requests
from bs4 import BeautifulSoup
import json


def get_data_from_site(url):

    result = requests.get(url)
    return result

def get_data_for_2_site(result):

    json_data = result.json()
    full_list = list()
    for json_data_elem in json_data:
        data = requests.get('https://www.tui.ru/api/office/list/?cityId=' + str(json_data_elem['cityId']))
        data_in_json = data.json()
        for elem in data_in_json:            
            news = {
                "address": elem['address'],
                "latlon": [json_data_elem['latitude'], json_data_elem['longitude']],
                "name": elem['name'],
                "phones": elem['phones'],
                "working_hours": workday(elem['hoursOfOperation'])
            }
            full_list.append(news)  
    save_to_json_file(full_list, 'tui.json')

def workday(elem):

    work = '' if elem['workdays']['isDayOff'] == True else "пн-пт " + elem['workdays']['startStr'] + "-" + elem['workdays']['endStr']
    sat = '' if elem['saturday']['isDayOff'] == True else "сб " + elem['saturday']['startStr'] + "-" + elem['saturday']['endStr']
    sun = '' if elem['sunday']['isDayOff'] == True else "вс " + elem['sunday']['startStr'] + "-" + elem['sunday']['endStr']
    return [work, sat, sun]

def get_data(result):

    html = result.text
    soup = BeautifulSoup(html, 'lxml')
    address_list = soup.find('div', class_='address').find_all('div', class_='city-item')
    data_list = list()
    for item in address_list:
        try:
            address = item.find('h4').text
        except: 
            address = ''

        shop_list = item.find_all('div', class_='shop-list-item')
        for shop in shop_list:
            try:
                full_address = address + ", " + shop.find('div', class_='shop-address').text
            except:
                full_address = ''

            try:
                latlon = []
                latlon.append(shop.attrs['data-shop-latitude'])
                latlon.append(shop.attrs['data-shop-longitude'])
            except:
                latlon = ''
            
            try:
                name = soup.find('div', class_='header').find('div', class_='logo').find('a').attrs['title']
            except:
                name = ''

            try:
                phones = []
                phones.append(soup.find('div', class_='header').find('div', class_='phone-wrap').find('span').text)
            except:
                phones = []

            try:
                working_hours = []
                working_hours.append(shop.attrs['data-shop-mode1'])
                working_hours.append(shop.attrs['data-shop-mode2'])
            except:
                working_hours = []
        
            data = {
                "address": full_address,
                "latlon": latlon,
                "name": name,
                "phones": phones,
                "working_hours": working_hours
            }
            data_list.append(data)
    save_to_json_file(data_list, 'mebelshara.json')

def save_to_json_file(lst, file_name):
    
    with open(file_name, 'w', encoding='utf-8') as wf:
        json.dump(lst, wf, indent=3, ensure_ascii=False)

def main():
    
    get_data(get_data_from_site('https://www.mebelshara.ru/contacts'))
    
    get_data_for_2_site(get_data_from_site('https://www.tui.ru/api/office/cities/'))


if __name__ == '__main__':
    main()
