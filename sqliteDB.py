import sqlite3

def createDB(dbname="ozon-books2.db"):
    connect = sqlite3.connect(dbname)
    cursor = connect.cursor()

    try:
        with connect: 
            # Таблица с книгами: 
            # название, автор, год первого тиража и год последнего (если известно) 
            # и нужно ли смотреть по более точным параметрам: isbn, артикль, продовец, издательство
            cursor.execute("""CREATE TABLE IF NOT EXISTS bookS
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            author TEXT,
                            year_start INTEGER,
                            year_end INTEGER,
                            publisher TEXT,
                            isbn_bool INTEGER, 
                            article_bool INTEGER,
                            seller_bool INTEGET)
                            """)
            
            # Таблица с цена на определенные книги, с датой и артиклем книги
            # указание "специфик" - поментка поиска по точным параметрам
            cursor.execute("""CREATE TABLE IF NOT EXISTS priceS
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            book_id INTEGER REFERENCES bookS (id) NOT NULL,
                            datetime TEXT,
                            price INTEGER,
                            article INTEGER,
                            specific_bool INTEGER,
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
            
            # Таблица id прадовцов на озон, для поиска только у них
            cursor.execute("""CREATE TABLE IF NOT EXISTS sellerS
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            seller TEXT,
                            ozon_id INTEGER NOT NULL)
                            """)

    except Exception as ex:
    #     # TODO LOG
        print(ex)
        pass

    connect.close()


def main():
    createDB()
    pass

if __name__  == '__main__':
    main()