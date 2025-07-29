def strToLst(string: str, sep: str = ',', replase_dots = True) -> list:
    """Преобразует строку в список, по указанному разделителю.
    Удаляет дубли
    Пропускает пустые строки"""
    if string is None: return None
    tmp = []
    string = string.replace(" ", "")
    if replase_dots:
        string = string.replace(".", sep)
    for i in string.split(sep):
        if i != '':
            item = normalizeStr(i)
            
            tmp.append(item)
    return list(set(tmp))

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
    import re
    string = re.sub(r"[^a-zA-Zа-яёА-ЯЁ0-9,.!'+-–]+", " ", string)
    # string = string.replace('\t', ' ')
    # string = string.replace('\r\n', ' ')
    # string = string.replace('\n', ' ')
    # string = string.replace('\u2009', ' ')
    # string = string.replace(' ', ' ') 
    # while '  ' in string:
    #     string = string.replace('  ', ' ')
    # string = string.strip()
    return string.strip()

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

def dictToCSV(data: list[dict], csvPath: str = "./tmp/output.csv") -> None:
    """Принимает список словарей, сохраняет в CSV"""
    import csv

    if isinstance(data, list) and len(data) == 0 and isinstance(data[0], dict):
        raise ValueError("Должнен быть список словарей, и ничто другое")
    
    fieldnames = [k for k in data[0].keys()]

    with open(csvPath, 'w', newline='', encoding='utf8') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def csvToDict(csvPath) -> list[dict]:
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

def strFromComparison(text: str) -> str:
    """Убирает из строки все кроме букв, цифр и пробелов.
    Так же нормализует"""
    import re
    # text = re.sub("ё", "е", text)
    # text = re.sub("Ё", "Е", text)
    # text = re.sub("[^a-zA-Zа-яА-Я0-9]", " ", text)
    # text = normalizeStr(text)
    # text = text.lower()
    # return text
    text = text.replace('ё', 'е').replace('Ё', 'Е')
    text = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", " ", text)
    return text.strip().lower()

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
    if haveDot and (' ' in title) and (len(title.split(' ')) > 2):
        for word in title.split(' '): 
            if word not in string:
                return False
        return True
    return False

def dictByKeys (lst: list[dict], firstKey: str, secondKey: str = None) -> dict:
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

def minPriceByKeys(lst: list[dict], firstKey='book_id', secondKey='typeSearch') -> list[dict]:
    """Принимает список словарей, делит по первому и второму ключу.
    По умолчанию ключи для словарей цен, а именно :'book_id' и 'typeSearch'.
    В словарях ОБЯЗАТЕЛЬНО должен быть ключ 'price'.
    """
    data = dictByKeys(lst, firstKey, secondKey)

    res = []
    # Отправленяем список словарей, где на один тип одного id имеется более одного словаря в min функцию
    # Результат функции и списки, где по одному словарю добавляем в возвращаемый список словарей
    for value in data.values():
        if len(value) > 1:
            mPriceItem = minPrice(value)
            if mPriceItem is not None:
                res.append(mPriceItem)
        elif len(value) == 1:
            res.extend(value)
            
    return res

def minPrice(lst: list[dict]) -> dict:
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

def uniArticleByKeys(lst: list[dict], firstKey='book_id', secondKey='article') -> list[dict]:
    """Принимает список словарей, делит по первому и второму ключу.
    По умолчанию ключи для словарей цен, а именно :'book_id' и 'article'.
    В словарях ОБЯЗАТЕЛЬНО должен быть ключ 'typeSearch'.
    """
    data = dictByKeys(lst, firstKey, secondKey)

    res = []
    # Отправленяем список словарей, где на один артикль одного id имеется более одного словаря функцию
    # Результат функции и списки, где по одному словарю добавляем в возвращаемый список словарей
    for value in data.values():
        # print(value)
        if len(value) > 1:
            uniqItem = uniqueArticle(value)
            if uniqItem is not None:
                res.append(uniqItem)
        elif len(value) == 1:
            res.extend(value)
            
    return res

def uniqueArticle(lst: list[dict]) -> dict:
    """Принимает список словарей. 
    Возвращает один словарь с уникальным article.
    Должны быть словари, содержащий как минимум:
    {'typeSearch': str}."""
    types = [item.get('typeSearch') for item in lst]
    if "article" in types:
        uniType = "article"
    elif "isbn" in types:
        uniType = "isbn"
    else:
        uniType = "text"

    for item in lst:
        if item.get('typeSearch', None) == uniType:
            return item

