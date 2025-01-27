def strToLst(string: str, sep: str = ',') -> list:
    """Преобразует строку в список, по указанному разделителю.
    Пропускает пустые строки"""
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

def cleanEmptyStr(string: str) -> str:
    """Pаменяет пустые строки на None"""
    return None if string == '' else string

def getSampleBookCSV(csvPath: str ='./tmp/sample.csv') -> None:
    """Создает пусть csv файл, с заголовками, подходящими для экспорта в БД"""
    import csv

    with open(csvPath, 'w', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['title','author','year_start','year_end','isbns','articles','options'])

def dictToCSV(data: list, csvPath: str = "./tmp/output.csv") -> None:
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
    """Возвращает список словарей, сгенерированных на основе csv файла"""
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
    """Создание представлений в БД, так как не смог решить вопрос средствами sqlalchemy.
    Нужно только для удобной работы в БД посредство браузеров БД"""
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
                            SELECT books.id AS book_id,
                                books.title AS Title,
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

def isTITLEinSTR(title: str, string: str) -> bool:
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

def dictByKeys (lst: list, firstKey: str, secondKey: str = None) -> dict:
    """Принимает список словарей, делит по первому и (если указано) второму ключам.
    Возвращает словарь с ключами  вида 'dict[firstKey]_dict[secondKey]' и значениями в виде 
    списков словарей, содержащими комбинацию значений этих ключей"""
    data = dict()
    for item in lst:
        # Генерируем имя ключа словаря, на основе указанных ключей
        if item.get(secondKey):
            name = f'{item.get(firstKey)}_{item.get(secondKey)}'
        elif item.get(firstKey):
            name = f'{item.get(firstKey)}'
        else:
            # raise ValueError(f'В словаре {item} нет указанного ключа "{firstKey}"')
            continue
        # Добавляем в новый словарь с key = name, и value по умолчанию = []
        data.setdefault(name, list())
        # Значения заполняются списком словарей из исходного lst
        data[name].append(item)
    return data

def minPriceByKeys(lst: list, firstKey='book_id', secondKey='typeSearch') -> list:
    """Принимает список словарей, делит по первому и второму ключу.
    По умолчанию ключи для словарей цен, а именно :'book_id' и 'typeSearch'.
    В словарях ОБЯЗАТЕЛЬНО должен быть ключ 'price'.
    """
    data = dictByKeys(lst, firstKey, secondKey)

    res = []
    # Отправленяем список словарей, где на один тип одного id более одного словаря в min функцию
    # Результат функции и списки, где по одному словарю добавляем в возврощаемый список словарей
    for value in data.values():
        if len(value) > 1:
            mPriceItem = minPrice(value)
            if mPriceItem is not None:
                res.append(mPriceItem)
        elif len(value) == 1:
            res.extend(value)
    return res

def minPrice(lst: list) -> dict:
    """Принимает список словарей. 
    Возвращает один словарь с минимальной ценой.
    Должны быть словари, содержащий как минимум:
    {'price': int}."""
    prices = [item.get('price') for item in lst if 'price' in item]
    if prices == []:
        raise ValueError('Ни в одном словаре в списке нет значения с ключем "price"')
    minPrice = min(prices)
    for item in lst:
        if item.get('price', None) == minPrice:
            return item

def getSearhData(book: dict) -> list:
    """Получение списка словарей данных, 
    для поиска и обработки полученных данных.
    Принимает словарь одной книги из database.getAllBooks():
    {title, author, year_start, year_end, isbns, articles, options}
    Возвращает список словарей {book_id, title, URL, type}.
    Словарей на книгу может быть больше одного"""
    def _articleURL(_book) -> list:
        aURLs = []
        if _book['articles']:
            for art in _book['articles']:
                URL = f"https://ozon.kz/product/{art}"
                aURLs.append({'URL': URL, 'type': 'article'})
        return aURLs

    def _isbnURL(_book, _param) -> list:
        iURLs = []
        if _book['isbns']:
            for isbn in _book['isbns']:
                URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{_param}&text={isbn}"
                iURLs.append({'URL': URL, 'type': 'isbn'})
        return iURLs

    def _parametrs(_book) -> str:
        """Генерируем дополнительные опции поиска для isbn и текста"""
        _param = str()
        if _book['year_start'] and _book['year_end']:
            releaseyear = '&releaseyear=' + str(_book["year_start"]) + '.000;' + str(_book["year_end"]) + '.000' 
            _param += releaseyear
        elif _book['year_start']:
            releaseyear ='&releaseyear=' + str(_book['year_start']) + '.000;' + str(_book['year_start']) + '.000'
            _param += releaseyear
        if _book['options']:
            for opt in _book['options']:
                if opt is not None:
                    _param = _param + '&' + opt
        return _param

    URLs = []
 
    # Определяем ограничения поиска и убираем из списка опций
    if book['options']:
        if ('onlyArticle' in book['options']) and (book['articles'] is not None):
            return _articleURL(book)
        elif ('onlyArticle' in book['options']) and (book['articles'] is  None):
            book['options'].pop(book['options'].index('onlyArticle'))

        if ('onlyISBN' in book['options']) and (book['isbns'] is not None):
            return _isbnURL(book, _parametrs(book))
        elif ('onlyISBN' in book['options']) and (book['isbns'] is None):
            book['options'].pop(book['options'].index('onlyISBN'))
    
    search_text = book['title']
    if book['author']:
        search_text = search_text + ' ' + book['author']
    search_text = search_text.replace(' ', '+')

    add_search_param = _parametrs(book)
    URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{add_search_param}&text={search_text}"
    URLs.append({'URL': URL, 'type': 'text'})
    URLs.extend( _isbnURL(book, add_search_param) )
    URLs.extend( _articleURL(book) )

    return URLs

