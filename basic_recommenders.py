
import nltk
import operator
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import copy
import sys
import heapq

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
	# print features
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
	initialize()
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

	hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
	for tagList in processedHashTags:
		for tag in tagList:
			if (hashtagFreqMap[tag] <= 5):
				tagList.remove(tag)



def singhamClassifier(processedTweets, processedHashTags, testTweets, testHashtags, rankApproach, featureVecApproach, k):

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
		print """Let me know if this is a lot of work. I would love to do it myself instead of monitoring and 
			querying people if they have done their part or not and whether they are facing some problems. 
			I distribute the work because, 
			a) No one else(I mean it) steps forward and takes the initiative to lead the team. People tend to 
			 wrap up shit at the end time and I do not like it. I like to put my full effort and the result, 
			 as always depends on luck.
			b) Some people tend to blame one for doing everything and not letting them know that he has already
			 completed it.

			 PS. I truly do not want to be any sort of leader/boss. I would love to do the job assigned to me 
			 and chill out and let the other guy worry about how to integrate and present my shit. 

			 PPS. I seriously do not like reminding people about their work again and again. It is irritating for both.
			 That is why I sometimes ask one member to remind the other member and keep myself totally out of the loop. 

			 PPPS. I am not in a bad mood or out of my mind. These are just some relevant points that I felt everyone should know and 
			 they are true in general for any responsible leader. Chill."""
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

			relevantTweets = heapq.nlargest(k, closenessScores, key=closenessScores.get)

			relevantTags = [processedHashTags[index] for index in relevantTweets]
			relevantTags = [item for sublist in relevantTags for item in sublist]
		
			if rankApproach == 2: #localFrequencyRanking
				finalTags = localFrequencyRanking(relevantTags, k)
			elif rankApproach == 3: 
				hashtagFreqMap = {}
				hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
				finalTags = globalFrequencyRanking(relevantTags,hashtagFreqMap, k)

		recommendationScore += compareHashtagsForTweet(testHashtags[i], finalTags)
		# rankRecommendation(testHashtags[i], finalTags) # updates rank recommendation map
	return float(recommendationScore * 100)/len(testHashtags)
	# return 0
	
# Ranking methods 
def tweetScoreBased(closenessScores, processedHashTags, k):
	relevantTweets = heapq.nlargest(k, closenessScores, key=closenessScores.get)
	# print relevantTweets
	relevantTags = [processedHashTags[index] for index in relevantTweets]
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
	sortedTags = heapq.nlargest(k, freqMap, key=freqMap.get)
	return sortedTags

def globalFrequencyRanking(relevantTags, hashtagFreqMap, k):
	freqMap = {}
	for tag in relevantTags:
		freqMap[tag] = hashtagFreqMap[tag]
	sortedTags = heapq.nlargest(k, freqMap, key=freqMap.get)
	return sortedTags

rankRecommendationMap=[]
def rankRecommendation(actualTweetHashtags, recommendedTweetHashtags):
	global rankRecommendationMap
	for tag in actualTweetHashtags:
		if tag in recommendedTweetHashtags:
			rankRecommendationMap[recommendedTweetHashtags.index(tag)+1] += 1
		else:
			rankRecommendationMap[len(rankRecommendationMap)-1] += 1

def fiveFoldValidation():	
	total = len(processedTweets)

	k = int(sys.argv[4])	
	# global rankRecommendationMap
	# rankRecommendationMap=[0]*(k+2)

	scoreList = []
	for i in range(2,3):
		j=i
		# print j
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
		featureVecApproach = str(sys.argv[2])
		rankApproach = int(sys.argv[3])
		
		recommendationScore = singhamClassifier(trainingTweets, trainingHashTags, testTweets, testHashtags,rankApproach, featureVecApproach, k)
	#*/

	#/* Following for Naive Bayes
		# k = int(sys.argv[2])
		# recommendationScore = naiveBayesRecommender(trainingTweets, trainingHashTags, testTweets, testHashtags, k)
	#*/
		scoreList.append(recommendationScore)
	
	print str(sys.argv[2]), str(int(sys.argv[3])), str(int(sys.argv[4])), str(float(sum(scoreList))/len(scoreList))
	# print str(sys.argv[2]), str(float(sum(scoreList))/len(scoreList))
	# print rankRecommendationMap

preProcessAllTweets(tarr,"h.txt","w.txt") #sets the processedHashTags and processedTweets
# hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
# plotHashtagFreqDistribution(hashtagFreqMap)
fiveFoldValidation()