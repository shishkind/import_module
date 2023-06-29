from tkinter import *
from tkinter.filedialog import *
import fileinput
import pyodbc
import transliterate
import datetime
from pyodbc import Error
from lxml import etree
from transliterate import translit
import os
l = []
Full_results = []
gl_indicators = []
gl_ind_flags = []
source = ""
author_list = []
all_firstnames = []
all_lastnames = []
all_patr = []
xml=[]
books = []
eLib_inds = []
authors = []
page_st = []
page_end = []
page_count=[]
django_result = [0,0,0,0,0,0]
count_publ = 0
count_art = 0 
count_conf = 0
count_book = 0
count_other = 0

def read(filename):
    global l
    global source
    global xml
    os.environ.__setitem__('DISPLAY', ':0.0')
    #root = Tk()
    #root.withdraw()
    print(os.path.abspath(str(filename)))
    with open(os.path.abspath(str(filename)), encoding='utf-8') as f:
        if str(f).find(".bib")!=-1:
            l = f.read().splitlines()
            for i in range(len(l)):  # Выявление источника экспорта путем поиска в файле адреса скопуса или категорий ВоС
                if l[i].find("https://www.scopus.com") != -1:
                    source = "Scopus"
                    break
                elif l[i].find("Web-of-Science") != -1:
                    source = "Web Of Science"
        if str(f).find(".xml")!=-1:
            xml = f.read()
            source = "eLibrary"
            #print(xml)
    #print(source)
 
def parseXML():
    global xml
    root = etree.fromstring(xml)
    book_dict = []
    global books
    global eLib_inds
    indicators = []
    ind_dict = []
    for book in root.getchildren():
        for elem in book.getchildren():
          if len(elem.getchildren()) > 0 :
            for sub_elem in elem.getchildren():
              if len(sub_elem.getchildren()) > 0 :
                for sub_elem1 in sub_elem.getchildren():
                  if len(sub_elem1.getchildren()) > 0 :  
                    for sub_elem2 in sub_elem1.getchildren():
                      if len(sub_elem2.getchildren()) > 0 :  
                        for sub_elem3 in sub_elem2.getchildren():
                          if not sub_elem3.text:
                            text = "None"
                          else:
                            text = sub_elem3.text
                          #print(sub_elem.tag + " => " + text)
                          book_dict.append(text)
                          ind_dict.append(sub_elem3.tag)
                        continue
                      if not sub_elem2.text:
                        text = "None"
                      else:
                        text = sub_elem2.text
                      #print(sub_elem.tag + " => " + text)
                      book_dict.append(text)
                      ind_dict.append(sub_elem2.tag)
                    continue
                  if not sub_elem1.text:
                    text = "None"
                  else:
                    text = sub_elem1.text
                  #print(sub_elem.tag + " => " + text)
                  book_dict.append(text)
                  ind_dict.append(sub_elem1.tag)
                continue
              if not sub_elem.text:
                text = "None"
              else:
                text = sub_elem.text
              #print(sub_elem.tag + " => " + text)
              book_dict.append(text)
              ind_dict.append(sub_elem.tag)
            continue
          if not elem.text:
                text = "None"
          else:
              text = elem.text
          #print(elem.tag + " => " + text)
          book_dict.append(text)
          ind_dict.append(elem.tag)
        
        if book.tag == "item":
            books.append(book_dict)
            indicators.append(ind_dict)
            ind_dict = []
            book_dict = []
    
    #for i in range(len(books)):
     # for j in range(len(books[i])):
        #print(indicators[i][j] + ": " + books[i][j])
      #print(" ")
    eLib_inds = indicators
    #return books