def getAllData() -> list:
    """Данные для поиска, по всем книгам.
    Возвращает список словарей 
    {book_id, title, {URL, type}}.
    Словарей на книгу может быть больше одного"""
    import database

    allData = []
    for book in database.getAllBooks():
        data = {'book_id': book['id'], 'title': book['title'], 'URLs': []}
        data['URLs'].extend( getSearhData(book) )
        if data['URLs'] != []:
            allData.append(data)
    return allData

def toJSON(data, filePath: str = "./tmp/output.json") -> None:
    """Сохраняет данные в json"""
    import json
    with open(filePath, 'w', encoding='utf8') as file:
        json.dump(data, file)
    
def fromJSON(filePath: str = "./tmp/output.json"):
    """Возвращает данные из json"""
    import json

    with open(filePath, 'r', encoding='utf8') as file:
        data = json.load(file)
    return data

def makeDir(dirPath: str) -> str:
    """Создает папку, если её нет и возвращает ту же строку, что и вошла"""
    # убрать нафиг, и просто написатать функцию, проверяющую наличие всех необходимых папок, и в случае чего создающую их? TODO
    import os
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return dirPath

def plotAllPrices(datetime_start=None, datetime_stop=None, show=False, save=True):
    """Выводит Х - даты, У - все минимальные цены по этой дате.
    Можно указать период"""
    import database, utils
    import matplotlib.pyplot as plt
    data = database.getPrices(getTitle=True, datetime_start=datetime_start, datetime_stop=datetime_stop)
    data = utils.minPriceByKeys(data, firstKey='book_id', secondKey='datetime')
    data = utils.dictByKeys(data, firstKey='book_id')

    plt.figure(figsize=(10,5))
    for items in data.values():
        prices = []
        dts = []
        for item in items:
            prices.append(item.get('price'))
            dts.append(item.get('datetime'))
        plt.plot(dts, prices)
    plt.title('График минимальных цен на книги')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    if show:
        plt.show()
    if save:
        plt.savefig(f"{makeDir('./graphics')}/allbooks.png")
    pass

def plotPriceByBook(book_id = 0, datetime_start=None, datetime_stop=None, show=False, save=True):
    """Выводит Х - даты, У - все цены по типу на книгу по этой дате.
    Можно указать период"""
    import database, utils
    import matplotlib.pyplot as plt
    data = database.getPrices(book_id=book_id, getTitle=True, datetime_start=datetime_start, datetime_stop=datetime_stop)
    data = utils.dictByKeys(data, firstKey='book_id')
    for items in data.values():
        prices = {'text': list(), 'isbn': list(), 'article': list()}
        dts = {'text': [], 'isbn': [], 'article': []}
        for item in items:
            prices[item.get('typeSearch')].append(item.get('price'))
            dts[item.get('typeSearch')].append(item.get('datetime'))

        plt.figure(figsize=(10,5))
        plt.title(items[0]['book_title'])
        plt.plot(dts['text'], prices['text'], 'r--*')
        plt.plot(dts['isbn'], prices['isbn'], 'g-..')
        plt.plot(dts['article'], prices['article'], 'b-.^')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend(['text', 'isbn', 'article'])
        plt.tight_layout()
        if show:
            plt.show()
        if save:
            plt.savefig(f"{makeDir('./graphics')}/{items[0].get('book_id')}.png")

def main():
    plotPriceByBook()
    pass

if __name__  == '__main__':
    main()