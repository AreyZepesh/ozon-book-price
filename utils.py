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
    string = string.replace('\r\n',' ')
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

def plotAllPrices(datetime_start=None, datetime_stop=None, show=False, save=True) -> None:
    """Выводит Х - даты, У - все минимальные цены по этой дате.
    Можно указать период"""
    import database, utils
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    data = database.getPrices(getTitle=True, datetime_start=datetime_start, datetime_stop=datetime_stop)
    data = utils.minPriceByKeys(data, firstKey='book_id', secondKey='datetime')
    data = utils.dictByKeys(data, firstKey='book_id')
    plt.figure(figsize=(10,5))
    min_dt = set()
    max_dt = set()
    for items in data.values():
        prices = []
        dts = []
        for item in items:
            prices.append(item.get('price'))
            dts.append(datetime.strptime(item.get('datetime'), "%Y-%m-%d %H:%M"))
        plt.plot(dts, prices)
        min_dt.add(min(dts))
        max_dt.add(max(dts))
    min_dt = min(min_dt)-timedelta(hours=2)
    max_dt = max(max_dt)+timedelta(hours=2)
    plt.title('График минимальных цен на книги')
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=100, interval_multiples=False))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().set_xlim(min_dt, max_dt)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    if show:
        plt.show()
    if save:
        plt.savefig(f"{makeDir('./graphics')}/allbooks.png")
    pass

def plotPriceByBook(book_id = 0, datetime_start=None, datetime_stop=None, show=False, save=True) -> None:
    """Выводит Х - даты, У - все цены по типу на книгу по этой дате.
    Можно указать период"""
    import database, utils
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    data = database.getPrices(book_id=book_id, getTitle=True, datetime_start=datetime_start, datetime_stop=datetime_stop)
    data = utils.dictByKeys(data, firstKey='book_id')
    for items in data.values():
        prices = {'text': list(), 'isbn': list(), 'article': list()}
        dts = {'text': [], 'isbn': [], 'article': []}
        for item in items:
            prices[item.get('typeSearch')].append(item.get('price'))
            dts[item.get('typeSearch')].append(datetime.strptime(item.get('datetime'), "%Y-%m-%d %H:%M"))
        plt.figure(figsize=(10,5))
        plt.title(items[0]['book_title'])
        plt.plot(dts['text'], prices['text'], 'r--*')
        plt.plot(dts['isbn'], prices['isbn'], 'g-..')
        plt.plot(dts['article'], prices['article'], 'b-.^')

        if dts['isbn'] != []:
            plt.text(dts['isbn'][-1], prices['isbn'][-1], f'{prices['isbn'][-1]}  ', c='g', va = 'top', ha = 'right', backgroundcolor=('w',0.25))
        if dts['article'] != []:
            plt.text(dts['article'][-1], prices['article'][-1], f'{prices['article'][-1]}  ', c='b', va='bottom', ha = 'right', backgroundcolor=('w',0.25))
        if dts['text'] != []:
            plt.text(dts['text'][-1], prices['text'][-1], f' {prices['text'][-1]}  ', c='r', va='bottom', ha='left', backgroundcolor=('w',0.25))

        min_dt = min(dts['text'] + dts['isbn'] + dts['article'])-timedelta(hours=2)
        max_dt = max(dts['text'] + dts['isbn'] + dts['article'])+timedelta(hours=2)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=100, interval_multiples=False))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().set_xlim(min_dt, max_dt)
        plt.xticks(rotation=45)
        plt.grid(True)
        
        legend = [f'Поиск по тексту', f'Поиск по isbn', f'Поиск по article']
        if prices['text'] != []:
            legend[0] +=  f", последняя цена {prices['text'][-1]}"
        if prices['isbn'] != []:
            legend[1] += f", последняя цена {prices['isbn'][-1]}"
        if prices['article'] != []:
            legend[2] += f", последняя цена {prices['article'][-1]}"
        plt.legend(legend)
        
        plt.tight_layout()
        if show:
            plt.show()
        if save:
            plt.savefig(f"{makeDir('./graphics')}/{items[0].get('book_id')}.png")

