import re
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

t1 = "hey man how  #People  aRe you#sachin ? @you weren't awesome 1lawesome days awwwesome  moving !!!"
t3 = "@PrincessSuperC Hey Cici #xxx sweetheart! Just wanted to let u know I luv u! OH! and will the mixtape drop soon? FANTASY RIDE MAY 5TH!!!!  "
t2 = "you #love awwwesome!!!! ASAP you-#21Guns #love-you-sachin"
tarr= [t1,t2,t3]

def preProcessAllTweets(tweetArray, hashtagFileName, wordsFileName):
    initialize()
    hashtagFile = open(hashtagFileName,'w')
    wordsFile = open(wordsFileName,'w')

    for tweet in tweetArray:
        processedTweet = processTweet(tweet)
        hashTags = retrieveHashTags(processedTweet)
        featureVector = getFeatureVector(processedTweet)
        hashtagFile.write(str(hashTags)+"\n")
        wordsFile.write(str(featureVector)+"\n")
    hashtagFile.close()
    wordsFile.close()

preProcessAllTweets(tarr,"h.txt","w.txt")




