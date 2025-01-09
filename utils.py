def strToLst(str: str, sep: str = ',') -> list:
    if str is None: return None
    tmp =[]
    for i in str.split(sep):
        if i != '':
            tmp.append(i)
    return tmp

def cleanDict(data: dict) -> dict:
    """Нормализует данные в словаре:
     - заменяет пустые значение на None
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    for k,v in data.items():
        data[k] = normalizeStr(v)
        data[k] = cleanEmptyStr(v)
    return data

def normalizeStr(str: str) -> str:
    """Нормализует данные в строке:
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    str = str.replace('\t',' ')
    str = str.strip()
    while '  ' in str:
        str = str.replace('  ', ' ')
    return str

def cleanEmptyStr(str: str) -> str:
    """Pаменяет пустые строки на None"""
    return None if str == '' else str

def getSampleCSV(csvPath: str ='sample.csv') -> None:
    import csv

    with open(csvPath, 'w', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['title','author','year_start','year_end','isbns','articles','options'])

def dictToCSV(data: list, csvPath: str = "output.csv") -> None:
    """Принимает список словарей, сохраняет в CSV"""
    import csv

    if isinstance(data, list) and len(data) == 0 and isinstance(data[0], dict):
        raise ValueError("Должнен быть список словарей, и ничто другое")
    
    fieldnames = [k for k in data[0].keys()]

    with open(csvPath, 'w', newline='', encoding='utf8') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def csvToDict(csvPath) -> list:
    """Возвращает список словарей"""
    import csv
    import os

    if not os.path.exists(csvPath):
        raise FileExistsError(f'Файла ({os.path.abspath(csvPath)}) не сушествует')

    data = []

    with open(csvPath, 'r', encoding='utf8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            row = cleanDict(row)
            if row['title'] is not None:
                row['isbns'] = strToLst(row['isbns'])
                row['articles'] = strToLst(row['articles'])
                # row['options'] = strToLst(row['options'])
            data.append(row)
    
    return data

def createViewS():
    pass

def main():
    pass

if __name__  == '__main__':
    main()