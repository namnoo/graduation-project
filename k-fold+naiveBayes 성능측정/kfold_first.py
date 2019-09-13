from __future__ import division
from collections import Counter, defaultdict
from sklearn.model_selection import train_test_split, KFold
import math, random, re, glob
import pandas as pd
from konlpy.tag import Okt
import csv

global result, cnt, classifier

cnt = 0
result = []

def tokenize(message):
    okt = Okt()
    all_words = okt.nouns(message)
    return set(all_words)

def count_words(training_set):
    counts = defaultdict(lambda: [0,0])
    training_set_arr = training_set.values
    for is_criminal, message in training_set_arr:
        for word in tokenize(message):
            counts[word][int(is_criminal)] += 1

    return counts

def word_probabilities(counts, total_non_criminals, total_criminals, k=1):
    return [(w,
             (non_criminals + k) / (total_non_criminals + 2 * k),
             (criminals + k) / (total_criminals + 2 * k))
              for w, (non_criminals, criminals) in counts.items()]

def criminal_probability(word_probs, message):
    message_words = tokenize(message)
    log_prob_if_not_criminal = 0.0
    log_prob_if_criminal = 0.0

    for word, prob_if_not_criminal, prob_if_criminal in word_probs:
        #print(word, prob_if_not_criminal, prob_if_criminal)
        if word in message_words:
            log_prob_if_not_criminal += math.log(prob_if_not_criminal)
            log_prob_if_criminal += math.log(prob_if_criminal)
        else:
            log_prob_if_not_criminal += math.log(1000.0 - prob_if_not_criminal)
            log_prob_if_criminal += math.log(1000.0 - prob_if_criminal)

    prob_if_not_criminal = log_prob_if_not_criminal
    prob_if_criminal = log_prob_if_criminal
    max_Proba = 0
    index_Proba = ""
    if max_Proba < (prob_if_criminal/ (prob_if_criminal + prob_if_not_criminal)):
        max_Proba = prob_if_criminal / (prob_if_criminal + prob_if_not_criminal)
        index_Proba = 'Crime'      

    return max_Proba, index_Proba # 제일 높은 확률, 카테고리

class NaiveBayesClassifier:
    def __init__(self, k=1):
        self.k = k
        self.word_probs = []

    def classify(self, message):
        return criminal_probability(self.word_probs, message)

    def train(self, training_set):
        # 범죄 데이터와 아닌 데이터의 갯수 세기
        num_non_criminals = len(training_set[training_set.is_criminal == 0])
        num_criminal = len(training_set[training_set.is_criminal == 1])

        # 학습 데이터 적용하여 모델 만들기
        word_counts = count_words(training_set)
        self.word_probs = word_probabilities(word_counts, num_non_criminals, num_criminal, self.k)

def train_and_test_model(data, sw, predicMess=''):
    global result, cnt

    if sw == '0': # modeling

        kf = KFold(n_splits=10, shuffle=True, random_state=0)
        for train_index, test_index in kf.split(data):
            tp, fp, fn, tn = 0, 0, 0, 0
            
            train_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            test_data = pd.DataFrame(columns=['is_criminal', 'message_'])

            for i in train_index:
                train_data.loc[i, 'is_criminal'] = data.iloc[i].is_criminal
                train_data.loc[i, 'message_'] = data.iloc[i].message_

            for j in test_index:
                test_data.loc[j, 'is_criminal'] = data.iloc[j].is_criminal
                test_data.loc[j, 'message_'] = data.iloc[j].message_

            classifier = NaiveBayesClassifier()
            classifier.train(train_data)

            test_data_arr = test_data.values
            classified = [(is_criminal, message_, classifier.classify(message_))
                          for is_criminal, message_ in test_data_arr]
            
            for c in classified:
                if c[2][0] > 0.5:
                    #print("범죄 기사 입니다. ", data[2][0])
                    #result.append('1')
                    #cnt = cnt +1
                    #print("검사한 데이터 수 :", cnt)
                    if c[0] == 1: # 테스트 정확
                        tp += 1
                    elif c[0] == 0: # 테스트 틀림
                        fp += 1
                else:
                    #print("범죄 기사가 아닙니다. ", data[2][0])
                    #result.append('0')
                    #cnt = cnt +1
                    #print("검사한 데이터 수 :", cnt)
                    if c[0] == 0: # 테스트 정확
                        fn += 1
                    elif c[0] == 1: # 테스트 틀림
                        tn += 1

            #print(result)
            print("TP: " + str(tp) + ", FP: " + str(fp) + ", FN: " + str(fn) + ", TN: " + str(tn))
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            accuracy = (tp + tn) / (tp + fn + fp + tn)
            f1_score = 2 * (precision * recall) / (precision + recall)
            print("Precision: " + str(precision) + ", Recall: " + str(recall) \
                  + ", Accuracy: " + str(accuracy) + ", F1-score: " + str(f1_score))
            
            #result = []
            
            """ this part test_data accuracy """

    else: # sw == 1 prediction
        
        kf = KFold(n_splits=10, shuffle=True, random_state=0)

        for train_index, test_index in kf.split(data):
            train_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            test_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            print("Train: " , train_index , ", Test: " ,test_index)
            for i in train_index:
                train_data.loc[i, 'is_criminal'] = data.iloc[i].is_criminal
                train_data.loc[i, 'message_'] = data.iloc[i].message_
            for j in test_index:
                test_data.loc[j, 'is_criminal'] = data.iloc[j].is_criminal
                test_data.loc[j, 'message_'] = data.iloc[j].message_
            #print(train_data)

            classifier = NaiveBayesClassifier()
            classifier.train(train_data)
        
            criminal_probability = classifier.classify(predicMess)
            
            if criminal_probability[0] > 0.5:
                print("범죄 기사 입니다. ", criminal_probability[0])
                result.append('1')
                cnt = cnt +1
                print("검사한 데이터 수 :", cnt)
            else:
                print("범죄 기사가 아닙니다. ", criminal_probability[0])
                result.append('0')
                cnt = cnt +1
                print("검사한 데이터 수 :", cnt)
            print(result)


def nlpKoCriminalStart(predicMessage, mode):
    # mode = '1' # '0': modeling, '1': prediction
    readData = pd.read_csv(r'C:\Users\namno\Desktop\Python\지혜\newsis_first_2000.csv', encoding='euc-kr')
    trainData = readData.loc[:,['is_criminal', 'message_']]


    train_and_test_model(trainData, mode, predicMessage)

nlpKoCriminalStart('', '0')


