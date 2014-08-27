import nltk
import operator
import copy
from common_functions import *

# Naive Bayes Self Implementation
def naiveBayesRecommender(processedTweets, processedHashTags, testTweets, testHashtags,k):
  print "hashTagMaps start"
  hashtagFreqMap, hashtagToWordFreq = hashTagMaps(processedTweets, processedHashTags)
  print "hashTagMaps done, both :) "
  print "Now, getting onto word frequency"
  wordFreqMap = getWordFrequency(processedTweets)
  print "Done. ! Moving on to get vocabulary"
  vocabulary = getVocabulary(processedTweets)
  print "Hey ! cheer up. vocabulary is done. "
  vocabSize = len(vocabulary.keys())
  totalFreq = sum(hashtagFreqMap.values())
  totalVocabFreq = sum(wordFreqMap.values())
  smoothingFactor = 0.001
  vocabSet = set(vocabulary.keys())


  recommendationScore = 0
  for i in range(len(testTweets)):
    testFeature = testTweets[i]
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

    print "sorting begin.."
    topKpairs = sorted(hashtagProbMap.iteritems(), key=operator.itemgetter(1))[-k:]
    print "sorting ends"
    finalTags = [tag for tag,prob in reversed(topKpairs)]
    # print testFeature
    # print [(tag,str(prob)) for tag,prob in reversed(topKpairs)]
    # print "-------------------\n"
    recommendationScore += compareHashtagsForTweet(testHashtags[i], finalTags)
  return float(recommendationScore * 100)/len(testHashtags)




# NLTK Naive Bayes 

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
