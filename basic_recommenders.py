
import nltk
import operator
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import copy
import sys


from common_functions import *
from naive_bayes import *
# from nltk.stem.snowball import SnowballStemmer
# stemmer = SnowballStemmer("english")
endl = "\n"

processedHashTags = []
processedTweets = []


# presence feature vector
def createPresenceFeatureVectors(features):
	vocabulary = getVocabulary(features)
	featureVectors = []
	vocabSize = len(vocabulary.keys())
	for feature in features:
		featureVector = [0]*vocabSize
		for word in feature:
			featureVector[vocabulary[word]] = 1
		featureVectors.append(featureVector)
	return featureVectors, vocabulary


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


def singhamClassifier(processedHashTags, processedTweets, testTweets, 
						rankApproach, featureVecApproach, k):

	featureVectors=[]
	vocabulary={}
	
	if featureVecApproach == "tfidf" :
		featureVectors, vocabulary = createTFIDFFeatureVectors(processedTweets)
	elif featureVecApproach == "presence" :
		featureVectors, vocabulary = createPresenceFeatureVectors(processedTweets)
	elif featureVecApproach == "tf" :
		featureVectors, vocabulary = createTFFeatureVectors(processedTweets)
	else:
		print "boss ! look @ featurevec approach ! :/"
		exit(0)

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
		# take top k tweets as the most relevant tweets
		finalTags = []
		if rankApproach == 1: #tweetScoreBased
			finalTags = tweetScoreBased(closenessScores, processedHashTags, k)
		else:
			relevantTweets = sorted(closenessScores.iteritems(), key=operator.itemgetter(1), reverse=True)[:k]
			relevantTags = [processedHashTags[index] for (index,score) in relevantTweets]
			relevantTags = [item for sublist in relevantTags for item in sublist]
		
			if rankApproach == 2: #localFrequencyRanking
				finalTags = localFrequencyRanking(relevantTags, k)
			elif rankApproach == 3: 
				hashtagFreqMap = {}
				hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
				finalTags = globalFrequencyRanking(relevantTags,hashtagFreqMap, k)

		print finalTags
	


# Ranking methods 

def tweetScoreBased(closenessScores, processedHashTags, k):
	relevantTweets = sorted(closenessScores.iteritems(), key=operator.itemgetter(1), reverse=True)[:k]
	# print relevantTweets
	relevantTags = [processedHashTags[index] for (index,score) in relevantTweets]
	relevantTags = [item for sublist in relevantTags for item in sublist]
	# take first k hashtags without changing the order
	tempHashtagSet = set()
	finalTags = []
	for tag in relevantTags:
		if tag not in tempHashtagSet:
			tempHashtagSet.add(tag)
			finalTags.append(tag)
	return finalTags[:k]

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
		rankApproach=1
		featureVecApproach="tfidf"
		k=5
		singhamClassifier(trainingHashTags, trainingTweets, testTweets, rankApproach, featureVecApproach, k)
		# naiveBayesRecommender(processedTweets, processedHashTags, testTweets, 5)

fiveFoldValidation()