def eLib_output():
    global books
    global eLib_inds
    global all_firstnames
    global all_lastnames
    global all_patr
    global authors
    global Full_results
    tmp_author = ""
    tmp_i=0
    tmp_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    global page_st
    global page_end   
    global page_count
    global count_publ
    global count_conf
    global count_art
    global count_book
    global count_other
    page_end = []
    page_st = []
    page_count = []
    indicators = ['genre','title', 'publisher', 'year', 'volume', 'pagesnumber', 'language', 'cited', 'doi', 'isbn', 'issn', 'linkurl',
                  'pages', 'title']
    for i in range(len(books)):
        for j in range(len(books[i])):
            if eLib_inds[i][j] == "lastname":
                tmp_author = tmp_author + books[i][j]
            if eLib_inds[i][j] == "initials":
                tmp_author = tmp_author + " " + books[i][j] + "; "
            if eLib_inds[i][j] == "pages":
                if books[i][j].find("-") != -1:
                    page_end.append(books[i][j][books[i][j].find("-")+1:].replace("e", ""))
                    page_st.append(books[i][j][:books[i][j].find("-")].replace("e", ""))
                    page_count.append(int(page_end[i])-int(page_st[i])+1)
                else:
                    page_st.append(books[i][j].replace("e", ""))
                    page_end.append(books[i][j].replace("e", ""))
                    page_count.append("1")
            if eLib_inds[i][j] == 'genre' and books[i][j] == 'статья в сборнике трудов конференции':
                count_conf += 1
            elif eLib_inds[i][j] == 'genre' and books[i][j] == 'статья в журнале':
                count_art += 1
            elif eLib_inds[i][j] == 'genre' and books[i][j] == 'книга или сборник статей':
                count_book += 1
            elif eLib_inds[i][j] == 'genre':
                count_other += 1            
            
                
        authors.append(tmp_author)
        tmp_author = ""

    for i in range( len(books)):
        for k in range(len(indicators)):
            if tmp_list[k] == 0:
                for j in range(tmp_i, len(books[i])):
                    if eLib_inds[i][j] == indicators[k]:
                        tmp_list[k] = books[i][j]
                        tmp_i=tmp_i+1
                        
                        break
                
        tmp_i=0
        tmp_author = ""
        count_publ+=1
        Full_results.append(tmp_list)
        tmp_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    print(Full_results)
    print(authors)
    print(page_st)
    print(page_end)
    print(page_count)
            


                

