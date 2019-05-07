import sys
import os
import codecs
import threading
import random
from multiprocessing import Pool
from .models import WordCount
 
######## Trick for multiprocessing on nested functions. ###############
# https://gist.github.com/EdwinChan/3c13d3a746bb3ec5082f
def generate_name(length=10, module=None):
  if module is None:
    module = sys.modules[__name__]
  while True:
    name = 'id{:0{length}d}'.format(random.randint(0, 10**length-1),
      length=length)
    if not hasattr(module, name):
      return name

def global_function(func):
  module = sys.modules[func.__module__]
  func.__name__ = func.__qualname__ = generate_name(module=module)
  setattr(module, func.__name__, func)
  return func
#######################################################################



def calculate_word_count(topic, window_size = 20, debug = False):
    '''
        topic -> space separated words forming the topic
        window_size -> size of the sliding window, use 0 to take each document as a window    
    '''
        


    ref_corpus_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref_corpus')
    colloc_sep = "_" #symbol for concatenating collocations
    TOTALWKEY = "!!<TOTAL_WINDOWS>!!" #key name for total number of windows (in wordcount)


    topic_word_rel = {} # related topic words, e.g. { "space": set(["space", "earth", ...]), ... }
    unigram_list = [] # a list of unigrams (from topic words and candidates)
    unigram_rev = {} # a reverse index of unigram_list
    word_count = {} # word counts (both single and pair)
    corpus_partitions = [] # a list of the partitions (files) of the corpus

    #locks
    wc_lock = threading.Lock()

    ####################
    #call back function#
    ####################
    @global_function
    def calcwcngram_complete(worker_wordcount):
        wc_lock.acquire()
        global num_comp
        global ord_count

        #update the wordcount from the worker
        for k, v in worker_wordcount.items():
            curr_v = 0
            if k in word_count:
                curr_v = word_count[k]
            curr_v += v
            word_count[k] = curr_v

        wc_lock.release()


    ##################
    #worker functions#
    ##################
    def convert_to_index(wordlist, unigram_rev):
        ids = []

        for word in wordlist.split():
            if word in unigram_rev:
                ids.append(unigram_rev[word])
            else:
                ids.append(0) 

        return ids

    def update_word_count(word, worker_wordcount):
        count = 0
        if word in worker_wordcount:
            count = worker_wordcount[word]
        count += 1
        worker_wordcount[word] = count

        if debug:
            print ("\tupdating word count for =", word)

    def update_pair_word_count(w1, w2, topic_word_rel, worker_wordcount):
        if (w1 in topic_word_rel and w2 in topic_word_rel[w1]) or \
            (w2 in topic_word_rel and w1 in topic_word_rel[w2]):
            if w1 > w2:
                combined = w2 + "|" + w1
            else:
                combined = w1 + "|" + w2
            update_word_count(combined, worker_wordcount)

    def get_ngrams(words, topic_word_rel):
        if debug:
            for word in words:
                if word > 0:
                    print (word, "=", unigram_list[word-1])

        all_ngrams = []
        ngram = []
        for i in range(0, len(words)):
            if (words[i] == 0):
                if len(ngram) > 0:
                    all_ngrams.append(ngram)
                    ngram = []
            else:
                ngram.append(unigram_list[words[i]-1])
        #append the last ngram
        if len(ngram) > 0:
            all_ngrams.append(ngram)
            ngram = []

        #permutation within ngrams
        ngrams_perm = []
        for ngram in all_ngrams:
            for i in range(1, len(ngram)+1):
                for j in range(0, len(ngram)-i+1):
                    comb = [ item for item in ngram[j:j+i] ]
                    ngrams_perm.append(' '.join(comb))

        #remove duplicates -->COMMENT TO BE REPETITION SENSITIVE!!
        ngrams_perm = list(set(ngrams_perm))

       
        #only include ngrams that are found in topic words
        ngrams_final = []
        for ngram_perm in ngrams_perm:
            if ngram_perm in topic_word_rel:
                ngrams_final.append(ngram_perm)
        

        return ngrams_final

    #calculate word counts, given a list of words
    def calc_word_count(words, topic_word_rel, unigram_list, worker_wordcount):

        ngrams = get_ngrams(words, topic_word_rel)
        if debug:
            print ("\nngrams =", ngrams, "\n")

        for ngram in ngrams:
            if (ngram in topic_word_rel):
                update_word_count(ngram, worker_wordcount)

        for w1_id in range(0, len(ngrams)-1):
            for w2_id in range(w1_id+1, len(ngrams)):
                if(ngrams[w1_id] != ngrams[w2_id]):
                    if debug:
                        print ("\nChecking pair (", ngrams[w1_id], ",", ngrams[w2_id], ")")
                    update_pair_word_count(ngrams[w1_id], ngrams[w2_id], topic_word_rel, worker_wordcount)

    #primary worker function called by threading pool
    @global_function
    def calcwcngram(worker_num, window_size, corpus_file, topic_word_rel, unigram_list, unigram_rev):
        #now process the corpus file and sample the word counts
        line_num = 0
        worker_wordcount = {}
        total_windows = 0

        #sys.stderr.write("Worker " + str(worker_num) + " starts: " + str(time.time()) + "\n")
        for line in codecs.open(corpus_file, "r", "utf-8"):
            #convert the line into a list of word indexes
            words = convert_to_index(line, unigram_rev)

            if debug:
                print ("====================================================================")
                print ("line =", line)
                print ("words =", " ".join([ str(item) for item in words]))

            
            doc_len = len(words)
            #number of windows
            if window_size > 0:
                num_windows = doc_len + window_size - 1
            else:
                num_windows = 1
            #update the global total number of windows
            total_windows += num_windows

            for tail_id in range(1, num_windows+1):
                if window_size != 0:
                    head_id = tail_id - window_size
                    if head_id < 0:
                        head_id = 0
                    words_in_window = words[head_id:tail_id]
                else:
                    words_in_window = words

                if debug:
                    print ("=========================")
                    print ("line_num =", line_num)
                    print ("words_in_window =", " ".join([ str(item) for item in words_in_window ]))

                calc_word_count(words_in_window, topic_word_rel, unigram_list, \
                    worker_wordcount)

                

            line_num += 1

        #update the total windows seen for the worker
        worker_wordcount[TOTALWKEY] = total_windows

        return worker_wordcount

    ################
    #main functions#
    ################
    #update the topic word - candidate words relation dictionary
    def update_topic_word_rel(w1, w2):
        related_word_set = set([])
        if w1 in topic_word_rel:
            related_word_set = topic_word_rel[w1]
        if w2 != w1:
            related_word_set.add(w2)

        topic_word_rel[w1] = related_word_set
        

    #get the partitions of all existing reference corpus
    for d in os.listdir(ref_corpus_dir):
        if not d.startswith("."):
            for f in os.listdir(ref_corpus_dir + "/" + d):
                if not f.startswith("."):
                    corpus_partitions.append(ref_corpus_dir + "/" + d + "/" + f)


    if (type(topic) == list):    
        topic_file = topic
    elif (type(topic) == str):
        topic_file = [topic]
    else:
        pass
        # ERRO 
          
    #process the topic file and get the topic word relation
    unigram_set = set([]) #a set of all unigrams from the topic words
    for line in topic_file:
        line = line.strip()

        topic_words = line.split()

        #update the unigram list and topic word relation
        for word1 in topic_words:
            #update the unigram first
            for word in word1.split(colloc_sep):
                unigram_set.add(word)

            #update the topic word relation
            for word2 in topic_words:
                if word1 != word2:
                    #if it's collocation clean it so it's separated by spaces
                    cleaned_word1 = " ".join(word1.split(colloc_sep))
                    cleaned_word2 = " ".join(word2.split(colloc_sep))
                    update_topic_word_rel(cleaned_word1, cleaned_word2)

    
    #sort the unigrams and create a list and a reverse index
    unigram_list = sorted(list(unigram_set))
    unigram_rev = {}
    unigram_id = 1
    for unigram in unigram_list:
        unigram_rev[unigram] = unigram_id
        unigram_id += 1



    
    # check for pre-existing word-relations in the DB and removing them
    for word in topic_word_rel:
        to_remove = []
        for related in topic_word_rel[word]:
            combined = related + "|" + word if word > related else word + "|" + related
            if WordCount.objects.filter(word=combined):
                to_remove.append(related)
        [topic_word_rel[word].remove(i) for i in to_remove]
    to_remove = []
    for word in topic_word_rel:
        if not topic_word_rel[word]:
            if WordCount.objects.filter(word=word):
                to_remove.append(word)
    [topic_word_rel.pop(i) for i in to_remove]
    
    if not topic_word_rel:
        return {}
    print("topic_word_rel:", str(topic_word_rel))

    #spawn multiple threads to process the corpus
    po = Pool()
    for i, cp in enumerate(corpus_partitions):
        # sys.stderr.write("creating a thread for corpus partition " + cp + "\n")
        # sys.stderr.flush()
        po.apply_async(calcwcngram, (i, window_size, cp, topic_word_rel, unigram_list, unigram_rev,), \
            callback=calcwcngram_complete)
        
    po.close()
    po.join()

    for word in word_count:
        if not WordCount.objects.filter(word=word):
            WordCount(word=word,count=word_count[word]).save()

    print(word_count)

    # retornar vazio se só tiver TOTALWINDOWS
    return word_count

