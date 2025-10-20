import requests
from bs4 import BeautifulSoup
import csv


def save_to_csv(titles, data, filename='parsed_data.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(titles)
        writer.writerows(data)


def parse_characters(data, rows):
    for i, row in enumerate(rows):
            cells = row.find_all(['td'])
            if len(cells) == 0:
                continue
            region = None
            try:
               region = cells[5].find('span').find('a')['title']
            except:
                region = "None"
            element = None
            try:
                element = cells[3].find('span').find('span').find('a')['title']
            except:
                element = "None"
            data.append(
                [
                    cells[1].find('a').text,
                    cells[2].find('span').find('span')['title'],
                    element,
                    cells[4].find('span').find('span').find('a')['title'],
                    region
                ]
            )

def parse_weapons(data, rows):
    for i, row in enumerate(rows):
        cells = row.find_all(['td'])
        if len(cells) == 0:
            continue
        data.append(
            [
                cells[1].find('a').text,
                cells[2].find('span').find('span')['title']
            ]
        )

def parse(parser,table_num,endpoint):
    try:
        response = requests.get("https://genshin-impact.fandom.com/wiki"+endpoint)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        first_table = soup.find_all('table')[table_num-1]
        tbody = first_table.find('tbody')
        rows = tbody.find_all('tr')
        print(f"Найдено строк: {len(rows)}")
        data = []
        parser(data,rows)
        return data


    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")



if __name__ == '__main__':
    save_to_csv(['Name', 'Rarity', 'Element', 'Weapon', 'Region'],parse(parse_characters, 1, "/Character/List"),'characters.csv')
    save_to_csv(['Name', 'Rarity'],parse(parse_weapons, 3, "/Sword"),'swords.csv')
    save_to_csv(['Name', 'Rarity'],parse(parse_weapons, 2, "/Claymore"),'claymores.csv') 
    save_to_csv(['Name', 'Rarity'],parse(parse_weapons, 2, "/Polearm"),'polearms.csv')   
    save_to_csv(['Name', 'Rarity'],parse(parse_weapons, 3, "/Catalyst"),'catalysts.csv') 
    save_to_csv(['Name', 'Rarity'],parse(parse_weapons, 2, "/Bow"),'bows.csv') 

