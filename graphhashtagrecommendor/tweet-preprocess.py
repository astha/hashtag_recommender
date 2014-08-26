import re
import operator
import numpy as np
import sys

stopWordListFileName="stopwords.txt"
hashtagsFileName="hashtags"
tweetsFileName="tweets"
slangDictFileName = "slangDict.txt"

slangDict={}
stopWords=[]

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

def processTweet(tweet):
    if(not ContainsHashTag(tweet)):
        return None
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\S]+)|(https?://[\S]+))','URL',tweet)
    #Convert @username to null
    tweet = re.sub('@[\S]+','at_user',tweet)
    #trim the appearing punctuations from begin and end of tweet
    tweet = tweet.strip('\'":?.,!')
    # remove punctuation from tweet
    tweet = re.sub('[?,.:"!]','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace non-ascii characters
    tweet = re.sub(r'[^\x00-\x7F]','', tweet)
    return tweet

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

def readSlangDictionary():
    slangDict={}
    f=open(slangDictFileName,'r')
    lines = f.readlines()
    for line in lines:
        arr=line.split(":")
        slangDict[arr[0].strip()]=arr[1].strip()
    f.close()
    return slangDict

def getFeatureWords(tweet):
    featureTweet = ""
    hashTags = []
    words = tweet.split()
    for w in words:
        arr=w.split('#')
        if(arr[0]!=""):
            # processing the word which is a non-hashtag.

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
                            featureTweet += " " + word
                else:
                    featureTweet += " " + w

        # the word is a hashtag
        for index in range(1,len(arr)):
            # will come here iff 'w' is of the type [#sachin, you#sir, you#sir#great]
            hashTags.append("#" + arr[index])
            featureTweet += " " + arr[index]

    hashTags = [tag for tag in hashTags if re.match('#[\w_-]+', tag)]
    if len(hashTags) == 0:
        return (None, None)
    else:
        return (featureTweet, ' '.join(hashTags))


def initialize():
    global stopWords
    stopWords = getStopWords()
    global slangDict
    slangDict = readSlangDictionary()


def main(argv):
    initialize()
    global hashtagsFileName, tweetsFileName
    hashtagFile = open(hashtagsFileName,'w')
    featureWordsFile = open(tweetsFileName,'w')
    fp = open(argv[0], 'r')
    tweet = fp.readline()
    while tweet:
        tweet = processTweet(tweet)
        if tweet is not None:
            (featureTweet, hashtags) = getFeatureWords(tweet)
            if hashtags is not None:
                featureTweet += '\n'
                hashtags += '\n'
                featureWordsFile.write(featureTweet)
                hashtagFile.write(hashtags)
        tweet = fp.readline()

if __name__ == "__main__":
    main(sys.argv[1:])