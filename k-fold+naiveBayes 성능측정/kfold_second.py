from __future__ import division
from collections import Counter, defaultdict
from sklearn.model_selection import train_test_split, KFold
import math, random, re, glob
import pandas as pd
from konlpy.tag import Okt
import csv

global result, index_Proba, modify

def tokenize(message):
    okt = Okt()
    all_words = okt.nouns(message)
    return set(all_words)

def count_words(training_set):
    counts = defaultdict(lambda: [0,0,0,0,0,0])
    training_set_arr = training_set.values
    for is_criminal, message in training_set_arr:
        for word in tokenize(message):
            counts[word][int(is_criminal)] += 1

    return counts

def word_probabilities(counts, total_non_criminals, total_violence, \
                       total_Sviolence, total_theft, total_robbery, total_murder, k=5):
    return [(w,
             (non_criminals + k) / (total_non_criminals + 2 * k),
             (violence + k) / (total_violence + 2 * k),
             (Sviolence + k) / (total_Sviolence + 2 * k),
             (theft + k) / (total_theft + 2 * k),
             (robbery + k) / (total_robbery + 2 * k),
             (murder + k) / (total_murder + 2 * k))
            for w, (non_criminals, violence, Sviolence, theft, robbery, murder) in counts.items()]

def criminal_probability(word_probs, message):
    global index_Proba
    message_words = tokenize(message)
    log_prob_if_not_criminal = 0.0
    log_prob_if_violence = log_prob_if_Sviolence = log_prob_if_theft = 0.0
    log_prob_if_robbery = log_prob_if_murder = 0.0

    for word, prob_if_not_criminal, prob_if_violence, prob_if_Sviolence, prob_if_theft, prob_if_robbery, prob_if_murder in word_probs:
        # 만약 기사에 word가 나타나면 해당 단어가 나올 log 확률을 더해 줌
        if word in message_words:
            log_prob_if_not_criminal += math.log(prob_if_not_criminal)
            log_prob_if_violence += math.log(prob_if_violence)
            log_prob_if_Sviolence += math.log(prob_if_Sviolence)
            log_prob_if_theft += math.log(prob_if_theft)
            log_prob_if_robbery += math.log(prob_if_robbery)
            log_prob_if_murder += math.log(prob_if_murder)

        # 만약 기사에 word가 나타나지 않는다면 해당 단어가 나오지 않을 log 확률을 더해 줌
        # 나오지 않을 확률은 log(1-나올 확률)로 계산
        else:
            log_prob_if_not_criminal += math.log(100.0 - prob_if_not_criminal)
            log_prob_if_violence += math.log(100.0 - prob_if_violence)
            log_prob_if_Sviolence += math.log(100.0 - prob_if_Sviolence)
            log_prob_if_theft += math.log(100.0 - prob_if_theft)
            log_prob_if_robbery += math.log(100.0 - prob_if_robbery)
            log_prob_if_murder += math.log(100.0 - prob_if_murder)
    """
    prob_if_not_criminal = math.exp(log_prob_if_not_criminal)
    prob_if_violence = math.exp(log_prob_if_violence)
    prob_if_Sviolence = math.exp(log_prob_if_Sviolence)
    prob_if_theft = math.exp(log_prob_if_theft)
    prob_if_robbery = math.exp(log_prob_if_robbery)
    prob_if_murder = math.exp(log_prob_if_murder)
    """
    prob_if_not_criminal = log_prob_if_not_criminal
    prob_if_violence = log_prob_if_violence
    prob_if_Sviolence = log_prob_if_Sviolence
    prob_if_theft = log_prob_if_theft
    prob_if_robbery = log_prob_if_robbery
    prob_if_murder = log_prob_if_murder
    
    max_Proba = 0
    index_Proba = ''
    if max_Proba < (prob_if_murder / (prob_if_murder + prob_if_not_criminal)):
        max_Proba = prob_if_murder / (prob_if_murder + prob_if_not_criminal)
        index_Proba = 'murder'
    if max_Proba < (prob_if_robbery / (prob_if_robbery + prob_if_not_criminal)):
        max_Proba = prob_if_robbery / (prob_if_robbery + prob_if_not_criminal)
        index_Proba = 'robbery'
    if max_Proba < (prob_if_theft / (prob_if_theft + prob_if_not_criminal)):
        max_Proba = prob_if_theft / (prob_if_theft + prob_if_not_criminal)
        index_Proba = 'theft'
    if max_Proba < (prob_if_Sviolence / (prob_if_Sviolence + prob_if_not_criminal)):
        max_Proba = prob_if_Sviolence / (prob_if_Sviolence + prob_if_not_criminal)
        index_Proba = 'Sviolence'
    if max_Proba < (prob_if_violence / (prob_if_violence + prob_if_not_criminal)):
        max_Proba = prob_if_violence / (prob_if_violence + prob_if_not_criminal)
        index_Proba = 'violence'
    #print("max_Proba: " + str(max_Proba) + ", index_Proba: " + str(index_Proba))
    return max_Proba, index_Proba # 제일 높은 확률, 카테고리

