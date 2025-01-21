def strToLst(string: str, sep: str = ',') -> list:
    if string is None: return None
    tmp =[]
    for i in string.split(sep):
        if i != '':
            tmp.append(normalizeStr(i))
    return tmp

def cleanDict(data: dict) -> dict:
    """Нормализует данные в словаре:
     - заменяет пустые значение на None
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    for k in data.keys():
        data[k] = normalizeStr(data[k])
        data[k] = cleanEmptyStr(data[k])
    return data

def normalizeStr(string: str) -> str:
    """Нормализует данные в строке:
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    string = string.replace('\t',' ')
    string = string.replace('\n',' ')
    string = string.replace('\u2009',' ')
    string = string.replace(' ', ' ') 
    while '  ' in string:
        string = string.replace('  ', ' ')
    string = string.strip()
    return string

def normalizePrice(string: str) -> int:
    """Нормализует цену, делает из строки число"""
    return int("".join(c for c in string if  c.isdecimal()))
    # string = normalizeStr(string)
    # string = string.replace('₸','') 
    # string = string.replace('₽','') 
    # string = string.replace('$','') 
    # while ' ' in string:
    #     string = string.replace(' ', '')
    # if string.isdigit():
    #     return int(string)
    # else:
    #     raise TypeError(f'Опа, что то новое, цена: {string}')

def cleanEmptyStr(string: str) -> str:
    """Pаменяет пустые строки на None"""
    return None if string == '' else string

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
            data.append(row)
    
    return data

def createViewS(dbname: str) -> None:
    import sqlite3
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    try:
        cursor.execute('BEGIN')

        cursor.execute("""CREATE VIEW IF NOT EXISTS books_view AS
                            SELECT books.id AS book_id, 
                                title, author, year_start, year_end, options,
                                COUNT(DISTINCT isbns.isbn) AS have_isbn,
                                COUNT(DISTINCT articles.article) AS have_article
                            FROM books
                                LEFT JOIN isbns ON books.id = isbns.book_id
                                LEFT JOIN articles ON bookS.id = articles.book_id
                            GROUP BY books.id
                        """)
        cursor.execute("""CREATE VIEW IF NOT EXISTS articles_view AS
                            SELECT books.id AS book_id,
                                title, author,
                                articles.article AS article
                            FROM books
                                INNER JOIN articles ON books.id = articles.book_id;
                        """)
        cursor.execute("""CREATE VIEW IF NOT EXISTS isbns_view AS
                            SELECT books.id AS book_id,
                                title, author,
                                isbns.isbn AS isbn
                            FROM books
                                INNER JOIN isbns ON books.id = isbns.book_id;
                        """)
        cursor.execute("""CREATE VIEW price_view AS
                            SELECT books.title AS Title,
                                datetime, price, article, typeSearch
                            FROM prices
                                LEFT JOIN books ON prices.book_id = books.id
                       """)
        
        cursor.execute('COMMIT')

    except Exception as ex:
        cursor.execute('ROLLBACK')
        raise ex

    finally:
        connect.commit()
        connect.close()

def strFromComparison(string: str) -> str:
    """Убирает из строки все кроме букв, цифр и пробелов.
    Так же нормализует"""
    import re
    string = re.sub("[^a-zA-Zа-яА-Я0-9 ]", " ", string)
    string = normalizeStr(string)
    string = string.lower()
    return string

def isTITLEinSTR(title: str, string: str):
    """Проверяет вхождение title в string.
    Сперва проверяется наличие title как есть: 
    если является частью string, вернется True.
    Иначе запускается цикл, по слову из title:
    если одного из слов нет string, вернется False;
    иначе, если все слова содержатся в строке, вернется True.
    Я понимаю что такой метод оставляет возможность для ошибки.
    Для фикса этого добавил проверку наличия точки и длины title больше 2"""
    haveDot = True if "." in title else False
    title = strFromComparison(title)
    string = strFromComparison(string)
    if title in string:
        return True
    if haveDot and (' ' in title) and (len(title.strip(' ')) > 2):
        for word in title.strip(' '): 
            if word not in string:
                return False
        return True
    return False

def main():
    print(csvToDict('./csv/test.csv'))
    pass

if __name__  == '__main__':
    main()