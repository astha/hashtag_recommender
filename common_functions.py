


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
  tweet = re.sub('[?,."!]','',tweet)
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
