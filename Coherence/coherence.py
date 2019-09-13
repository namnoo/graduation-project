from konlpy.tag import Kkma, Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
import re
import sys
import numpy as np

file = open('test.csv', 'r', encoding='euc-kr')
reader = csv.reader(file)

content = ""
docList = []

for line in reader:
    content = re.sub('[^0-9a-zA-Zㄱ-힗 .]',' ',line[2])

    reversed_content = ''.join(reversed(content))
    for i in range(0, len(content)):
        if reversed_content[i:i + 2] == '.다':
            content = ''.join(reversed(reversed_content[i:]))
            break

    content = content.replace('.', '. ')

    kkma = Kkma()

    noun = ' '.join(kkma.nouns(content))

    docList.append(noun)

    print(noun)

tfidf_vectorizer = TfidfVectorizer(min_df=1)
tfidf_matrix = tfidf_vectorizer.fit_transform(docList)

document_distances = (tfidf_matrix * tfidf_matrix.T)
print(document_distances)

print("Result: " + str(document_distances.get_shape()[0]) +\
      'x' + str(document_distances.get_shape()[1]))
np.set_printoptions(threshold=sys.maxsize)
print(document_distances.toarray())    
