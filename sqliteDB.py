import sqlite3
import itertools

DEFAULT_DB = "ozon-books2.db"

# Создание пустой БД
def createDB(dbname=DEFAULT_DB) -> None:
    """Создание БД по умолчанию, посредством допфункци (вызов внутри)
    происходит создание базовых таблиц и представлений"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    
    try:
        cursor.execute('BEGIN')

        createTables(cursor)
        insertDataTest(cursor)

        createViews(cursor)

        cursor.execute('COMMIT')

    except Exception as ex:
        # TODO LOG
        cursor.execute('ROLLBACK')
        raise ex
    
    finally:
        connect.commit()
        connect.close()

def createTables(cursor) -> None:
    """Создание базовых таблиц"""
    # Таблица id издателей на озон, книги к ней цепляются
    cursor.execute("""CREATE TABLE IF NOT EXISTS publisherS
                    (publisher_id INTEGER PRIMARY KEY NOT NULL UNIQUE ON CONFLICT REPLACE,
                    publisher TEXT NOT NULL UNIQUE ON CONFLICT REPLACE)
                    """)
    # Таблица с книгами: 
    # название, автор, год первого тиража и год последнего (если известно) 
    # и нужно ли смотреть по более точным параметрам: isbn, артикль, продовец, издательство
    cursor.execute("""CREATE TABLE IF NOT EXISTS bookS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    author TEXT,
                    year_start INTEGER,
                    year_end INTEGER,
                    publisher_id INTEGER,
                    FOREIGN KEY (publisher_id) REFERENCES publisherS(publisher_id) ON DELETE SET NULL)
                    """)
    
    # Таблица с ценми на найденные книги, с датой и артиклем книги
    # указание "специфик" - поментка поиска по точным параметрам
    cursor.execute("""CREATE TABLE IF NOT EXISTS priceS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    datetime TEXT,
                    price INTEGER,
                    article INTEGER,
                    specific TEXT,
                    FOREIGN KEY (book_id) REFERENCES bookS(id) ON DELETE CASCADE)
                    """)
    
    # Таблица с isbn для книг, чтоб именно их искать
    cursor.execute("""CREATE TABLE IF NOT EXISTS isbnS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    isbn TEXT UNIQUE,
                    FOREIGN KEY (book_id) REFERENCES bookS(id) ON DELETE CASCADE)
                    """)
    
    # Таблица с артиклями книг, хотя по идее хватит и одного, но пусть
    cursor.execute("""CREATE TABLE IF NOT EXISTS articleS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    article INTEGER UNIQUE,
                    FOREIGN KEY (book_id) REFERENCES bookS(id) ON DELETE CASCADE)
                    """)

def createViews(cursor) -> None:
    """Создание базовых представлений"""
    cursor.execute("""CREATE VIEW IF NOT EXISTS books_view AS
                    SELECT bookS.id AS book_id, title, author, year_start, year_end, 
                    publisherS.publisher, 
                    publisherS.publisher_id,
                    COUNT(DISTINCT isbnS.isbn) AS have_isbn,
                    COUNT(DISTINCT articleS.article) AS have_article
                    FROM bookS
                    LEFT JOIN publisherS ON bookS.publisher_id = publisherS.publisher_id
                    LEFT JOIN isbnS ON bookS.id = isbnS.book_id
                    LEFT JOIN articleS ON bookS.id = articleS.book_id
                    GROUP BY bookS.id
                    """)
    cursor.execute(""" CREATE VIEW IF NOT EXISTS prices_view AS
                    SELECT books.title, datetime, price, article, specific
                    FROM priceS
                    LEFT JOIN books ON priceS.book_id = books.id
                    """)
    cursor.execute("""CREATE VIEW IF NOT EXISTS isbns_view AS
                    SELECT bookS.id AS book_id,
                    title, author, isbnS.isbn AS isbn
                    FROM bookS
                    LEFT JOIN isbnS ON bookS.id = isbnS.book_id
                """)
    cursor.execute("""CREATE VIEW IF NOT EXISTS articles_view AS
                    SELECT bookS.id AS book_id,
                    title, author, articleS.article AS article
                    FROM bookS
                    LEFT JOIN articleS ON bookS.id = articleS.book_id
                """)


# Добавление/получение книг, isbn, артиклей, издателей
def addBook(book_data: tuple, dbname=DEFAULT_DB) -> None:
    """Добавление или обновление книги в БД"""
    # TODO ? возврат данных книги в виде словаря (для обновления класса книги)
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    
    try:
        cursor.execute('BEGIN')
        if not isinstance(book_data, tuple) or (len(book_data) != 4):
            raise ValueError("""ERROR: Книга должна быть кортежем:
                             1. с количеством значений равным 4 (четыре);
                             2. со значениями перечисленных параметров: [title, author, year_start, year_end].""")
        book_id = getBookID(book_data[0])
        if book_id == 0:
            del book_id
            cursor.execute("""INSERT INTO bookS 
                        (title, author, year_start, year_end)
                        VALUES (?, ?, ?, ?)
                        """, book_data) 
        else:
            book_data = (book_id,) + book_data
            cursor.execute("""REPLACE INTO bookS 
                        (id, title, author, year_start, year_end)
                        VALUES (?, ?, ?, ?, ?)
                        """, book_data) 
        

        cursor.execute('COMMIT')

    except Exception as ex:
        # TODO LOG
        cursor.execute('ROLLBACK')
        raise ex
    
    finally:
        connect.commit()
        connect.close()

def getAllBooks(dbname=DEFAULT_DB) -> list:
    """Получить список словарей всех книг в БД"""
    bookS = []

    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    cursor.execute("PRAGMA table_info('books_view')")
    keyList = [k[1] for k in cursor.fetchall()]
    cursor.execute('SELECT * FROM books_view')

    for book in cursor.fetchall():
        t_book = {}
        for k, v in itertools.zip_longest(keyList, book):
            t_book[k] = v
        if "have_isbn" in t_book:
            if t_book["have_isbn"] > 0:
                t_book['isbnS'] = getISBNs(t_book["book_id"], dbname)
            else:
                t_book['isbnS'] = []
        if 'have_article' in t_book:
            if t_book["have_article"] > 0:
                t_book['articleS'] = getArticles(t_book["book_id"], dbname)
            else:
                t_book['articleS'] = []

        bookS.append(t_book)
    connect.close()
    return bookS

def getBookID(title: str, dbname=DEFAULT_DB) -> int:
    """Возвращает ID книги по названию, либо 0, если книга не найдена.
    Генерирует исключение, если id больше одного, хотя поиск не может вернуть больше одного id)"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    cursor.execute("""SELECT id FROM bookS
                   WHERE title IN (?)""", (title, ))
    res = cursor.fetchall()
    connect.close()
    if len(res) == 1:
        book_id = res[0][0]
    elif len(res) == 0:
        book_id = 0
    else:
        # TODO log... а нужно ли это исключение?
        raise ValueError("ERROR: Внезапно поиск ID вернул не одно или ноль значений")
    return book_id

def addISBN(book_id: int, isbn: str, dbname=DEFAULT_DB):
    """Добавить isbn для книги (по id книги)"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    
    try:
        cursor.execute('BEGIN')
        cursor.execute("""INSERT OR REPLACE INTO isbnS
                    (book_id, isbn)
                    VALUES (?, ?)
                    """, (book_id, isbn))
        cursor.execute('COMMIT')

    except Exception as ex:
        # TODO LOG
        cursor.execute('ROLLBACK')
        raise ex
    
    finally:
        connect.commit()
        connect.close()

