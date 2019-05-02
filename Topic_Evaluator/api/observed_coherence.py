"""
Author:         Jey Han Lau
Date:           May 2013
"""
import sys
import operator
import math
import codecs
import numpy as np
from collections import defaultdict
from .models import WordCount


def topic_coherence(topic, metric):
    #parameters
    colloc_sep = "_" #symbol for concatenating collocations
    WTOTALKEY = "!!<TOTAL_WINDOWS>!!" #key name for total number of windows (in word count file)


    def fetch(word):
        return WordCount.objects.filter(word=word)

    #compute the association between two words
    def calc_pair(w1, w2, metric):
        w1_count =  fetch(w1)[0].count if fetch(w1) else 0 
        w2_count =  fetch(w2)[0].count if fetch(w2) else 0 

        combined = w2 + "|" + w1 if w1 > w2 else w1 + "|" + w2
        combined_count =  fetch(combined)[0].count if fetch(combined) else 0


        if (metric == "pmi") or (metric == "npmi"):
            if w1_count == 0 or w2_count == 0 or combined_count == 0:
                result = 0.0
            else:
                result = math.log((float(combined_count)*float(window_total))/ \
                    float(w1_count*w2_count), 10)
                if metric == "npmi":
                    result = result / (-1.0*math.log(float(combined_count)/(window_total),10))

        return result

    window_total =  fetch(WTOTALKEY)[0].count if fetch(WTOTALKEY) else 0

    topic = topic.strip()
    topic_words = topic.split()
    topic_assoc = []
    for w1_id in range(0, len(topic_words)-1):
        target_word = topic_words[w1_id]
        #remove the underscore and sub it with space if it's a collocation/bigram
        w1 = " ".join(target_word.split(colloc_sep))
        for w2_id in range(w1_id+1, len(topic_words)):
            topic_word = topic_words[w2_id]
            #remove the underscore and sub it with space if it's a collocation/bigram
            w2 = " ".join(topic_word.split(colloc_sep))
            if target_word != topic_word:
                topic_assoc.append(calc_pair(w1, w2, metric))

    return float(sum(topic_assoc))/len(topic_assoc)



def model_coherence(topics, metric, topns):

    #read the topic file and compute the observed coherence

    top_coherence = defaultdict(list) # {topicid: [tc]}
    topic_tw = {} #{topicid: topN_topicwords}
    for topic_id, line in enumerate(topics):
        topic_list = line.split()[:max(topns)]
        topic_tw[topic_id] = " ".join(topic_list)
        for n in topns:
            top_coherence[topic_id].append(topic_coherence(" ".join(topic_list[:n]), metric))

    #sort the topic coherence scores in terms of topic id
    response = {}
    tc_items = sorted(top_coherence.items())
    mean_coherence_list = []
    for item in tc_items:
        topic_words = topic_tw[item[0]].split()
        mean_coherence = np.mean(item[1])
        mean_coherence_list.append(mean_coherence)
        response[topic_tw[item[0]]] = mean_coherence

    response['mean'] = np.mean(mean_coherence_list)
    response['median'] = np.median(mean_coherence_list)

    return response