def parse_WoS(n):
    global gl_indicators
    global count_publ
    global count_conf
    global count_art
    global count_book
    global count_other
    indicators = ['Author', 'Editor', 'Book-Group-Author', 'Title', 'Booktitle', 'Journal', 'Year', 'Volume', 'Number',
                  'Pages',
                  'Month', 'Note', 'Organization', 'Abstract', 'Publisher', 'Address', 'Type', 'Language',
                  'Affiliation', 'DOI', 'Early Access Date', 'ISSN', 'EISSN', 'ISBN', 'Keywords', 'Keywords-Plus',
                  'Research-Areas', 'Web-of-Science-Categories', 'Author-Email', 'ResearcherID-Numbers',
                  'ORCID-Numbers',
                  'Cited-References', 'Number-of-Cited-References', 'Times-Cited', 'Usage-Count-Last-180-days',
                  'Usage-Count-Since', 'Journal-ISO', 'Doc-Delivery-Number', 'Unique-ID', 'OA', 'DA']
    ind_flags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0]
    tmp_str = ""
    tmp = []
    result = ""
    i1 = 0
    results = []
    tmp_ind = 0
    flag = 0
    new_art = 0
    for i in range(n, len(l)):  # Построчная запись файла в tmp, пока не встретится пустая строка
        if l[i] != '':  # Если строка не пустая, то запись в тмп
            tmp.append(l[i])
        else:  # Если пустая, в качестве начала указывается адрес следующей статьи и цикл записи прерывается
            new_art = i + 2
            break
    while i1 < len(tmp):  # Построчная анализ блока
        if i1 == 0:  # Для первой записи отдельный обработчик, поскольку авторы в ВоС содержатся в одинарных скобках,
            # в отличии от остальных показателей
            if tmp[i1].find('}') == -1 and tmp[i1].find(
                    '{') != -1:  # Если в строке нет закрывющейся скобки, то к ней прибавляется следующая, после чего
                # следующая строка удаляется
                tmp[i1] = tmp[i1] + tmp[i1 + 1][2:]
                del tmp[i1 + 1]
                continue
            if tmp[i1].find('{') == -1 and tmp[i1].find(
                    '}') != -1:  # Если в строке  нет открывающейся скобки, то она прибавляется к предыдущей и удаляется
                tmp[i1 - 1] = tmp[i1 - 1] + tmp[i1]
                del tmp[i1]
                continue
            if tmp[i1].find('}') != -1 and tmp[i1].find(
                    '{') != -1:  # Если в строке есть обе скобки, то строка обрабатывается
                tmp_str = tmp[i1]
                if tmp_str.find('Author =') != -1:  # Проверка, что первая строка действительно содержит авторов
                    for c in range(len(tmp_str)):  # Поиск открытой и закрытой скобок
                        open = tmp_str.find('{')
                        close = tmp_str.find('}')
                        break
                    for c in range(open + 1, close):  # Посимвольное добавление текста в скобках в переменную
                        result = result + tmp_str[c]
                    results.append(result)  # Добавление перемнной в общий список
                    # print(result)
                    result = ''  # Обнуление переменной
                    ind_flags[0] = 1  # Установка флага
                i1 += 1  # Следующий шаг
                # print("")
        else:  # Для всех остальных показателей, которые содержатся в двойных скобках
            if tmp[i1].find('}}') == -1 and tmp[i1].find(
                    '{{') == -1:  # Если в строке нет скобок, то переход к следующему шагу
                i1 += 1
                continue
            if tmp[i1].find('}}') == -1 and tmp[i1].find('{{') != -1:  # Аналогично авторам
                tmp[i1] = tmp[i1] + tmp[i1 + 1][2:]
                del tmp[i1 + 1]
                continue
            if tmp[i1].find('{{') == -1 and tmp[i1].find('}}') != -1:  # Аналогично авторам
                tmp[i1 - 1] = tmp[i1 - 1] + tmp[i1]
                del tmp[i1]
                continue
            if tmp[i1].find('}}') != -1 and tmp[i1].find('{{') != -1:  # Аналогично авторам
                tmp_str = tmp[i1]
                for ind in range(tmp_ind, len(indicators)):  # Проход по списку индикаторов
                    if ind_flags[ind] == 1:  # Если флаг показателя уже установлен, то переход к следующему
                        continue
                    if tmp_str.startswith(indicators[ind]) != 0:  # Если строка начинается с элемента списка показателей
                        for c in range(len(tmp_str)):  # Поиск скобок
                            open = tmp_str.find('{') + 1
                            close = tmp_str.find('}}')
                            break
                        for c in range(open + 1, close):  # Посимвольная запись
                            result = result + tmp_str[c]
                        if indicators[ind] == 'Type' and result == 'Proceedings Paper':
                            count_conf += 1
                        elif indicators[ind] == 'Type' and result == 'Article':
                            count_art += 1
                        elif indicators[ind] == 'Type' and result == 'Book Chapter':
                            count_book += 1
                        elif indicators[ind] == 'Type':
                            count_other += 1
                        results.append(result)  # Добавление переменной в список
                        result = ''  # Обнуление
                        ind_flags[ind] = 1  # Установка флага
                        tmp_ind = ind  # переменная для установки диапазона цикла
                        break
                i1 += 1
            else:
                break
    gl_ind_flags.append(ind_flags)  # Добавление флагов статьи в общий список флагов
    Full_results.append(results)  # Добавление списка результатов в общий список
    count_publ += 1
    if new_art == 0:
        gl_indicators = indicators
        return
    parse_WoS(new_art)