def getISBNs(book_id: int, dbname=DEFAULT_DB) -> list:
    """Получить список isbn книги по id"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    cursor.execute("""SELECT isbn FROM isbnS
                    WHERE book_id IN (?)
                    """, (book_id,))
    
    isbnS = [s[0] for s in cursor.fetchall()]
    connect.close()
    return isbnS

def addPublisher(publisher: str, publisher_id: int, dbname=DEFAULT_DB):
    """Добавить издательство и его id на озон. Оба значения в таблице должны быть уникальны, иначе замена"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    try:
        cursor.execute('BEGIN')

        cursor.execute("""INSERT OR REPLACE INTO publisherS
                    (publisher, publisher_id)
                    VALUES (?, ?)
                    """, (publisher.strip().upper(), int(publisher_id)))

        cursor.execute('COMMIT')

    except Exception as ex:
        # TODO LOG
        cursor.execute('ROLLBACK')
        raise ex
    
    finally:
        connect.commit()
        connect.close()

def getPublisher(publisher: str = None,  dbname=DEFAULT_DB) -> tuple: 
    """Возвощает кортеж с ID на озоне и названием издательства"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    if isinstance(publisher, int) or ( isinstance(publisher, str) and publisher.strip().isdigit() ):
        cursor.execute("""SELECT * FROM publisherS
                        WHERE publisher_id IN (?)
                        """, (int(publisher),))
    elif isinstance(publisher, str):
        cursor.execute("""SELECT * FROM publisherS
                        WHERE publisher IN (?)
                        """, (publisher.strip().upper(),))
    publisher = cursor.fetchone()
    connect.close()
    return publisher

def getAllPublishers(dbname=DEFAULT_DB) -> list:
    """Получить список всех издателей книг с их ID на озоне.
    Возвращает список кортежей (ozon_id, издательство)"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM publisherS")
    
    publisherS = [s for s in cursor.fetchall()]
    connect.close()
    return publisherS

def addArticle(book_id: int, article: str, dbname=DEFAULT_DB):
    """Добавить артикль для книги (по id книги)"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()
    
    try:
        cursor.execute('BEGIN')
        cursor.execute("""INSERT OR REPLACE INTO articleS
                    (book_id, article)
                    VALUES (?, ?)
                    """, (book_id, article))
        cursor.execute('COMMIT')

    except Exception as ex:
        # TODO LOG
        cursor.execute('ROLLBACK')
        raise ex
    
    finally:
        connect.commit()
        connect.close()
    
def getArticles(book_id: int, dbname=DEFAULT_DB) -> list:
    """Получить список артиклей книги по id"""
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    cursor.execute("""SELECT article FROM articleS
                    WHERE book_id IN (?)
                    """, (book_id,))
    articleS = [s[0] for s in cursor.fetchall()]
    connect.close()
    return articleS

def addPrice():
    # TODO как правильно? по одной или все разом? инкапсуляция или быстродействие?
    pass

def getPriceS():
    # TODO возврат цен... за дату? по книге? за период?
    pass

# Тестовые данные для БД. Вызывается в createDB
def insertDataTest(cursor):
        """Добавление данных для тестов"""
        cursor.execute("""INSERT INTO publisherS (publisher_id,publisher)
                    VALUES (855962,'АСТ')""")
        cursor.execute("""INSERT INTO isbnS (isbn,book_id,id)
                    VALUES ('966-696-368-X',1,1),
                    ('978-5-17-042767-3',1,2),
                    ('978-5-9713-5115-3',1,3)""")
        cursor.execute("""INSERT INTO bookS (publisher_id,year_end,year_start,author,title,id)
                    VALUES (855962,2007,2003,NULL,'Бессильные мира сего',1),
                    (NULL,NULL,NULL,'Сапковский','Свет вечный',2)
                    """)

def main():
    pass

if __name__  == '__main__':
    main()