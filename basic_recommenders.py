import re
import nltk
import operator
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import copy
import sys
# from nltk.stem.snowball import SnowballStemmer
# stemmer = SnowballStemmer("english")
endl = "\n"

processedHashTags = []
processedTweets = []


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
	print "getVocabulary()", endl
	vocabulary = dict()
	vocabCount = 0
	for feature in features:
		for word in feature:
			if not word in vocabulary.keys():
				vocabulary[word] = vocabCount
				vocabCount += 1
	return vocabulary

def getWordFrequency(features):
	print "getWordFrequency()..", endl
	wordFreqMap = dict()
	for feature in features:
		for word in feature:
			if wordFreqMap.has_key(word):
				wordFreqMap[word] += 1
			else:
				wordFreqMap[word] = 1
	return wordFreqMap

# presence feature vector
def createPresenceFeatureVectors(features):
	vocabulary = getVocabulary(features)
	featureVectors = []
	for feature in features:
		featureVector = [0]*vocabularyCount
		for word in feature:
			featureVector[vocabulary[word]] = 1
		featureVectors.append(featureVector)
	return featureVectors, vocabulary

def createPresenceFeatureVectors(features, vocabulary):
	featureVectors = []
	for feature in features:
		featureVector = [0]*vocabularyCount
		for word in feature:
			featureVector[vocabulary[word]] = 1
		featureVectors.append(featureVector)
	return featureVectors

# tf feature vector
def createTFFeatureVectors(features):
	vectorizer = CountVectorizer()
	textFeatures = [' '.join(feature) for feature in features]
	return vectorizer.fit_transform(textFeatures).toarray(), vectorizer.vocabulary

# tfidf feature vector
def createTFIDFFeatureVectors(features):
	vectorizer = CountVectorizer()
	textFeatures = [' '.join(feature) for feature in features]
	tf_features = vectorizer.fit_transform(textFeatures).toarray()
	vocabulary = vectorizer.vocabulary_
	transformer = TfidfTransformer()
	tfidf_features = transformer.fit_transform(tf_features).toarray()
	return tfidf_features,vocabulary

def initialize():
	global stopWords
	stopWords = getStopWords()
	global slangDict
	slangDict = readSlangDictionary()

tarr = []
filename = sys.argv[1]
fp = open(filename, 'r')
line = fp.readline()
while line:
	tarr.append(line)
	line = fp.readline()
fp.close()

def preProcessAllTweets(tweetArray, hashtagFileName, wordsFileName):
	print "Pre Processing Begins...", endl
	initialize()
	hashtagFile = open(hashtagFileName,'w')
	wordsFile = open(wordsFileName,'w')
	global processedHashTags, processedTweets
	processedTweets = [];
	processedHashTags = [];
	for tweet in tweetArray:
		
		processedTweet = processTweet(tweet)
		if(processedTweet == ""):
			continue
		feature = getFeatures(processedTweet)
		if len(feature) == 0:
			continue
		hashtagList = retrieveHashTags(processedTweet)

		processedHashTags.append(hashtagList)
		processedTweets.append(feature)	
	hashtagFile.close()
	wordsFile.close()
	print "Pre Processing ends..", endl

def calculateHashtagFrequency(processedHashTags):
	print "hashtag frequency\n"
	hashtagFreqMap = {}
	for hashtagList in processedHashTags:
		for hashEle in hashtagList:
			if hashtagFreqMap.has_key(hashEle):
				hashtagFreqMap[hashEle] += 1
			else:
				hashtagFreqMap[hashEle] = 1
	return hashtagFreqMap



def test(processedHashTags, processedTweets, testTweets):
	featureVectors, vocabulary = createTFIDFFeatureVectors(processedTweets)

	relevanceThreshold = 0
	for processedTestTweet in testTweets:
		print("\n--------------------\n")
		print processedTestTweet
		tweetNumber = 0
		closenessScores = {}
		for tweet in featureVectors:
			score = 0
			for word in processedTestTweet:
				if word in vocabulary:
					score = score + tweet[vocabulary[word]]
			if score > relevanceThreshold:
				closenessScores[tweetNumber] = score
			tweetNumber = tweetNumber + 1
		# take top 5 tweets as the most relevant tweets
		relevantTweets = sorted(closenessScores.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]
		# print relevantTweets
		relevantTags = [processedHashTags[index] for (index,score) in relevantTweets]
		relevantTags = [item for sublist in relevantTags for item in sublist]
		

		hashtagFreqMap = {}
		hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
		finalTags = globalFrequencyRanking(relevantTags,hashtagFreqMap, 5)
		print finalTags
		break

def tweetScoreBased(closenessScores, processedHashTags):
	relevantTweets = sorted(closenessScores.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]
	# print relevantTweets
	relevantTags = [processedHashTags[index] for (index,score) in relevantTweets]
	relevantTags = [item for sublist in relevantTags for item in sublist]
	# take first 5 hashtags without changing the order
	tempHashtagSet = set()
	finalTags = []
	for tag in relevantTags:
		if tag not in tempHashtagSet:
			tempHashtagSet.add(tag)
			finalTags.append(tag)
	return finalTags[:5]



