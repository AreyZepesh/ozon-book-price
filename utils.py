def strToLst(str: str, sep: str = ',') -> list:
    if str is None: return None
    tmp =[]
    for i in str.split(sep):
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

def normalizeStr(str: str) -> str:
    """Нормализует данные в строке:
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    str = str.replace('\t',' ')
    str = str.replace('\n',' ')
    str = str.replace('\u2009',' ')
    str = str.replace(' ', ' ') 
    while '  ' in str:
        str = str.replace('  ', ' ')
    str = str.strip()
    return str

def normalizePrice(str: str) -> int:
    """Нормализует цену, делает из строки число"""
    str = normalizeStr(str)
    str = str.replace('₸','') 
    str = str.replace('₽','') 
    str = str.replace('$','') 
    while ' ' in str:
        str = str.replace(' ', '')
    if str.isdigit():
        return int(str)
    else:
        raise TypeError(f'Опа, что то новое, цена: {str}')

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

def main():
    print(csvToDict('./csv/test.csv'))
    pass

if __name__  == '__main__':
    main()