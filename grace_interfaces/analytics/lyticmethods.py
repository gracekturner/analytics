from .models import *
from decimal import *
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from itertools import combinations
import re
import networkx as nx
#from nltk.corpus import wordnet as wn

## takes a list of text objects and builds a topic fingerprint for each, then reverse index for ""
## originally used wordnet etc. but the performance value for that is shit. (~6x worse) Pythonanywhere times out.
## so now it looks at basic words without getting very fancy. It looks at it by sentence tho.
def topic_fingerprint_builder(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Finger_Print_" + set_name):
        return id_object.properties.filter(title = "Finger_Print_" + set_name)[0]
    results = {}
    count = 0

    for each in list_of_text_objects:

        if each == id_object: continue
        count +=1
        sentences = sent_tokenize(each.text)

        for sentence in sentences:
            text = pos_tag(word_tokenize(sentence))

            word_count = {}
            for word in text:
                if word[0] in ["are", "is", "have", "not", "has", "do", "be", "am"]:
                    continue
                if len(word) != 2: continue
                pos = word[1]
                word = word[0]
                syn = []
                if pos == "NN" or pos == "VB" or pos == "VBP" or pos == "JJ" or pos == "RB":
                    if word not in word_count:
                        word_count[word] = 0
                    word_count[word] +=1
            fprint = sorted(word_count, key = word_count.get)[-3:]

            for each in fprint:
                if each not in results:
                    results[each] = {}
                    results[each]["count"] = 0
                    results[each]["ids"] = set()
                results[each]["ids"].add(count)
                results[each]["count"] = len(results[each]["ids"])


    #print results
    if not id_object.properties.filter(title = "Finger_Print_" + set_name):
        p = Property(title = "Finger_Print_" + set_name, description = repr(results))
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Finger_Print_" + set_name)[0]
        p.description = repr(results)
        p.save()
    return p

def topic_fingerprint_builder_old(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Finger_Print_" + set_name):
        #id_object.properties.filter(title = "Finger_Print_" + set_name)[0].delete()
        return id_object.properties.filter(title = "Finger_Print_" + set_name)[0]
    results = {}
    count = 0
    for each in list_of_text_objects:
        if each == id_object: continue
        count +=1
        text = word_tokenize(each.text)
#        text = pos_tag(text)
        text = [word for word in text if word not in stopwords.words('english')]
        synsets = {}
        word_count = {}
        for word in text:
            if word:
#                pos = wordnet.morphy(word[1])
                try:
                    w = wn.morphy(word)
                except:
                    continue

                if word:
                    syn = wn.synsets(word)
                    if word not in word_count:
                        word_count[word] = 0
                        synsets[word] = syn
                    word_count[word] +=1
        word_pairs = combinations(sorted(synsets), 2)
        result = {}
        for each in word_pairs:
            for a,b in zip(synsets[each[0]],synsets[each[1]]):
                if a.wup_similarity(b) > 0.65:
                    result[each] = word_count[each[0]] + word_count[each[1]]

        result.update(word_count)
        fprint = sorted(result, key = result.get)[-3:]

        for each in fprint:
            if each not in results:
                results[each] = {}
                results[each]["count"] = 0
                results[each]["ids"] =set()
            results[each]["count"] +=1
            results[each]["ids"].add(count)

    #print results
    if not id_object.properties.filter(title = "Finger_Print_" + set_name):
        p = Property(title = "Finger_Print_" + set_name, description = repr(results))
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Finger_Print_" + set_name)[0]
        p.description = repr(results)
        p.save()
    return p

# takes a list of Text objects, the array of id_object(s) associated with that dataset,
# and the title of the dataset ("set_name") for identification.
def similarity_opt(pair):
    one = pair[0]
    two  = pair[1]
    inter = one.intersection(two)
    uni = one.union(two)
    return Decimal(len(inter))/(Decimal(len(uni)))

def word_bags_freq(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Word_Bag_Freq_" + set_name):
        return id_object.properties.filter(title = "Word_Bag_Freq_" + set_name)[0]
    result_wordbag = []
    count = 0
    ## process the data into word bags (sets of unique words, not including stopwords)
    for each in list_of_text_objects:
        if each == id_object: continue
        text = word_tokenize(each.text)
        text = [word for word in text if word not in stopwords.words('english')]
        dicty = {}
        for word in text:
            if word not in dicty:
                dicty[word] = 0
            dicty[word] += 1

        result_wordbag.append(dicty)

    result_wordbag = repr(result_wordbag)

    ## if not done, add to properties ##
    if not id_object.properties.filter(title = "Word_Bag_Freq_" + set_name):
        p = Property(title = "Word_Bag_Freq_" + set_name, description = result_wordbag)
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Word_Bag_Freq_" + set_name)[0]
        p.description = result_wordbag
        p.save()
    return p

def topic_similarity_score(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Topic_Score_" + set_name ):
        return
    wb = word_bags_freq(list_of_text_objects, id_object, set_name)
    print wb


def sentiment(list_of_text_objects, id_object, set_name):

    # if they already have the score for this dataset, return ####note: may need to update
    #this in case of updating a dataset
    if id_object.properties.filter(title = "Sentiment_Score_" + set_name ):
        return
    # set up sentiment analyzer
    sid = SentimentIntensityAnalyzer()
    pos = 0
    neg = 0
    neu = 0
    # for each text object
    for each in list_of_text_objects:
        # check if one of the objects associated is the id object(s), if so,
        # skip
        if id_object  == each:
            continue

        #get sentences out of (possibly) multiple paragraphs of data
        entry = each.text
        pgs= entry.split("\n")
        total = 0
        count = 0
        for pg in pgs:
            lines_list = tokenize.sent_tokenize(pg)
            for sentence in lines_list:

                #get the compound score for the sentence
                description = ""
                #create sentiment scores
                ss = sid.polarity_scores(sentence)
                total += Decimal(ss["compound"])
                count +=1
        # build an average over all the sentences in the text object, create property object associated
        # with that ID
        if count != 0:
            avg = Decimal(Decimal(total)/Decimal(count))
        if count == 0:
            continue
        if avg < 0:
            neg +=1
        if avg > 0:
            pos+=1
        if avg == 0:
            neu +=1

    # add summary property to the text
    if not id_object.properties.filter(title = "Sentiment_Score_" + set_name):
        p = Property(title = "Sentiment_Score_" + set_name, description = "Negative Texts: \n" + str(neg) + "\n Positive Texts: \n" + str(pos) + "\n Neutral Texts: \n" + str(neu))
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Sentiment_Score_" + set_name)[0]
        p.description = "Negative Texts: \n" + str(neg) + "\n Positive Texts: \n" + str(pos) + "\n Neutral Texts: \n" + str(neu)
        p.save()

def categorizer(list_of_text_objects, keywords, id_object, set_name):
    dictionary = {}
    dictionary["Uncategorized"] = set()
    for each in keywords:
        dictionary[keywords[each]] = set()
    ## get set of texts that belong to each category ##
    found = False

    #count = 0
    for each in list_of_text_objects:
        if each == id_object: continue
        for word in keywords:
            if re.search(word, each.text, re.IGNORECASE):
                dictionary[keywords[word]].add(each)

                found = True
        if not found:
            dictionary["Uncategorized"].add(each)
        found = False

    ## get frequencies for each category ##
    freq = ""
    for key in dictionary:
        freq += str(key) + "\n" + str(len(dictionary[key])) + "\n"

    ## if already done, replace ##
    if id_object.properties.filter(title = "Category_Score_" + set_name):
        p = id_object.properties.filter(title = "Category_Score_" + set_name)[0]
        p.description = freq
        p.save()
    ## if not done, create new ##
    else:
        p = Property(title = "Category_Score_" + set_name, description = freq)
        p.save()
        id_object.properties.add(p)
    return p

def word_bags(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Word_Bag_" + set_name):
        #id_object.properties.filter(title = "Word_Bag_" + set_name)[0].delete()
        return id_object.properties.filter(title = "Word_Bag_" + set_name)[0]
    result_wordbag = []
    count = 0
    ## process the data into word bags (sets of unique words, not including stopwords)
    for each in list_of_text_objects:
        if each == id_object: continue
        text = word_tokenize(each.text)
        text = [word for word in text if word not in stopwords.words('english')]
        textset = set(text)
        result_wordbag.append(textset)
        #result_wordbag+= repr(textset) + "\n" + str(count) + "\n"
        #count+=1
    result_wordbag = repr(result_wordbag)
    ## if not done, add to properties ##
    if not id_object.properties.filter(title = "Word_Bag_" + set_name):
        p = Property(title = "Word_Bag_" + set_name, description = result_wordbag)
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Word_Bag_" + set_name)[0]
        p.description = result_wordbag
        p.save()
    return p

def similarity_score2(list_of_text_objects, id_object, set_name):
    if id_object.properties.filter(title = "Similarity_Score_" + set_name):
        return
        #id_object.properties.filter(title = "Similarity_Score_" + set_name)[0].delete()
    wb = word_bags(list_of_text_objects, id_object, set_name).description


    wb = eval(wb)
    ids = range(len(wb))

    pairs = list(combinations(wb, 2))
    vals = list(combinations(ids, 2))
    result = []



    for i in range(0, len(pairs)):
        sim_score = similarity_opt(pairs[i])
        if sim_score >= 0.1:
            result.append(vals[i])
    G=nx.Graph()
    G.add_nodes_from(range(len(ids)))
    G.add_edges_from(result)
    pos = nx.fruchterman_reingold_layout(G)

    newdict = {}
    for i in pos:
        ax1 = pos[i][0]
        ax2 = pos[i][1]
        string = str(ax1) + "," + str(ax2)
        newdict[i] = string

    ## figure out how to represent "array()" and dict as string and back again
    result = repr(result) + "\n" + str(len(ids)) + "\n" + repr(newdict)
    #print result


    if not id_object.properties.filter(title = "Similarity_Score_" + set_name):
        p = Property(title = "Similarity_Score_" + set_name, description = result)
        p.save()
        id_object.properties.add(p)
    else:
        p = id_object.properties.filter(title = "Similarity_Score_" + set_name)[0]
        p.description = result
        p.save()


