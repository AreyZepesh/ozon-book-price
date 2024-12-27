import sqlite3

def createDB(dbname="ozon-books.db"):
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

def createTables(cursor):
    # Таблица id издателей на озон, книги к ней цепляются
    cursor.execute("""CREATE TABLE IF NOT EXISTS publisherS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publisher TEXT,
                    publisher_ozon_id INTEGER NOT NULL)
                    """)
    # Таблица с книгами: 
    # название, автор, год первого тиража и год последнего (если известно) 
    # и нужно ли смотреть по более точным параметрам: isbn, артикль, продовец, издательство
    cursor.execute("""CREATE TABLE IF NOT EXISTS bookS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    year_start INTEGER,
                    year_end INTEGER,
                    publisher_id INTEGER,
                    FOREIGN KEY (publisher_id) REFERENCES publisherS(id) ON DELETE SET NULL)
                    """)
                    # , isbn_bool INTEGER, article_bool INTEGER, seller_bool INTEGET)
    
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
                    isbn TEXT,
                    FOREIGN KEY (book_id) REFERENCES bookS(id) ON DELETE CASCADE)
                    """)
    
    # Таблица с артиклями книг, хотя по идее хватит и одного, но пусть
    cursor.execute("""CREATE TABLE IF NOT EXISTS articleS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    article INTEGER,
                    FOREIGN KEY (book_id) REFERENCES bookS(id) ON DELETE CASCADE)
                    """)
    
    # Таблица id продавцов на озон, для поиска только у них. А надо ли?
    cursor.execute("""CREATE TABLE IF NOT EXISTS sellerS
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller TEXT,
                    seller_ozon_id INTEGER NOT NULL)
                    """)

def createViews(cursor):
    cursor.execute("""CREATE VIEW IF NOT EXISTS books_view AS
                    SELECT bookS.id AS book_id, title, author, year_start, year_end, 
                    publisherS.publisher, 
                    publisherS.publisher_ozon_id,
                    COUNT(DISTINCT isbnS.isbn) AS have_isbn,
                    COUNT(DISTINCT articleS.article) AS have_article
                    FROM bookS
                    LEFT JOIN publisherS ON publisher_id = publisherS.id
                    LEFT JOIN isbnS ON bookS.id = isbnS.book_id
                    LEFT JOIN articleS ON bookS.id = articleS.book_id
                    GROUP BY title
                    """)
    cursor.execute(""" 
                    CREATE VIEW IF NOT EXISTS prices_view AS
                    SELECT books.title, datetime, price, article, specific
                    FROM priceS
                    LEFT JOIN books ON priceS.book_id = books.id
                    """)
                    

def insertDataTest(cursor):
        cursor.execute("""INSERT INTO isbnS (isbn,book_id,id)
                    VALUES ('966-696-368-X',1,1),
                    ('978-5-17-042767-3',1,2),
                    ('978-5-9713-5115-3',1,3)""")
        cursor.execute("""INSERT INTO publisherS (publisher_ozon_id,publisher,id)
                    VALUES (855962,'АСТ',1)""")
        cursor.execute("""INSERT INTO bookS (publisher_id,year_end,year_start,author,title,id)
                    VALUES (1,2007,2003,NULL,'Бессильные мира сего',1),
                    (NULL,NULL,NULL,'Сапковский','Свет вечный',2)
                    """)

def getISBNs(id, dbname="ozon-books.db"):
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    cursor.execute("""
                    SELECT isbn FROM isbnS
                    WHERE book_id IN (?)
                    """, (id,))
    
    isbnS = [s[0] for s in cursor.fetchall()]
    connect.close()
    return isbnS

def getARTICLEs(id, dbname="ozon-books.db"):
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    cursor.execute("""
                    SELECT article FROM articleS
                    WHERE book_id IN (?)
                    """, (id,))
    articleS = [s[0] for s in cursor.fetchall()]
    connect.close()
    return articleS

    



def main():
    createDB()
    pass

if __name__  == '__main__':
    main()