def parse_Scopus(n):  # Аналогично ВоС
    global gl_indicators
    global count_publ
    global count_conf
    global count_art
    global count_book
    global count_other
    indicators = ['author', 'title', 'journal', 'year', 'volume', 'number', 'pages', 'doi', 'art_number', 'note', 'url',
                  'affiliation',
                  'correspondence_address1', 'editor', 'publisher', 'issn', 'isbn', 'language', 'abbrev_source_title',
                  'document_type']
    ind_flags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    new_art = 0
    tmp = []
    tmp_str = ''
    result = ''
    results = []
    tmp_ind = 0
    for i in range(n, len(l)):
        if l[i] != '':
            tmp.append(l[i])
        else:
            new_art = i + 1
            break
    for i in range(len(tmp)):
        tmp_str = tmp[i]
        for ind in range(tmp_ind, len(indicators)):
            if ind_flags[ind] == 1:
                continue
            if tmp_str.startswith(indicators[ind]) != 0:
                for c in range(len(tmp_str)):
                    open = tmp_str.find('{')
                    close = tmp_str.find('}')
                    break
                for c in range(open + 1, close):
                    result = result + tmp_str[c]
                if indicators[ind] == 'document_type' and result == 'Conference Paper':
                    count_conf += 1
                elif indicators[ind] == 'document_type' and result == 'Article':
                    count_art += 1
                elif indicators[ind] == 'document_type' and result == 'Book Chapter':
                    count_book += 1
                elif indicators[ind] == 'document_type':
                    count_other += 1

                results.append(result)
                result = ''
                ind_flags[ind] = 1
                tmp_ind = ind

    gl_ind_flags.append(ind_flags)
    Full_results.append(results)
    count_publ += 1
    if new_art == 0:
        gl_indicators = indicators
        return
    parse_Scopus(new_art)


def assignment():
    global gl_indicators
    global Full_results
    global gl_ind_flags
    for i in range(len(gl_ind_flags)):
        for j in range(1, len(gl_ind_flags[i])):
            # Если флаг равен нулю, то на его индекс в результаты вставляется пробел
            if gl_ind_flags[i][j] == 0:
                Full_results[i].insert(j, " ")


