import sys
import os
from nltk import PorterStemmer
stemmer = PorterStemmer()

def main(args):
	tweets = open(args[0], 'r')
	newTweets = open(args[0]+"_processed", 'w')
	l1 = tweets.readline()
	while l1:
		l1 = l1.split()
		processedTweet = ""
		for a in l1:
			w = stemmer.stem(a)
			if w:
				processedTweet += " " + w
			else:
				processedTweet += " " + a
		newTweets.write(processedTweet.strip() + "\n")
		l1 = tweets.readline()
	os.remove(args[0])
	os.rename(args[0]+"_processed", args[0])
	
if __name__ == "__main__":
    main(sys.argv[1:])