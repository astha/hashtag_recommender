import re
import nltk
import operator
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
# from nltk.stem.snowball import SnowballStemmer
# stemmer = SnowballStemmer("english")


processedHashTags = []
processedTweets=[]

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
	return pattern.findall(tweet)


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


		# for index in range(1,len(arr)):
			# will come here iff 'w' is of the type [#sachin, you#sir, you#sir#great]
			# hashtagWord = arr[index]
			# featureVector.append(hashtagWord)

	return featureVector

def getVocabulary(features):
	vocabulary = dict()
	for feature in features:
		for word in feature:
			vocabulary[word] = True
	return vocabulary

# presence feature vector
def createPresenceFeatureVectors(features):
	vocabulary = getVocabulary(features).keys()
	featureVectors = []
	for feature in features:
		featureVector = []
		for word in vocabulary:
			if word in feature:
				featureVector.append(1)
			else:
				featureVector.append(0)
		featureVectors.append(featureVector)
	return featureVectors, vocabulary

# tf feature vector
def createTFFeatureVectors(features):
	vectorizer = CountVectorizer()
	textFeatures = [' '.join(feature) for feature in features]
	return vectorizer.fit_transform(textFeatures).toarray(), vectorizer.vocabulary

# tfidf feature vector
def createTFIDFFeatureVectors(features):
	print features[1:10]
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
fp = open("tweets", 'r')
line = fp.readline()
while line:
	tarr.append(line)
	line = fp.readline()
fp.close()

def preProcessAllTweets(tweetArray, hashtagFileName, wordsFileName):
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
		hashtagList = retrieveHashTags(processedTweet)
		# hashtagFile.write(str(hashtagList)+"\n")
		# wordsFile.write(str(feature)+"\n")
		processedHashTags.append(hashtagList)
		processedTweets.append(feature)	
	hashtagFile.close()
	wordsFile.close()







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
		# take first 5 hashtags without changing the order
		tempHashtagSet = set()
		finalTags = []
		for tag in relevantTags:
			if tag not in tempHashtagSet:
				tempHashtagSet.add(tag)
				finalTags.append(tag)
		print finalTags[:5]




def fiveFoldValidation():
	preProcessAllTweets(tarr,"h.txt","w.txt") #sets the processedHashTags and processedTweets
	trainingHashTags=[]
	trainingTweets = []
	testTweets = []
	total = len(processedTweets)

	for i in range(0,2):
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

		test(trainingHashTags, trainingTweets, testTweets)



fiveFoldValidation()