def split():
    global author_list
    global source
    pg_st = []
    pg_end = []
    count_pages = []
    global gl_indicators
    result = ''
    tmp_flag = 0
    lastname = []
    tmp_lastname = ""
    global all_lastnames
    tmp_firstname = ""
    firstname = []
    global all_firstnames
    patr = []
    global all_patr
    #if source == "eLibrary":
        #for i in range()
    for k in range(len(Full_results)):
        tmp_authors = []
        if gl_ind_flags[k][0] == 1 and gl_indicators[0].upper() == "AUTHOR":  # Если есть автор
            tmp = Full_results[k][0]  # Cтрока с авторами записывается в переменную
            for i in range(len(Full_results[k][0])):
                if Full_results[k][0].find(" and ") != -1:  # Если в строке есть and
                    Full_results[k][0] = Full_results[k][0].replace(' and', ';')  # Запоминание индекса
                else:
                    tmp_authors.append(tmp)  # Если в строке нет and, то она просто записывается в переменную
                    break
        author_list.append(tmp_authors)  # Добавление переменной в список
        for i in range(len(Full_results[k])):
            if gl_indicators[i].upper() == 'PAGES':  # Если в статье есть страницы
                if Full_results[k][i] != " ":
                    if Full_results[k][i].find("-") != -1:  # Если есть разделитель
                        tmp_st = Full_results[k][i][:Full_results[k][i].find("-")]  # Запоминание части до разделителя
                        pg_st.append("".join(c for c in tmp_st if  c.isdecimal()))
                        tmp_end = Full_results[k][i][
                                  Full_results[k][i].find("-") + 1:]  # Запоминание части после разделителя
                        pg_end.append("".join(c for c in tmp_end if  c.isdecimal()))
                        count_pages.append(int("".join(c for c in tmp_end if  c.isdecimal())) - int("".join(c for c in tmp_st if  c.isdecimal())) + 1)  # Количество страниц
                    else:  # Если страница одна, то она записывается в качестве начальной и конечной
                        pg_st.append("".join(c for c in Full_results[k][i] if  c.isdecimal()))
                        pg_end.append("".join(c for c in Full_results[k][i] if  c.isdecimal()))
                        count_pages.append(1)
                    tmp_flag = 1  # Флаг на то, что хотя бы в одной из статей есть страницы
                else:
                    pg_st.append("0")
                    pg_end.append("0")
                    count_pages.append("0")
                    tmp_flag = 1
            if gl_indicators[i].upper() == 'NOTE' and Full_results[k][i].find("cited By") != -1:  # есть в поле note есть количество цитирований, то они переформатируются просто в чисто
                Full_results[k][i] = Full_results[k][i][Full_results[k][i].find("cited By") + 9:]
                Full_results[k][i] = Full_results[k][i][:Full_results[k][i].find("; ")]
            if gl_indicators[i].upper() == "ISSN" and Full_results[k][i].find("-") != -1:
                Full_results[k][i] = Full_results[k][i][:Full_results[k][i].find("-")] + Full_results[k][i][Full_results[k][i].find("-")+1:]
        #if source == "Web Of Science":
        
    if tmp_flag == 1:  # Добавление новых показателей, флагов и инфы о страницах в общие списки (Проверка по флагу и прошлого блока)
        for i in range(len(gl_indicators)):  # Построчный перебор индикаторов
            if gl_indicators[i].upper() == 'PAGES':  # Если нашли в строке pages
                gl_indicators.insert(i, "Count of pages")  # Вставка на этот индекс новых показателей
                gl_indicators.insert(i, "End page")
                gl_indicators.insert(i, "Start page")
                del gl_indicators[i + 3]  # Удаление показателя pages
                for j in range(len(Full_results)):  # Аналогичное действие для обработанных данных
                    Full_results[j].insert(i, str(count_pages[j]))
                    Full_results[j].insert(i, pg_end[j])
                    Full_results[j].insert(i, pg_st[j])
                    del Full_results[j][i + 3]
                    gl_ind_flags[j].insert(i, 1)  # Для флагов тоже
                    gl_ind_flags[j].insert(i, 1)
                    gl_ind_flags[j].insert(i, 1)
                    del gl_ind_flags[j][i + 3]


def output(): # Тут просто вывод общего списка  показателей (уже допиленного), для авторов отдельный вывод
    global source
    global gl_indicators
    global Full_results
    global gl_ind_flags
    global all_patr
    global all_lastnames
    global all_firstnames
    #if source == "eLibrary":
    for i in range(len(Full_results)):
        for j in range(len(gl_ind_flags[i])):
            print(str(j) + " " + gl_indicators[j] + ":  " + Full_results[i][j])
        print("")
    print("Exported from " + source)


