
import nltk
import operator
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import copy
import sys

space=" "
endl = "\n"

from common_functions import *
from naive_bayes import *
# from nltk.stem.snowball import SnowballStemmer
# stemmer = SnowballStemmer("english")


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
	return vectorizer.fit_transform(textFeatures).toarray(), vectorizer.vocabulary_

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
	# print "Pre Processing Begins...", endl
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
	# print "Pre Processing ends..", endl


def singhamClassifier(processedTweets, processedHashTags, testTweets, testHashtags,
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
	recommendationScore = 0
	for i in range(len(testTweets)):
		processedTestTweet = testTweets[i]
		# print("\n--------------------\n")
		# print processedTestTweet
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

		recommendationScore += compareHashtagsForTweet(testHashtags[i], finalTags)
		# print finalTags
	return float(recommendationScore * 100)/len(testHashtags)
	
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

def compareHashtagsForTweet(actualTweetHashtags, recommendedTweetHashtags):
	if len(set(actualTweetHashtags) & set(recommendedTweetHashtags)):
		return True 
	else:
		return False

def recommendationScore(actualHashtags, recommendedHashtags):
	count = 0
	# print len(actualHashtags), len(recommendedHashtags)
	for i in range(len(actualHashtags)):
		count += compareHashtagsForTweet(actualHashtags[i], recommendedHashtags[i])
	return float(count) * 100 / len(actualHashtags)

def fiveFoldValidation():
	preProcessAllTweets(tarr,"h.txt","w.txt") #sets the processedHashTags and processedTweets
	
	total = len(processedTweets)

	scoreList = []
	for i in range(0,5):
		j=i
		print j
		trainingTweets=[]
		trainingHashTags=[]
		testTweets = []
		testHashtags = []
		for count in range(0,4):

			for ele in processedTweets[int(j*0.2*total): int((j+1)*0.2*total)]:
				trainingTweets.append(ele)
			for ele in processedHashTags[int(j*0.2*total): int((j+1)*0.2*total)]:
				trainingHashTags.append(ele)
			j = (j+1)%5

		j = (i-1)%5
		for ele in processedTweets[int(j*0.2*total): int((j+1)*0.2*total)]:
			testTweets.append(ele)
		for ele in processedHashTags[int(j*0.2*total): int((j+1)*0.2*total)]:
			testHashtags.append(ele)

	#/* Following for Singham classifier
		# featureVecApproach = str(sys.argv[2])
		# rankApproach = int(sys.argv[3])
		# k = int(sys.argv[4])
		# recommendationScore = singhamClassifier(trainingTweets, trainingHashTags, testTweets, testHashtags,rankApproach, featureVecApproach, k)
	#*/

	#/* Following for Naive Bayes
		k = int(sys.argv[2])
		recommendationScore = naiveBayesRecommender(trainingTweets, trainingHashTags, testTweets, testHashtags, k)
	#*/
		scoreList.append(recommendationScore)
	
	# print str(sys.argv[2]), str(int(sys.argv[3])), str(int(sys.argv[4])), str(float(sum(scoreList))/len(scoreList))
	print str(sys.argv[2]), str(float(sum(scoreList))/len(scoreList))

fiveFoldValidation()