class NaiveBayesClassifier:
    def __init__(self, k=5):
        self.k = k
        self.word_probs = []

    def classify(self, message):
        return criminal_probability(self.word_probs, message)

    def train(self, training_set):
        # 범죄 데이터와 아닌 데이터의 갯수 세기
        num_non_criminals = len(training_set[training_set.is_criminal == '0'])
        num_violence = len(training_set[training_set.is_criminal == '1'])
        num_Sviolence = len(training_set[training_set.is_criminal == '2'])
        num_theft= len(training_set[training_set.is_criminal == '3'])
        num_robbery = len(training_set[training_set.is_criminal == '4'])
        num_murder = len(training_set[training_set.is_criminal == '5'])

        # 학습 데이터 적용하여 모델 만들기
        word_counts = count_words(training_set)
        self.word_probs = word_probabilities(word_counts, num_non_criminals, num_violence, \
                                             num_Sviolence, num_theft, num_robbery, num_murder, self.k)

def train_and_test_model(data, sw, predicMess=''):
    global result

    if sw == '0': # modeling

        kf = KFold(n_splits=10, shuffle=True, random_state=0)

        for train_index, test_index in kf.split(data):
            tp, fp, fn, tn = 0, 0, 0, 0
            
            train_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            test_data = pd.DataFrame(columns=['is_criminal', 'message_'])

            #print("Train: " , train_index , ", Test: " ,test_index)

            for i in train_index:
                train_data.loc[i, 'is_criminal'] = data.iloc[i].is_criminal
                train_data.loc[i, 'message_'] = data.iloc[i].message_
            for j in test_index:
                test_data.loc[j, 'is_criminal'] = data.iloc[j].is_criminal
                test_data.loc[j, 'message_'] = data.iloc[j].message_
            #print(train_data)

            classifier = NaiveBayesClassifier()
            classifier.train(train_data)

            test_data_arr = test_data.values
            classified = [(is_criminal, message_, classifier.classify(message_))
                          for is_criminal, message_ in test_data_arr]

            for c in classified:
                if c[2][0] > 0.5:
                    category = ''
                    if c[2][1] == "murder":
                        category = '살인'
                        if c[0] == 5: tp += 1
                        else: tn += 1
                    elif c[2][1] == "robbery":
                        category = '강도'
                        if c[0] == 4: tp += 1
                        else: tn += 1
                    elif c[2][1] == "theft":
                        category = '절도'
                        if c[0] == 3: tp += 1
                        else: tn += 1
                    elif c[2][1] == "Sviolence":
                        category = '성폭행'
                        if c[0] == 2: tp += 1
                        else: tn += 1
                    elif c[2][1] == "violence":
                        category = '폭행'
                        if c[0] == 1: tp += 1
                        else: tn += 1
                    #print(category, " 카테고리 입니다. ", c[2][1])
                else:
                    #print("범죄 데이터가 아닙니다. ", c[2][1])
                    if c[0] == 0: fn += 1
                    else: fp += 1

            print("TP: " + str(tp) + ", FP: " + str(fp) + ", FN: " + str(fn) + ", TN: " + str(tn))
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            accuracy = (tp + tn) / (tp + fn + fp + tn)
            f1_score = 2 * (precision * recall) / (precision + recall)
            print("Precision: " + str(precision) + ", Recall: " + str(recall) \
                  + ", Accuracy: " + str(accuracy) + ", F1-score: " + str(f1_score))

            #result = []
                    

    else: # sw == 1 prediction
        """
        random.seed(0)

        train_data, test_data = train_test_split(data, test_size=0.1)

        classifier = NaiveBayesClassifier()
        classifier.train(train_data)

        criminal_probability = classifier.classify(predicMess)
        """
        kf = KFold(n_splits=10, shuffle=True, random_state=0)

        for train_index, test_index in kf.split(data):
            train_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            test_data = pd.DataFrame(columns=['is_criminal', 'message_'])
            print("Train: " , train_index , ", Test: " ,test_index)
            for i in train_index:
                train_data.loc[i, 'is_criminal'] = data.iloc[i].is_criminal
                train_data.loc[i, 'message_'] = data.iloc[i].message_
            for j in test_index:
                test_data.loc[i, 'is_criminal'] = data.iloc[j].is_criminal
                test_data.loc[i, 'message_'] = data.iloc[j].message_
            #print(train_data)

            classifier = NaiveBayesClassifier()
            classifier.train(train_data)

            criminal_probability = classifier.classify(predicMess)
            
            if criminal_probability[0] > 0.5:
                category = ''
                if criminal_probability[1] == "murder":
                    category = '살인'
                    result = '5'
                elif criminal_probability[1] == "robbery":
                    category = '강도'
                    result = '4'
                elif criminal_probability[1] == "theft":
                    category = '절도'
                    result = '3'
                elif criminal_probability[1] == "Sviolence":
                    category = '성폭행'
                    result = '2'
                elif criminal_probability[1] == "violence":
                    category = '폭행'
                    result = '1'
                print(category, " 카테고리 입니다. ", criminal_probability[0])
            else:
                print("범죄 데이터가 아닙니다. ", criminal_probability[0])
                result = str(index_Proba)

            modify.append(result)


def nlpKoCriminalStart(predicMessage, mode):
    # mode = '1' # '0': modeling, '1': prediction
    readData = pd.read_csv(r'C:\Users\namno\Desktop\Python\textRank-original-percent\data_500_500_textRank_not_crime_plus.csv', encoding='euc-kr')
    #readData = pd.read_csv(r'C:\Users\namno\Desktop\test.csv', encoding='euc-kr')
    trainData = readData.loc[:,['is_criminal', 'message_']]


    train_and_test_model(trainData, mode, predicMessage)

nlpKoCriminalStart('', '0')
