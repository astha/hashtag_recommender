import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

stopWordListFileName="stopwords.txt"
slangDictFileName = "slangDict.txt"

stopWords=[]
slangDict={}


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
  val = re.search(r".*(#\w+)",tweet)
  if(val is None):
    return False
  else:
    return True

def retrieveHashTags(tweet):
  pattern=re.compile(r"#[\w_-]+")
  return [ h.lower() for h in pattern.findall(tweet)]


def processTweet(tweet):
  #Convert @username to ""
  tweet = re.sub('@[\S]+','',tweet)

  if(not ContainsHashTag(tweet)):
    return ""
  #Convert www.* or https?://* to URL
  tweet = re.sub('((www\.[\S]+)|(https?://[\S]+))','URL',tweet)
  
  #trim the appearing punctuations from begin and end of tweet
  tweet = tweet.strip('\'"?.,!')
  # remove punctuation from tweet
  tweet = re.sub('[-\'"]','',tweet)
  #Remove additional white spaces
  tweet = re.sub('[\s]+', ' ', tweet)
  return tweet

def readSlangDictionary():
  slangDict={}
  f=open(slangDictFileName,'r')
  lines = f.readlines()
  for line in lines:
    arr=line.split(":")
    slangDict[arr[0].strip()]=arr[1].strip()
  f.close()
  return slangDict

def getFeatures(tweet):
  featureVector = []
  # print tweet
  tweet = tweet.replace('\\', ' ')
  words = re.split('[?,.;:~"* !/]+', tweet)
  for w in words:

    arr=w.split('#')
    if(arr[0]!=""):
      #replace two or more with one occurrence
      w = replaceThreeOrMore(arr[0])
      #strip punctuation
      w = w.strip('\'"?,.-*;')
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
  return featureVector

def getVocabulary(features):
  vocabulary = dict()
  vocabCount = 0
  for feature in features:
    for word in feature:
      if not word in vocabulary.keys():
        vocabulary[word] = vocabCount
        vocabCount += 1
  return vocabulary

def getWordFrequency(features):
  wordFreqMap = dict()
  for feature in features:
    for word in feature:
      if wordFreqMap.has_key(word):
        wordFreqMap[word] += 1
      else:
        wordFreqMap[word] = 1
  return wordFreqMap

def calculateHashtagFrequency(processedHashTags):
  hashtagFreqMap = {}
  for hashtagList in processedHashTags:
    for hashEle in hashtagList:
      if hashtagFreqMap.has_key(hashEle):
        hashtagFreqMap[hashEle] += 1
      else:
        hashtagFreqMap[hashEle] = 1
  return hashtagFreqMap

def hashTagMaps(processedTweets, processedHashTags):
  hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
  hashtagToWordFreq = {}
  vocabulary = getVocabulary(processedTweets)
  vocabularyCount = len(vocabulary.keys())
  for i in range(len(processedHashTags)):
    hashtagList = processedHashTags[i]
    for hashtag in hashtagList:
      if not hashtagToWordFreq.has_key(hashtag):
        hashtagToWordFreq[hashtag] = [0]*vocabularyCount
      for word in set(processedTweets[i]):
        hashtagToWordFreq[hashtag][vocabulary[word]] += 1
  return hashtagFreqMap, hashtagToWordFreq

def initialize():
  global stopWords
  stopWords = getStopWords()
  global slangDict
  slangDict = readSlangDictionary()

def compareHashtagsForTweet(actualTweetHashtags, recommendedTweetHashtags):
  if len(set(actualTweetHashtags) & set(recommendedTweetHashtags)):
    return True 
  else:
    return False

def plotHashtagFreqDistribution(hashtagFreqMap):
  x_axis = [x+1 for x in range(25)]
  y_axis = [0] * 25
  total_hashtags = sum(hashtagFreqMap.values())
  num_hashtags = len(hashtagFreqMap.keys())
  for key in hashtagFreqMap.keys():
    if hashtagFreqMap[key] <= 25:
      y_axis[hashtagFreqMap[key] - 1] += 1

  fig, ax1 = plt.subplots()
  title = 'Number of Hashtags v/s Number of Hashtag Occurences\n'
  title += 'Total HashTags = ' + str(total_hashtags) + ', '
  title += 'Different Hashtags = ' + str(num_hashtags)
  plt.suptitle(title)
  plt.xlabel("Hashtag Occurence")
  ax1.set_ylabel("Number of Hashtags")
  ax1.plot(x_axis, y_axis, marker='o', color='g')
  ax1.plot(x_axis, y_axis, color='g')
  for tl in ax1.get_yticklabels():
    tl.set_color('g')

  ax2 = ax1.twinx()
  y_axis = np.cumsum(y_axis)
  ax2.set_ylabel('Cumulative Occurence')
  ax2.plot(x_axis, y_axis, marker='o', color='b')
  ax2.plot(x_axis, y_axis, color='b')
  for tl in ax2.get_yticklabels():
    tl.set_color('b')
  plt.grid()
  plt.savefig("hashtag_freq.png")
  plt.clf()

  # freqMap[hashtagFreqMap[key]] += 1
  # print [(key, num) for key,num in astha]
  # print freqMap
  # exit(0)