def localFrequencyRanking(relevantTags, k):
	freqMap = {}
	for tag in relevantTags:
		if freqMap.has_key(tag):
			freqMap[tag] += 1
		else :
			freqMap[tag] = 1
	sortedTags = sorted(freqMap.iteritems(), key=operator.itemgetter(1), reverse=True)[:k]
	return [ tag for tag,freq in sortedTags]

def globalFrequencyRanking(relevantTags, hashtagFreqMap, k):
	freqMap = {}
	for tag in relevantTags:
		freqMap[tag] = hashtagFreqMap[tag]
	sortedTags = sorted(freqMap.iteritems(), key=operator.itemgetter(1), reverse=True)[:k]
	return [ tag for tag,freq in sortedTags]



def createNaiveBayesFeatureVector(feature, featureVector):
	for word in feature:
		featureVector[word] = 1
	return featureVector


def naiveBayesClassifier(processedHashTags, processedTweets, testTweets):
	vocabulary = getVocabulary(processedTweets)
	for key,value in vocabulary.items():
		vocabulary[key] = 0

	train = []
	test = []

	for i in range(len(processedTweets)):
		feature = processedTweets[i]
		featureVector = copy.deepcopy(vocabulary)
		featureVector = createNaiveBayesFeatureVector(feature, featureVector)
		for hashtag in processedHashTags[i]:
			train.append((featureVector,hashtag))

	print "Trainig shuru"
	classifier = nltk.classify.NaiveBayesClassifier.train(train)
	print "Training Ends \n"

	for feature in testTweets:
		featureVector = copy.deepcopy(vocabulary)
		featureVector = createNaiveBayesFeatureVector(feature, featureVector)
		test.append((featureVector))

	
	for i in range(len(testTweets)):
		tweet = testTweets[i]
		pdist = classifier.prob_classify(test[i])

		allHashTags = pdist.samples()
		hashtagProb = {}
		for ht in allHashTags:
			hashtagProb[ht] = pdist.prob(ht)
		sortedProbs = sorted(hashtagProb.iteritems(), key=operator.itemgetter(1))

		bestMatch = reversed(sortedProbs[-5:])
		bestMatch = [i[0] for i in bestMatch]
		print tweet
		print bestMatch
		print sortedProbs[-5:]
		
		print "\n--------------------\n"

def hashTagMaps(processedTweets, processedHashTags):
	print "hashTag maps ", endl
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

def naiveBayesRecommender(processedTweets, processedHashTags, testTweets, k):
	hashtagFreqMap, hashtagToWordFreq = hashTagMaps(processedTweets, processedHashTags)
	wordFreqMap = getWordFrequency(processedTweets)
	vocabulary = getVocabulary(processedTweets)
	vocabSize = len(vocabulary.keys())
	totalFreq = sum(hashtagFreqMap.values())
	totalVocabFreq = sum(wordFreqMap.values())
	smoothingFactor = 0.001
	vocabSet = set(vocabulary.keys())


	vocabulary = getVocabulary(processedTweets)
	for testFeature in testTweets:
		featureVector = [0]*vocabSize
		hashtagProbMap = {}
		restWords = vocabSet - set(testFeature)
		for tag in hashtagFreqMap.keys():
			hashtagProbMap[tag] = float(hashtagFreqMap[tag])/totalFreq #Prior Probability
			for word in testFeature:
				if hashtagProbMap[tag] ==  0:
					print word
					exit(0)
				if vocabulary.has_key(word):
					freq = hashtagToWordFreq[tag][vocabulary[word]]
					if freq != 0:
						hashtagProbMap[tag] *= float(freq) / hashtagFreqMap[tag]
					else:
						hashtagProbMap[tag] *=  float(wordFreqMap[word]) / totalVocabFreq
			
			for word in restWords:
				freq = hashtagToWordFreq[tag][vocabulary[word]]
				if freq / hashtagFreqMap[tag] == 1:
					hashtagProbMap[tag] *= smoothingFactor
				else:
					hashtagProbMap[tag] *= (1 - (float(freq) / hashtagFreqMap[tag]))

		topKpairs = sorted(hashtagProbMap.iteritems(), key=operator.itemgetter(1))[-k:]
		finalTags = [tag for tag,prob in reversed(topKpairs)]
		print testFeature
		print [(tag,str(prob)) for tag,prob in reversed(topKpairs)]
		print "-------------------\n"


def fiveFoldValidation():
	preProcessAllTweets(tarr,"h.txt","w.txt") #sets the processedHashTags and processedTweets
	trainingHashTags=[]
	trainingTweets = []
	testTweets = []
	total = len(processedTweets)

	for i in range(0,1):
		j=i
		for count in range(0,4):

			for ele in processedTweets[int(j*0.2*total): int((j+1)*0.2*total)]:
				trainingTweets.append(ele)
			for ele in processedHashTags[int(j*0.2*total): int((j+1)*0.2*total)]:
				trainingHashTags.append(ele)
			j = (j+1)%5

		j = (i-1)%5
		for ele in processedTweets[int(j*0.2*total): int((j+1)*0.2*total)]:
			testTweets.append(ele)

		testTweets = processedTweets[int(0*0.2*total): int(1*0.2*total)]
		# naiveBayesClassifier(trainingHashTags, trainingTweets, testTweets)
		# test(trainingHashTags, trainingTweets, testTweets)
		naiveBayesRecommender(processedTweets, processedHashTags, testTweets, 5)

fiveFoldValidation()