def sql_export():
    global all_firstnames
    global all_patr
    global all_lastnames
    global authors
    global page_count
    global page_end
    global page_st
    global Full_results
    server = '192.168.20.170'
    database = 'BasePPS'
    username = 'shishkin.d'
    password = '295#Skz'
    try:
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()
        print("Successful connection to db")
    except Error as e:
        print("Connection Error!")
        return
    current_date = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
    if source == "eLibrary":
        for k in range(len(Full_results)):
            tmp_transl = authors[k]
            tmp_transl = tmp_transl.replace('ia', 'ия')
            tmp_transl = tmp_transl.replace('x', 'кс')
            tmp_transl = tmp_transl.replace('Yu', 'Ю')
            tmp_transl = tmp_transl.replace('kaya', 'кая')
            tmp_transl = tmp_transl.replace('sky', 'ский')
            cursor.execute("""INSERT INTO dbo.tmp_export (NameAuthor_EN, NameAuthor_RU, Name_Edt, Year, Release, DOI_ED, URL_ISI, Name_PDO, Name_Part, ISSN, ISBN, language_part, NameStruct, Valume_UIA, PageCount, PageBg, PageEnd, Valume_IndA, Name_ABase) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", authors[k], translit(tmp_transl, 'ru'), Full_results[k][13], Full_results[k][3], Full_results[k][4], Full_results[k][8], Full_results[k][11], Full_results[k][2], Full_results[k][1], Full_results[k][10], Full_results[k][9], Full_results[k][6], Full_results[k][0], "", page_count[k], page_st[k], page_end[k], Full_results[k][7], source)
            cnxn.commit()
        print("success")    
    else:
        for k in range(len(Full_results)):
            tmp_transl = Full_results[k][0]
            tmp_transl = tmp_transl.replace('ia', 'ия')
            tmp_transl = tmp_transl.replace('x', 'кс')
            tmp_transl = tmp_transl.replace('Yu', 'Ю')
            tmp_transl = tmp_transl.replace('kaya', 'кая')
            tmp_transl = tmp_transl.replace('sky', 'ский')
            if source == "Scopus":
                cursor.execute("""INSERT INTO dbo.tmp_export (NameAuthor_EN, NameAuthor_RU, Name_Edt, Year, Release, DOI_ED, URL_ISI, Name_PDO, Name_Part, ISSN, ISBN, language_part, NameStruct, Valume_UIA, PageCount, PageBg, PageEnd, Valume_IndA, Name_ABase) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", Full_results[k][0], translit(tmp_transl, 'ru'), Full_results[k][2], Full_results[k][3], Full_results[k][4], Full_results[k][9], Full_results[k][12], Full_results[k][16], Full_results[k][1], Full_results[k][17], Full_results[k][18], Full_results[k][19], Full_results[k][21], Full_results[k][10], Full_results[k][8], Full_results[k][6], Full_results[k][7], Full_results[k][11], source)
            elif source == "Web Of Science":
                cursor.execute("""INSERT INTO dbo.tmp_export (NameAuthor_EN, NameAuthor_RU, Name_Edt, Year, Release, DOI_ED, Name_PDO, Name_Part, ISSN, ISBN, language_part, NameStruct, Valume_UIA, PageCount, PageBg, PageEnd, Valume_IndA, Name_ABase) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", Full_results[k][0], translit(tmp_transl, 'ru'), Full_results[k][5], Full_results[k][6], Full_results[k][7], Full_results[k][21], Full_results[k][16], Full_results[k][3], Full_results[k][23], Full_results[k][25], Full_results[k][19], Full_results[k][18], Full_results[k][40], Full_results[k][11], Full_results[k][9], Full_results[k][10], Full_results[k][35], source)
            cnxn.commit()   
        print("success") 




def main(filename):
    read(filename)
    global source
    global l
    global Full_results
    global gl_ind_flags
    global count_publ
    global count_conf
    global count_art
    global count_book
    global count_other
    xml=[]
    books = []
    eLib_inds = []
    authors = []
    page_st = []
    page_end = []
    page_count=[]
    count_publ = 0
    count_art = 0 
    count_conf = 0
    count_book = 0
    count_other = 0
    Full_results = []
    gl_ind_flags = []
    if source == "Scopus":
        parse_Scopus(2)
        assignment()
        split()
        output()
        #sql_export()
    elif source == "Web Of Science":
        parse_WoS(2)
        assignment()
        split()
        output()
        #sql_export()
    elif source == "eLibrary":
        parseXML()
        eLib_output()
        #sql_export()
    else:
        print("File Error!")
        return
    django_result[0] = source
    django_result[1] = count_publ
    django_result[2] = count_conf
    django_result[3] = count_art
    django_result[4] = count_book
    django_result[5] = count_other
    return(django_result)
    #if source == "Web Of Science":
        #sql_wos()
    #else:
        #print("sql для скопуса в разработке")


if __name__ == '__main__':
    main()

