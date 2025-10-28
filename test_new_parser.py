import requests
from bs4 import BeautifulSoup
import csv
import yaml
import io
from typing import List, Dict, Any, Tuple

def data_to_csv_string(titles: List[str], data: List[List[str]]) -> str:
    """Конвертирует данные в CSV строку"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(titles)
    
    # Фильтруем пустые и полностью NULL строки
    non_empty_data = []
    for row in data:
        # Проверяем, что строка не пустая и не состоит полностью из NULL
        if any(field and field != "NULL" for field in row):
            non_empty_data.append(row)
    
    writer.writerows(non_empty_data)
    
    return output.getvalue()

def parse_rule(element, rule: str, rule_name: str = "") -> str:
    """
    Парсит элемент по заданному правилу
    Формат правила: tag1:index1/tag2:index2:attribute
    """
    steps = rule.split('/')
    current_element = element
    
    for i, step in enumerate(steps):
        is_last_step = i == len(steps) - 1
        parts = step.split(':')
        
        if len(parts) < 2:
            return ""
            
        tag = parts[0]
        try:
            index = int(parts[1])
        except ValueError:
            return ""
        
        # Поиск элементов
        found_elements = current_element.find_all(tag)
        
        if not found_elements or index >= len(found_elements):
            return ""
        
        current_element = found_elements[index]
        
        # Если это последний шаг и указан атрибут
        if is_last_step and len(parts) == 3:
            attr = parts[2]
            if attr == 'text':
                text = current_element.get_text(strip=True)
                return text if text else ""
            else:
                attr_value = current_element.get(attr, "")
                return attr_value if attr_value else ""
    
    text = current_element.get_text(strip=True)
    return text if text else ""

def parse_page(config: Dict[str, Any]) -> Tuple[List[str], List[List[str]]]:
    """Парсит страницу по заданной конфигурации"""
    print(f"Начало парсинга: {config['name']}")
    print(f"URL: {config['url']}")
    
    try:
        response = requests.get(config['url'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим таблицу по указанному номеру (по умолчанию первая таблица)
        table_num = config.get('table', 1) - 1  # Конвертируем в 0-based индекс
        tables = soup.find_all('table')
        
        if not tables:
            print("Ошибка: таблицы не найдены на странице")
            return [], []
        
        if table_num >= len(tables):
            print(f"Ошибка: таблица #{table_num + 1} не найдена, на странице только {len(tables)} таблиц")
            return [], []
        
        table = tables[table_num]
        print(f"Используется таблица #{table_num + 1}")
        
        tbody = table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')
        
        print(f"Найдено строк: {len(rows)}")
        
        data = []
        valid_rows = 0
        setnull = config.get('setnull', False)
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) == 0:
                continue
            
            row_data = []
            has_valid_data = False
            
            for rule_config in config['rules']:
                rule_name = rule_config['name']
                try:
                    value = parse_rule(row, rule_config['rule'], rule_name)
                    
                    # Если значение пустое и включен setnull, заменяем на "NULL"
                    if not value and setnull:
                        value = "NULL"
                    
                    row_data.append(value)
                    
                    # Проверяем, есть ли в строке хотя бы одно валидное (не NULL и не пустое) значение
                    if value and value != "NULL":
                        has_valid_data = True
                        
                except Exception:
                    error_value = "NULL" if setnull else ""
                    row_data.append(error_value)
            
            # Добавляем строку только если в ней есть валидные данные
            if has_valid_data:
                data.append(row_data)
                valid_rows += 1
        
        # Получаем заголовки из правил
        titles = [rule['name'] for rule in config['rules']]
        
        print(f"Успешно спарсено строк: {valid_rows}")
        return titles, data

    except requests.RequestException as e:
        print(f"Ошибка HTTP запроса: {e}")
        return [], []
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге: {e}")
        return [], []

def parse_from_yml(yml_str: str) -> Dict[str, str]:
    """
    Основная функция парсинга на основе YML конфигурации
    Возвращает словарь: имя задачи -> CSV строка
    """
    print("=== Начало парсинга по YML конфигурации ===")
    result = {}
    
    try:
        configs = yaml.safe_load(yml_str)
        print(f"Найдено конфигураций: {len(configs)}")
        
        for i, config in enumerate(configs):
            print(f"\n{'='*50}")
            print(f"Обработка конфигурации {i+1}/{len(configs)}: {config['name']}")
            print(f"Setnull: {config.get('setnull', False)}")
            print(f"Table: {config.get('table', 1)}")
            print(f"{'='*50}")
            
            # Парсим страницу
            titles, data = parse_page(config)
            
            if data:
                # Конвертируем в CSV строку
                csv_string = data_to_csv_string(titles, data)
                result[config['name']] = csv_string
                print(f"✓ Успешно сгенерирован CSV для '{config['name']}'")
            else:
                print(f"❌ Не удалось получить данные для '{config['name']}'")
                result[config['name']] = ""
                
        print(f"\n{'='*50}")
        print("Парсинг завершен!")
        print(f"{'='*50}")
                
    except yaml.YAMLError as e:
        print(f"❌ Ошибка парсинга YAML: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
    
    return result

# Пример использования
if __name__ == '__main__':
    yml_config = """
- name: Parse all characters from fandom
  url: https://genshin-impact.fandom.com/wiki/Character/List
  table: 1
  setnull: true
  rules:
    - name: Name 
      rule: td:1/a:0:text
    - name: Rarity
      rule: td:2/span:0/span:0:title
    - name: Element
      rule: td:3/span:0/span:0/a:0:title
    - name: Weapon
      rule: td:4/span:0/span:0/a:0:title
    - name: Region
      rule: td:5/span:0/a:0:title
- name: Parse swords
  url: https://genshin-impact.fandom.com/wiki/Sword
  table: 2
  setnull: true
  rules:
    - name: Name 
      rule: td:1/a:0:text
    - name: Rarity
      rule: td:2/span:0/span:0:title
"""
    
    # Парсим данные
    results = parse_from_yml(yml_config)
    
    # Сохраняем в файлы
    for name, csv_data in results.items():
        if csv_data:
            filename = f"{name.lower().replace(' ', '_')}.csv"
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_data)
            print(f"Сохранено в файл: {filename}")
            
            # Выводим первые несколько строк для проверки
            lines = csv_data.strip().split('\n')
            print("Первые 5 строк CSV:")
            for i in range(min(5, len(lines))):
                print(f"  {lines[i]}")