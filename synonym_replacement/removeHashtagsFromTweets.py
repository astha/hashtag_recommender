import sys
import os

def main(args):
	tweets = open(args[0], 'r')
	tags = open(args[1], 'r')
	newTweets = open(args[0]+"_processed", 'w')
	newTags = open(args[1]+"_processed", 'w')
	l1 = tweets.readline()
	l2 = tags.readline()
	while l1 and l2:
		l1 = l1.split()
		tagline = l2
		l2 = [a.strip('#') for a in l2.split()]
		processedTweet = ""
		for a in l1:
			if a in l2:
				l2.remove(a)
			else:
				processedTweet += " " + a
		if processedTweet != "":
			newTweets.write(processedTweet.strip()+"\n")
			newTags.write(tagline.strip()+"\n")
		l1 = tweets.readline()
		l2 = tags.readline()
	os.remove(args[0])
	os.remove(args[1])
	os.rename(args[0]+"_processed", args[0])
	os.rename(args[1]+"_processed", args[1])
	
if __name__ == "__main__":
    main(sys.argv[1:])