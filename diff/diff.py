 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re


def print_(dic):
    if (type(dic) is dict): 
        for a,b in dic.items():
            if (type(b) is dict): 
                print( ''.join(a) + ' ')
                print_(b)
            else:
                print( ''.join(a) + ' ' + ''.join(b))
    else:
        print (''.join(dic))
            

def extract_table_horizon(soup): #return dictionary
    
    data = {}
    table = soup.find('table')
    titles = []
    rows = table.find_all('tr')
    for row in rows:
        index = row.find('th')
        index = re.sub("\r|\n","",index.text) 
        titles.append(index)
        content = row.find('td')
        if(not bool(content)):
            data[index] = ''
            continue
        link = content.find('a')
        if(bool(link)):
            link_dict ={}
            link_dict[data[titles[0]]+'-'+link.text] = link['href']
            data[index] = link_dict
        else:
            content = re.sub("\r|\n| ","",content.text)
            data[index] = content

    return data

def extract_table_vertical(soup): #return list
    data = []
    table = soup.find('table')

    rows = table.find_all('tr')
    index = []
    for row in rows:
        titles = row.find_all('th')
        if (len(titles) > 0) :
            for title in titles:
                title = re.sub("\r|\n| ","",title.text)
                index.append(title)
            continue
        item = {}
        contents = []
        cols = row.find_all('td')
        for content in cols:
            links = content.find_all('a')
            if(len(links) > 0):
                link_dict ={}
                for link in links:
                    link_dict[link.text] = link['href']
                contents.append(link_dict)
            else:        
                text = re.sub("\r|\n| ","",content.text)
                contents.append(text)
        
        for i in range(len(index)):
            item[index[i]] = contents[i]

        data.append(item)
    
    return data

def diff_item(new, old):
    soup1 = BeautifulSoup(new,'html5lib')
    data1 = extract_table_vertical(soup1)
    if(old):
        soup2 = BeautifulSoup(old,'html5lib')
        data2 = extract_table_vertical(soup2)
        dif = []
        for i in data2:
            if i not in data:
                dif.append(i)
        return dif
    else:
        return data1
    

def diff_class( new_class, old_class):
    noti = {}
    cal = {}
    down = {}
    new_content = new_class['Content']
    old_content = old_class['Content']
    item_list = ['課程資訊','公佈欄','課程內容','作業區','投票區','學習成績']
    timeNplace = ['上課時間','上課地點']
    for key in item_list:
        cal[key] = {}
        down[key] = {}
        noti[key] = {}
        if (key == '課程資訊'):
            if not new_content[key]:
                continue
            info = extract_table_horizon(BeautifulSoup(new_content[key],'html5lib'))
            for i in timeNplace:
                noti[i] = info[i]
                cal[i] = info[i]

        elif (key == '公佈欄') or ( key == '作業區'):

            
            html_new = new_content[key]['html']
            if not html_new:
                continue
            html_old = old_content[key]['html']
            differ = diff_item(html_new,html_old)

            for i in differ:
                if(key == '公佈欄'):
                    title = list(i['公告主題'].keys())[0]
                    post = extract_table_horizon(BeautifulSoup(new_content[key]['content'][title],'html5lib'))
                    
                    noti[key][title] = post['公告內容']
                    down[key][title] = post['相關附檔']
                else:
                    title = list(i['名稱'].keys())[0]
                    post = extract_table_horizon(BeautifulSoup(new_content[key]['content'][title],'html5lib'))
                    noti[key][title] = post['繳交期限']
                    cal[key][title] = post['繳交期限']
                    down[key][title] = post['相關檔案']

        elif (key == '投票區') or (key == '學習成績'):
            
            html_new = new_content[key]
            if not html_new:
                continue
            html_old = old_content[key]
            new_data = diff_item(html_new,html_old)
            for i in new_data:
                if key =='投票區':
                    title = i['投票主題']
                    noti[key][title] = i['結束日期']
                else:
                    title = i['項目']
                    noti[key][title] = i['得分']
        elif key == '課程內容':
            if not new_content[key]:
                continue
            cal['考試'] = {}
            html_new = new_content[key]
            html_old = old_content[key]
            new_data = diff_item(html_new,html_old)
            data = extract_table_vertical(BeautifulSoup(html_new,'html5lib'))
            for a in data:
                for b in a.values():
                    if ('期中考' in b):  
                        cal['考試']['期中考'] = a['日期']
                    elif ('期末考' in b):
                        cal['考試']['期末考'] = a['日期']
            for i in new_data:
                if(type(i['內容檔案']) is dict):
                    for title,item in i['內容檔案'].items():
                        down[key][i['週次']+'-'+title] = item

    return noti,cal,down
def get_head(new_class):
    head = {}
    titles = ['ChineseName','EnglishName','Tutor']
    for i in titles:
        head[i] = new_class[i]
    return head
def diff( new_lectures, old_lectures):
    notifications = []
    calendars = []
    downlaods = []
    for i in range(len(new_lectures)):
        new_class = new_lectures[i]
        old_class = old_lectures[i]
      
        head = get_head(new_class)
        noti, cal, down = diff_class(new_class,old_class)
        
        head['Content'] = noti
        notifications.append(head)
        head['Content'] = cal
        calendars.append(head)
        head['Content'] = down
        downlaods.append(head)
        
    return notifications,calendars,downlaods
def main():
    notifications,calendars ,downlaods = diff(lecture,lecture2)

if __name__ == '__main__':

    old_file = 'hw2.html'
    new_file = 'hw1.html'

    lecture =  [
        {
        'ChineseName' : 'aaa',
        'EnglishName' : 'bbb',
        'Tutor' : 'ccc',
        'url': 'https://ceiba.ntu.edu.tw/1062PE2074_B9',
        'Content': {
            '課程資訊': open('info.html','r').read(),
            '教師資訊': open('tutor.html','r').read(),
            '公佈欄': {
                'html':open('board.html','r').read(),
                'content':{
                    '期中考說明書':open('board_i.html','r').read()
                }
            },
            '課程內容': open('sylab.html','r').read(),
            '作業區': {
                'html':'',
                'content': {
                }
                    
            },
            '投票區': '',
            # TODO: 討論看版: html_sring
            '學習成績': open('grade.html','r').read()
        }
        }
    ]
    lecture2 =  [
        {
        'ChineseName' : 'aaa',
        'EnglishName' : 'bbb',
        'Tutor' : 'ccc',
        'Content': {
            '課程資訊': '',
            '教師資訊': '',
            '公佈欄': {
                'html':{},
                'content':{}
            },
            '課程內容': '',
            '作業區': {
                   'html':{},
                'content':{} 
            },
            '投票區': '',
            # TODO: 討論看版: html_sring
            '學習成績': ''
            }
        }
    ]
    main()
