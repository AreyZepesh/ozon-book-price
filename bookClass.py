import sqliteDB

class Book:
    def __init__(self, title, author = "", year_start = "", year_end = "") -> None:
        # TODO функция издателя,  получение из БД
        self.id = None
        self.setTitle(title)
        self.author: str = author
        self.year_start: int = year_start
        self.year_end: int = year_end
        self.isbnS = []
        self.articleS = []
    
    def setTitle(self, title):
        # убрать табуляции и лишние проблемы из названия, стандартизация
        title = title.strip()
        title = title.replace('\t',' ')
        while "  " in title:
            title = title.replace("  ", " ")
        self.title: str = title

    def __str__(self) -> str:
        return f"{self.title}, {self.author}, {self.year_start}, {self.year_end}"
    
    def sendToDB(self):
        sqliteDB.addBook((self.title, self.author, self.year_start, self.year_end))
        self.getID()
        if len(self.isbnS) > 0:
            pass

    def getID(self):
        self.id = sqliteDB.getBookID(self.title)
        if self.id is None or self.id == 0:
            # TODO sendToDB ???
            raise IndexError('Книга не найдена в базе')
            
    def addISBN(self, isbn):
        if self.id is not None and  self.id != 0:
            sqliteDB.addISBN(self.id, isbn)
        else:
            self.getID()
            self.addISBN(isbn)

    def addArticle(self, article):
        if self.id is not None and  self.id !=0:
            sqliteDB.addArticle(self.id, article)
        else:
            self.getID()
            self.addArticle(article)
    
    def getISBNs(self):
        if self.id is not None and  self.id !=0:
            self.isbnS = sqliteDB.getISBNs(self.id)
        else:
            self.getID()
            self.getISBNs()

    def getArticles(self):
        if self.id is not None and  self.id !=0:
            self.articleS = sqliteDB.getArticles(self.id)
        else:
            self.getID()
            self.getArticles()



def main():
    pass


if __name__  == '__main__':
    main()