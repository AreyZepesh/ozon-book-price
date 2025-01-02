import sqliteDB

class Book:
    def __init__(self, title, author = "", year_start = "", year_end = "") -> None:
        # TODO функция издателя, исбн и артикля, получение из БД
        self.title: str = title
        self.author: str = author
        self.year_start: int = year_start
        self.year_end: int = year_end
    
    def __str__(self) -> str:
        return f"{self.title}, {self.author}, {self.year_start}, {self.year_end}"
    
    def sendToDB(self):
        sqliteDB.addBook((self.title, self.author, self.year_start, self.year_end))
        self.id = sqliteDB.getBookID(self.title)

def main():
    # Вызов класса из его модуля может привести к ошибкам имени модуля. 
    # Отсюда будет __main__.Book, а из других мест: bookClass.Book.
    pass


if __name__  == '__main__':
    main()