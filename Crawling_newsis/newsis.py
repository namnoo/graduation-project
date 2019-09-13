''' 뉴시스
한 페이지당 20개의 기사
기사 리스트에서 본문까지 확인 가능!!!! '''

import sys
import re
import urllib.request
import csv
from bs4 import BeautifulSoup
from urllib.parse import quote

TARGET_URL_BEFORE_KEWORD = "http://www.newsis.com/search/schlist/?val="
TARGET_URL_BEFORE_PAGE_NUM = "&sort=rec&jo=all_jogun&bun=direct&sdate=20190813" + \
                             "&term=allday&edate=20190908&s_yn=Y&catg=1&t=1&page="
TARGET_URL_REST = "&c[]=10200"

# 키워드로 검색했을 때 나오는 기사 페이지 수
def get_page_total_num(keyword):
    URL_with_page_num = TARGET_URL_BEFORE_KEWORD + quote(keyword) + \
                        TARGET_URL_BEFORE_PAGE_NUM + "1" + TARGET_URL_REST
    source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
    soup = BeautifulSoup(source_code_from_URL, 'html.parser')
    
    soupDiv = soup.find('div', class_='search_result mgt21')
    soupToText = soupDiv.find_all('span', class_='c1')[1].text
    textToInt = int(re.findall("\d+", soupToText)[0])

    # 한 페이지당 20개의 기사가 있음
    return int(textToInt / 20)
    
# 기사 검색 페이지에서 기사 제목과 기사 본문, 기사 링크 모두 받아오기
def get_link_from_news(keyword):
    total_page = get_page_total_num(keyword)
    
    # CSV 파일 생성
    file = open(r'C:\Users\namno\Desktop\Python\newsis_output_8월13일이후_' + keyword + '.csv', 'w', encoding='euc-kr', newline='')
    wcsv = csv.writer(file)
    
    for page in range(1, total_page+1):
        for current in range(20):
            URL_with_page_num = TARGET_URL_BEFORE_KEWORD + quote(keyword) + \
                        TARGET_URL_BEFORE_PAGE_NUM + str(page) + TARGET_URL_REST
            source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
            soup = BeautifulSoup(source_code_from_URL, 'html.parser')
            
            soupAllDiv = soup.findAll('div', class_='area')[current]

            # 기사 제목
            title = soupAllDiv.find('strong', class_='title').text
            #print(title.encode('euc-kr'))
            #print(chardet.detect(title.encode('euc-kr')))
            title = title.encode('euc-kr', 'ignore').decode('euc-kr')
            # 기사 링크
            link = soupAllDiv.find("a").attrs['href']
            link = link.encode('euc-kr', 'ignore').decode('euc-kr')
            # 기사 본문
            content = ''.join(soupAllDiv.find('p', class_='txt1').text.splitlines())   
            content = content.encode('euc-kr', 'ignore').decode('euc-kr')

            # 기사 날짜
            date = ''.join(re.findall("\d+", soupAllDiv.find('span', class_='date').text))
            addDate = date[:8] + ' ' + date[8:10] + ':' + date[10:]
            addDate = addDate.encode('euc-kr', 'ignore').decode('euc-kr')
             # CSV 작성
            wcsv.writerow([addDate, title, content, link])

            print("Page: " + str(page) + ", Current: " + str(current))

    file.close()

              
# 메인
def main(argv):
    if len(argv) != 2:
        print("python [모듈 이름] [키워드]")
        return
    keyword = argv[1]
    
    get_link_from_news(keyword)

if __name__ == '__main__':
    main(sys.argv)
