from utils import makeDir, getListFiles
import os

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
    min_dt, max_dt = set(), set()
    l_dt, m_dt = None, None
    for items in data.values():
        prices, dts = list(), list()
        for item in items:
            prices.append(item.get('price'))
            dts.append(datetime.strptime(item.get('datetime'), "%Y-%m-%d %H:%M"))
        plt.plot(dts, prices)
        if not l_dt or not m_dt:
            l_dt = len(dts)
            m_dt = len(dts)
        l_dt = max(len(dts), l_dt)
        m_dt = min(len(dts), m_dt)
        min_dt.add(min(dts))
        max_dt.add(max(dts))
    min_dt = min(min_dt)-timedelta(hours=2)
    max_dt = max(max_dt)+timedelta(hours=2)

    if l_dt > 20:
        l_dt = 20

    if l_dt <= 2:
        m_dt = 0

    # print(l_dt, m_dt)

    plt.title('График минимальных цен на книги')
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=m_dt, maxticks=l_dt, interval_multiples=False))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().set_xlim(min_dt, max_dt)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    if save:
        plt.savefig(f"{makeDir('./graphics')}/allbooks.png")
    if show:
        plt.show()
    plt.close()

def plotPriceByBook(book_id = 0, datetime_start=None, datetime_stop=None, show=False, save=True) -> None:
    """Выводит Х - даты, У - все цены по типу на книгу по этой дате.
    Можно указать период"""
    import database, utils
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    data = database.getPrices(book_id=book_id, getTitle=True, datetime_start=datetime_start, datetime_stop=datetime_stop)
    data = utils.dictByKeys(data, firstKey='book_id')
    if save:
        if book_id == 0:
            for file in getListFiles(2):
                    if os.path.exists(file):
                        os.remove(file)
        else:
            file = f"./graphics/b{str(book_id).zfill(3)}.png"
            if os.path.exists(file):
                os.remove(file)
    for items in data.values():
        prices = {'text': list(), 'isbn': list(), 'article': list()}
        dts = {'text': [], 'isbn': [], 'article': []}
        legend = []
        for item in items:
            prices[item.get('typeSearch')].append(item.get('price'))
            dts[item.get('typeSearch')].append(datetime.strptime(item.get('datetime'), "%Y-%m-%d %H:%M"))
        plt.figure(figsize=(10,5))
        plt.title(items[0]['book_title'])
        if dts['text'] != []:
            plt.plot(dts['text'], prices['text'], 'r--*')
            plt.text(dts['text'][-1], prices['text'][-1], f' {prices['text'][-1]}  ', c='r', va='bottom', ha='left', backgroundcolor=('w',0.25))
            legend.append(f"Поиск по тексту, последняя цена {prices['text'][-1]}")
        if dts['isbn'] != []:
            plt.plot(dts['isbn'], prices['isbn'], 'g-..')
            plt.text(dts['isbn'][-1], prices['isbn'][-1], f'{prices['isbn'][-1]}  ', c='g', va = 'top', ha = 'right', backgroundcolor=('w',0.25))
            legend.append(f"Поиск по isbn, последняя цена {prices['isbn'][-1]}")
        if dts['article'] != []:
            plt.plot(dts['article'], prices['article'], 'b-.^')
            plt.text(dts['article'][-1], prices['article'][-1], f'{prices['article'][-1]}  ', c='b', va='bottom', ha = 'right', backgroundcolor=('w',0.25))
            legend.append(f"Поиск по article, последняя цена {prices['article'][-1]}")
        plt.grid(True)
        plt.legend(legend)

        l_dt = len(set(dts['text'] + dts['isbn'] + dts['article']))
        if l_dt > 20:
            l_dt = 20

        if l_dt <= 2:
            m_dt = 0
        else:
            m_dt = l_dt//2
        # print(len(set(dts['text'] + dts['isbn'] + dts['article'])), l_dt, set(dts['text'] + dts['isbn'] + dts['article']))

        min_dt = min(dts['text'] + dts['isbn'] + dts['article'])-timedelta(hours=2)
        max_dt = max(dts['text'] + dts['isbn'] + dts['article'])+timedelta(hours=2)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=m_dt, maxticks=l_dt, interval_multiples=False))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().set_xlim(min_dt, max_dt)
        plt.xticks(rotation=45)
        plt.tight_layout()
        if save:
            plt.savefig(f"{makeDir('./graphics')}/b{str(items[0].get('book_id')).zfill(3)}.png")
        if show:
            plt.show()
        plt.close()

