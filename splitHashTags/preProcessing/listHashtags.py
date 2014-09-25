import operator
import sys

def main(argv):
    hashTags = {}
    hashtagFile = open(argv[0],'r')
    line = hashtagFile.readline()
    uniqueTags = open("uniqueTags", 'w')
    while line:
        line = line.strip(' \n')
        line = line.split(' ')
        for tag in line:
            if tag in hashTags:
                hashTags[tag] += 1
            else:
                hashTags[tag] = 1
        line = hashtagFile.readline()

    hashTags = hashTags.keys()
    for tag in hashTags:
    	uniqueTags.write(tag.strip() + "\n")

if __name__ == "__main__":
    main(sys.argv[1:])