def getSearhData(book: dict) -> list[dict]:
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
                if opt is not None and '=' in opt:
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

def getAllData() -> list[dict]:
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

def getEnv(key=None) -> str|dict:
    """Без ключа: Возвращает словарь, с переменными из файла .env.
    С ключем: Возвращает значение переменной с именем равном ключу"""
    from dotenv import dotenv_values

    if key:
        value = dotenv_values('.env').get(key)
        if value:
            if value.isdigit():
                value = int(value)
            if value == "None":
                value = None
            return value
        return None
    return dotenv_values('.env')

def getEmail() -> list[list]:
    """Запрос писем с почты, возвращает все, от определенных отправителей.
    Возвращает список списков, начиная с самого нового, к самому старому.
    Во вложенном списке первый [0] элемент - дата и время письма, объект datetime.
    Последующие элементы - части тела письма, от одного."""
    # TODO фильтр: отправитель - озон или телефон
    import imaplib, email
    acceptFrom = ('ozzionni@gmail.com', 'mailer@sender.ozon.ru')
    email_imap = getEnv('EMAIL_IMAP')
    email_imap_port = getEnv('EMAIL_IMAP_PORT')
    email_login = getEnv('EMAIL_LOGIN')
    email_password = getEnv('EMAIL_PASSWORD')
    # if not (email_imap and email_imap_port and email_login and email_password):
    #     # print("Один или более из параметров для почты пуст")
    #     return None
    mails = []
    with imaplib.IMAP4_SSL(email_imap, port=email_imap_port) as imap:
        imap.login(email_login, email_password)
        imap.select("INBOX")
        data = imap.search(None, 'ALL')[1]
        data = data[0].split()

        for item in data:
            f_data = imap.fetch(item, "(RFC822)")[1]
            email_message = email.message_from_bytes(f_data[0][1])
            emFrom = email.utils.parseaddr(email_message['From'])[1]
            if emFrom not in acceptFrom:
                continue
            body = [
                email.utils.parsedate_to_datetime(email_message['Date']).astimezone().replace(tzinfo=None)
                ]
            if email_message.is_multipart():
                for payload in email_message.get_payload():
                    body.append(payload.get_payload(decode=True).decode('utf-8'))
            else:    
                body.append(email_message.get_payload(decode=True).decode('utf-8'))
            mails.append(body)
    return reversed(mails)

def getCodeFromEmail(timeH=0.5) -> str:
    """Возвращает код для озона из писем, за период времени, не более timeH.
    timeH - возраст письма не должен превышать этого значения, в часах"""
    def _getCodeFromHTML(body: str) -> str:
        """Поиск кода в письме html версткой"""
        import bs4
        soup = bs4.BeautifulSoup(body, 'html.parser')
        res = soup.find('td', string=re.compile('([0-9]{6})'))
        if res is not None:
            return normalizeStr(res.text)

    import re
    from datetime import timedelta, datetime
    dtnow = datetime.now()
    mails = getEmail()
    # if not mails:
    #     return None
    for mail in mails:
        if dtnow - mail[0] > timedelta(hours=timeH):
            continue
        for row in mail[1:]:
            if "Оповещение системы безопасности" in row:
                continue
            if '<!DOCTYPE html' in row:
                return  _getCodeFromHTML(row)
            else:
                return re.search( '[0-9]{6}', normalizeStr(row) ).group()


def getListFiles(searchtype: int = None, path: str = './graphics', filetype: str = '.png') -> list[str]:
    """0 - Таблицы цен, 
    1 - Общий график, 
    2 - отдельные графики по книгам.
    Любое другое - вернет все filetype."""
    import os
    files = os.listdir(path)
    files.sort()
    if searchtype == 0:
        return [f"{path}/{file}" for file in files if ("aBooksTable" in file) and (filetype in file)]
    elif searchtype == 1:
        return [f"{path}/{file}" for file in files if ("allbooks" in file) and (filetype in file)]
    elif searchtype == 2:
        return [f"{path}/{file}" for file in files if ('b' == file[0]) and ("allbooks" not in file) and ("aBooksTable" not in file) and (filetype in file)]
    else:
        return [f"{path}/{file}" for file in files if filetype in file]

def main():
    pass

if __name__  == '__main__':
    main()