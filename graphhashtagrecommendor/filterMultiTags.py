import sys

def main():
	uniqueTags = []
	uniqueTagsFile = open('uniqueTags','r')
	multiTags = open('multiTags','w')
	multiTweets = open('multiTweets','w')
	tweets = open('tweets','r')
	hashtags = open('hashtags', 'r')
	line = uniqueTagsFile.readline()
	while line:
		uniqueTags.append(line.strip('\n'))
		line = uniqueTagsFile.readline()

	tweetline = tweets.readline()
	hashtagline  = hashtags.readline()
	while tweetline and hashtagline:
		hashtagline = hashtagline.strip('\n').split(' ')
		hashtagline = [x for x in hashtagline if x not in uniqueTags]
		if len(hashtagline) != 0:
			multiTags.write(' '.join(hashtagline) + '\n')
			multiTweets.write(tweetline)
		tweetline = tweets.readline()
		hashtagline  = hashtags.readline()


if __name__ == "__main__":
	main()