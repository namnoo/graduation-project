import csv
import re
from textrankr import TextRank

f = open(r'C:\Users\namno\Desktop\Python\newsis_output_8월13일이후_폭력+폭행+성폭력+성폭행+강도+절도+살인+살해.csv', 'r', encoding='euc-kr')
reader = csv.reader(f)

f2 = open(r'C:\Users\namno\Desktop\Python\newsis_output_8월13일이후_textRank_폭력+폭행+성폭력+성폭행+강도+절도+살인+살해.csv', 'w', encoding='euc-kr', newline='')
writer = csv.writer(f2)

for line in reader:
    line_modify = []
    content = ""

    line_modify.append(line[0])
    #line_modify.append(line[1])
    line_modify.append(re.sub('[^0-9a-zA-Zㄱ-힗 .]',' ',line[1]))

    # 기사 맨 뒤 이메일 삭제
    reversed_content = ''.join(reversed(line[2]))
    for i in range(0, len(line[2])):
        # reverse 된 기사 내용중, ".다"로 끝나는 경우 기사 내용이 끝난 것이기 때문에 기사 내용이 끝난 후의 광고, 기자 등의 정보는 다 지움
        if reversed_content[i:i + 2] == '.다':
            content = ''.join(reversed(reversed_content[i:]))
            break    

    content = content.replace('.', '. ')
    line_modify.append(re.sub('[^0-9a-zA-Zㄱ-힗 .]',' ',content))
    
    text = TextRank(content)
    text = text.summarize()
    text = re.sub('[^0-9a-zA-Zㄱ-힗 .]',' ',text)
    line_modify.append(text)
    print(text)
    
    line_modify.append(line[3])

    writer.writerow(line_modify)
 
f.close()
f2.close()
