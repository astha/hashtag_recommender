

def hashTagMaps(processedTweets, processedHashTags):
	hashtagFreqMap = calculateHashtagFrequency(processedHashTags)
	hashtagToWordFreq = {}
	vocabulary = getVocabulary(processedTweets)
	vocabularyCount = len(vocabulary.keys())
	for i in len(processedHashTags):
		hashtagList = processedHashTags[i]
		for hashtag in hashtagList:
			if not hashtagToWordFreq.has_key(hashtag):
				hashtagToWordFreq[hashtag] = [0]*vocabularyCount
			for word in set(processedTweets[i]):
				hashtagToWordFreq[hashtag][vocabulary[word]] += 1
	return hashtagFreqMap, hashtagToWordFreq

def createNaiveBayesFeatureVectors(processedTweets, processedHashTags):
	featureVectors = createPresenceFeatureVectors(processedTweets, vocabulary)
	return featureVectors

def naiveBayesRecommender(processedTweets, processedHashTags, testTweets):
	featureVectors = createNaiveBayesFeatureVectors(processedTweets, processedHashTags)
	hashtagFreqMap, hashtagToWordFreq = hashTagMaps(processedTweets, processedHashTags)

	for testFeature in testTweets:
		featureVector = [0]*vocabularyCount
		for word in testFeature:
			featureVector[vocabulary[word]] = 1
	# Incomplete function