def plotPriceTable(onefile=False, telegram_size = True, show=False, save=True):
    from matplotlib import pyplot as plt
    from database import getPriceStat
    if save:
        for file in getListFiles(0):
                if os.path.exists(file):
                    os.remove(file)
    def _genTableData(statPrices: dict) -> tuple[list[list], list[list], str]:
        """Возвращает (cells, cellsColor, dateText)"""
        last_dts, prev_dts = set(), set()
        cells, cellsColor = list(), list()
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
        
        for d in statPrices:
            last_dts.add(d.pop('last_date'))
            prev_dts.add(d.pop('prev_date'))
            row = list(d.values())
            # Если название книги длинное - перенос на другую строку, грубый вариант
            # Эта число примерно, вручную для ширины 11, вставляя O
            max_title = 38
            # row[0] = '00000'
            # row[1] = 'О'*max_title*3
            if row[1] and len(row[1]) > max_title*2:
                row[1] = row[1][:max_title*2]
            if row[1] and len(row[1]) > max_title:
                if '. ' in row[1]:
                    sents = row[1].split('. ') 
                    half = int(len(sents)/2)
                    half1 = '. '.join(sents[:half])
                    half2 = '. '.join(sents[half:])
                    if len(half1) <= max_title and len(half2) <= max_title:
                        row[1] = half1 + '.\n' + half2
                if (' ' in row[1]) and ('\n' not in row[1]):
                    words = row[1].split()
                    half = int(len(words)/2)
                    row[1] = ' '.join(words[:half]) + '\n' + ' '.join(words[half:])
                if '\n' not in row[1]:
                    half = int(len(row[1])/2)
                    row[1] = row[1][:half] + '\n' + row[1][half:]
                    
            cells.append(row)
            
            #Выставляем цвета ячеек, 2д
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

        if None in last_dts:
            last_dts.remove(None)
        if None in prev_dts:
            prev_dts.remove(None)

        if len(last_dts) > 1:
            last_dts = f"{min(last_dts)} - {max(last_dts)}"
        else:
            last_dts = ''.join(last_dts)
        if len(prev_dts) > 1:
            prev_dts = f"{min(prev_dts)} - {max(prev_dts)}"
        else:
            prev_dts = ''.join(prev_dts)
        dateText = f"Последние цены на книги: {last_dts}\nПредыдущие цены книг: {prev_dts}"

        return (cells, cellsColor, dateText)

    def _plotTable(cells: list[list], cellsColor: list[list], dateText: str) -> plt:
        # Высчитываем высоту полотна, исходя из количества строк
        plotHeight = 0.4 * len(cells)+2
        # Высота строки, в формуле +1, хотя строки на 2 больше: причина - появляется пробел между таблицами
        rowHeight = 1/(len(cells)+1)

        # Ширина колонок, в сумме желательно иметь 1, и подписи колонок
        colWidths = [0.05, 0.51, 0.11, 0.11, 0.11, 0.11]
        colLabels = ['ID', 'Название книги', 'Последняя\nцена', 'Предыдущая\nцена', 'Минимальная\nцена', 'Средняя\nцена']
        
        # Создание холста
        plt.figure(figsize=(11, plotHeight), dpi=100)

        #  Первая таблица, loc это позиция относительно свобоного места, и кроме центра эту таблицу колбасит везде
        tab = plt.table(cellText=cells, 
                        cellColours=cellsColor,
                        colWidths=colWidths,  
                        colLabels=colLabels,
                        cellLoc="center", rowLoc="center", loc="center")
        tab.auto_set_font_size(False)
        # Правим цвет ячеек и высоту строк
        cellDict = tab.get_celld()
        for y in range(len(cells[0])):
            cellDict[(0,y)].set_facecolor(cellsColor[1][0])
            for x in range(len(cells)+1):
                cellDict[(x,y)].set(edgecolor = "g", height = rowHeight, fontsize=12)
                cellDict[(x,y)].set_text_props(fontweight="bold")
                if y == 0 and len(cellDict[(x,0)].get_text().get_text()) >= 5: cellDict[(x,0)].set_fontsize(10)
            cellDict[(0,y)].set_fontsize(10)

        # Тоже самое для ячейки с датами
        tab2 = plt.table(cellText=[[dateText],],cellLoc="right", rowLoc="center", loc='bottom')
        tab2.auto_set_font_size(False)
        cellD = tab2.get_celld()
        cellD[(0,0)].set_height(rowHeight)
        cellD[(0,0)].set_text_props(fontweight="bold")
        if (len(cells)+1)%2 != 0:
            cellD[(0,0)].set_facecolor(cellsColor[0][0])
        else:
            cellD[(0,0)].set_facecolor(cellsColor[1][0])

        # Отключаем отображение оси, чуть подгоняем маштаб и сохраняем в файл
        plt.gca().set_axis_off()
        plt.tight_layout()
        # if save:
        #     plt.savefig(f"{makeDir('./graphics')}/aBooksTable{EndOutFilename}.png")
        # if show:
        #     plt.show()
        # plt.close()
        return plt
    
    
    cells, cellsColor, dateText = _genTableData(getPriceStat())

    if onefile:
        ln_to_page = len(cells)
    elif telegram_size:
        ln_to_page = 25 
    else:
        ln_to_page = 48
    for ct in range(0, len(cells), ln_to_page):
        pl = _plotTable(cells[1*ct:ln_to_page+ct], cellsColor[1*ct:ln_to_page+ct], dateText)
        if save:
            pl.savefig(f"{makeDir('./graphics')}/aBooksTable{str(ct+1).zfill(4)}.png")
        if show:
            pl.show()
        pl.close()
                                    
