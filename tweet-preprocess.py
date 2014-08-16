import re
import operator
import numpy as np
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

stopWords=[]
stopWordListFileName="stopwords.txt"
def getStopWords():
    stopWords = []
    stopWords.append("at_user")
    stopWords.append("url")

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords

def replaceThreeOrMore(word):
    pattern = re.compile(r"(.)\1\1+", re.DOTALL) #re.DOTALL means . represents any character including '\n'
    return pattern.sub(r"\1", word)

def ContainsHashTag(tweet):
    val = re.search(r".*(#.+)",tweet)
    if(val is None):
        return False
    else:
        return True

def retrieveHashTags(tweet):
    pattern=re.compile(r"#[\w_-]+")
    return pattern.findall(tweet)


def processTweet(tweet):
    if(not ContainsHashTag(tweet)):
        return ""
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\S]+)|(https?://[\S]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[\S]+','AT_USER',tweet)
    #trim the appearing punctuations from begin and end of tweet
    tweet = tweet.strip('\'"?.,!')
    # remove punctuation from tweet
    tweet = re.sub('[?,."!]','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    return tweet

slangDictFileName = "slangDict.txt"
slangDict={}

hashtag_map = {}
hashtag_count = 0
hashtag_freq = {}
hashtag_to_word = {}

word_map = {}
word_count = 0
word_freq = {}

def readSlangDictionary():
    slangDict={}
    f=open(slangDictFileName,'r')
    lines = f.readlines()
    for line in lines:
        arr=line.split(":")
        slangDict[arr[0].strip()]=arr[1].strip()
    f.close()
    return slangDict

def getFeatureVector(tweet):
    featureVector = []
    words = tweet.split()
    for w in words:

        arr=w.split('#')
        if(arr[0]!=""):
            #replace two or more with one occurrence
            w = replaceThreeOrMore(arr[0])
            #strip punctuation
            w = w.strip('\'"?,.-')
            #the word should start with alphabet or it should be a hashtag
            val = re.search(r"(^[#a-zA-Z])", w)
            w = w.lower()

            #ignore if it is a stop word
            if(w in stopWords or val is None):
                continue
            else:
                # if you want to add stemming, uncomment line below
                # w = stemmer.stem(w)
                if w in slangDict.keys():
                    replacementWord = slangDict[w]
                    for word in replacementWord.split():
                        if not word.lower() in stopWords:
                            featureVector.append(word.lower())
                else:
                    featureVector.append(w)


        for index in range(1,len(arr)):
            # will come here iff 'w' is of the type [#sachin, you#sir, you#sir#great]
            hashtagWord = arr[index]
            featureVector.append(hashtagWord)

    return featureVector

def initialize():
    global stopWords
    stopWords = getStopWords()
    global slangDict
    slangDict = readSlangDictionary()

def addToHashtagMap(hashTags):
    global hashtag_map, hashtag_count, hashtag_freq, hashtag_to_word
    for word in hashTags:
        if not hashtag_map.has_key(word):
            hashtag_map[word] = hashtag_count
            hashtag_count = hashtag_count + 1
            hashtag_freq[word] = 0
            hashtag_to_word[word] = []
        hashtag_freq[word] += 1

def addToWordMap(featureVector): 
    global word_map, word_count, word_freq
    for word in featureVector:
        if not word_map.has_key(word):
            word_map[word] = word_count
            word_count = word_count + 1
            word_freq[word] = 0
        word_freq[word] += 1 

# t1 = "hey man how hey #People  aRe you#sachin ? @you weren't awesome 1lawesome days awwwesome  moving !!!"
# t2 = "you #love awwwesome!!!! ASAP you-#21Guns #love-you-sachin"
# t3 = "@PrincessSuperC Hey Cici #xxx sweetheart! Just wanted to let u know I luv u! OH! and will the mixtape drop soon? FANTASY RIDE MAY 5TH!!!!  "
tarr = []
fp = open("tweets", 'r')
line = fp.readline()
while line:
    tarr.append(line)
    line = fp.readline()
fp.close()

num_features = []

def preProcessAllTweets(tweetArray, hashtagFileName, wordsFileName):
    initialize()
    global num_features, word_count
    # hashtagFile = open(hashtagFileName,'w')
    # wordsFile = open(wordsFileName,'w')

    for tweet in tweetArray:
        processedTweet = processTweet(tweet)
        hashTags = retrieveHashTags(processedTweet)
        featureVector = getFeatureVector(processedTweet)
        addToWordMap(featureVector)
        addToHashtagMap(hashTags)
        new_feature = [0] * word_count

        # in how many tweets does a word occur given a specific hashtag
        for word in set(featureVector):
            new_feature[word_map[word]] += 1
            for tag in hashTags:  
                hashtag_to_word[tag].extend([0]*(word_count-len(hashtag_to_word[tag])))
                hashtag_to_word[tag][word_map[word]] += 1
     
        num_features.append(new_feature)
        # hashtagFile.write(str(hashTags)+"\n")
        # wordsFile.write(str(featureVector)+"\n")
    
    # hashtagFile.close()
    # wordsFile.close()
    map(lambda x: x.extend([0]*(word_count-len(x))), num_features)

preProcessAllTweets(tarr,"h.txt","w.txt")

# resize array for all hashtags
hashtags = hashtag_map.keys()
for tag in hashtags:  
    hashtag_to_word[tag].extend([0]*(word_count-len(hashtag_to_word[tag])))

fp = open("here", 'r')
total_hashtags = sum(list(hashtag_freq.values()))
for feature in num_features: 
    line = fp.readline()
    print("\n--------------------\n")
    print(line)
    probability = {}
    for tag in hashtags:
        probability[tag] = 1.0
        # probability[tag] = float(hashtag_freq[tag]) / total_hashtags
        # uncomment this to allow probability prior based on freq of hashtag (bad results)
        for i in range(0, len(feature)):
            if feature[i]:
                if (hashtag_to_word[tag][i]):
                    probability[tag] *= float(hashtag_to_word[tag][i])  / hashtag_freq[tag]
                else:
                    probability[tag] *= 0.95
    sorted_prob = sorted(probability.iteritems(), key=operator.itemgetter(1))
    # print(sorted_prob)
    best_match = sorted_prob[-5:]
    best_match = reversed(best_match)
    best_match = [i[0] for i in best_match]
    print(best_match)

fp.close()