def plotPriceTable():
    from matplotlib import pyplot as plt
    from database import getPriceStat

    def _genTableData(statPrices: dict) -> tuple[list[list], list[list], str]:
        """Возвращает (cells, cellsColor, dateText)"""
        #Формируем информацию под таблицей, с датами
        last_dts = set([d.pop('last_date') for d in statPrices])
        prev_dts = set([d.pop('prev_date') for d in statPrices])
        dateText = f"Последняя цена на книги от: {', '.join(last_dts)}\nПредыдущая цена книг от: {', '.join(prev_dts)}"

        # Генерим 2д списки для таблицы 
        cells = [list(data.values()) for data in statPrices]

        # Переменные для цветов, список, костыль чередования строк, словарь с цветами
        cellsColor = []
        revers = False
        colours = {
                    "Azure": "#F0FFFF",
                    "Honeydew": "#F0FFF0",
                    "Snow": "#FFFAFA",
                    "Blue": "#AFEEEE",
                    "PaleGreen": "#98FB98",
                    "Yellow": "#fbee98",
                    "DarkGreen": "#32CD32",
                    "Green": "#00FF00",
                    "Rose" : "#FFE4E1"
                    }
        
        #Выставляем цвета ячеек, 2д
        for row in cells:
            # Базовые цвета
            rowColor = [colours['Honeydew'], colours['Honeydew'], colours['Snow'], colours['Blue'], colours['PaleGreen'], colours['Yellow']]
            # Чередуем цвета строк
            if not revers:
                rowColor[0] = colours['Azure']
                rowColor[1] = colours['Azure']
            revers = not revers
            # Подкрашиваем актуальную цену
            if row[2] is None:
                pass
            elif row[4] and row[2] <= row[4]:
                rowColor[2] = colours['DarkGreen']
            elif row[3] and row[2] <= row[3]:
                rowColor[2] = colours['Green']
            elif row[5] and row[2] > row[5]:
                rowColor[2] = colours['Rose']
            cellsColor.append(rowColor)

            # Если название книги длинное - перенос на другую строку, грубый вариант
            # if row[1] and len(row[1]) > 75:
            #     half = int(len(row[1])/2)
            #     row[1] = row[1][:half] + '\n' + row[1][half:]

        return (cells, cellsColor, dateText)

    cells, cellsColor, dateText = _genTableData(getPriceStat())
    # Высчитываем высоту полотна, исходя из количества строк
    plotHeight = 0.4 * len(cells)+2
    # Высота строки, в формуле +1, хотя строки на 2 больше: причина - появляется пробел между таблицами
    rowHeight = 1/(len(cells)+1)

    # Ширина колонок, в сумме желательно иметь 1, и подписи колонок
    colWidths = [0.05, 0.55, 0.1, 0.1, 0.1, 0.1]
    colLabels = ['ID', 'Название книги', 'Последняя\nцена', 'Предыдущая\nцена', 'Минимальная\nцена', 'Средняя\nцена']
    
    # Создание холста
    plt.figure(figsize=(16, plotHeight), dpi=100)

    #  Первая таблица, loc это позиция относительно свобоного места, и кроме центра эту таблицу колбасит везде
    tab = plt.table(cellText=cells, 
                    cellColours=cellsColor,
                    colWidths=colWidths,  
                    colLabels=colLabels,
                    cellLoc="center", rowLoc="center", loc="center")
    # Правим цвет ячеек и высоту строк
    cellDict = tab.get_celld()
    for y in range(len(cells[0])):
        cellDict[(0,y)].set_facecolor(cellsColor[1][0])
        for x in range(len(cells)+1):
            cellDict[(x,y)].set_height(rowHeight)

    # Тоже самое для ячейки с датами
    tab2 = plt.table(cellText=[[dateText],],cellLoc="right", rowLoc="center", loc='bottom')
    cellD = tab2.get_celld()
    cellD[(0,0)].set_height(rowHeight)
    if (len(cells)+1)%2 != 0:
        cellD[(0,0)].set_facecolor(cellsColor[0][0])
    else:
        cellD[(0,0)].set_facecolor(cellsColor[1][0])

    # Размер шрифта регулируем
    for t in [tab, tab2]:
        t.auto_set_font_size(False)
        t.set_fontsize(10)

    # Отключаем отображение оси, чуть подгоняем маштаб и сохраняем в файл
    plt.gca().set_axis_off()
    plt.tight_layout()
    plt.savefig(f"{makeDir('./graphics')}/aBooksTable.png")

def getEnv(key=None) -> str|dict:
    """Без ключа: Возвращает словарь, с переменными из файла .env.
    С ключем: Возвращает значение переменной с именем равном ключу"""
    from dotenv import dotenv_values

    if key:
        return dotenv_values('.env').get(key)
    return dotenv_values('.env')

def getEmail() -> list[list]:
    """Запрос писем с почты, возвращает все, от определенных отправителей.
    Возвращает список списков, начиная с самого нового, к самому старому.
    Во вложенном списке первый [0] элемент - дата и время письма, объект datetime.
    Последующие элементы - части тела письма, от одного."""
    # TODO фильтр: отправитель - озон или телефон
    import imaplib, email
    acceptFrom = ('ozzionni@gmail.com', 'mailer@sender.ozon.ru')
    email_login = getEnv('EMAIL_LOGIN')
    email_password = getEnv('EMAIL_PASSWORD')
    mails = []
    with imaplib.IMAP4_SSL("imap.yandex.kz", port=993) as imap:
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

    for mail in getEmail():
        if dtnow - mail[0] > timedelta(hours=timeH):
            continue
        # print(mail[0])
        for row in mail[1:]:
            if '<!DOCTYPE html' in row:
                return  _getCodeFromHTML(row)
            else:
                return re.search( '[0-9]{6}', normalizeStr(row) ).group()

    pass

def main():
    pass

if __name__  == '__main__':
    main()