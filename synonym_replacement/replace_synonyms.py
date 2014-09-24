#replace synonyms in text
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import sys

def main(args):
	stops = set(stopwords.words('english')+['I'])
	a=open(args[0])
	blines=a.readlines()
	a.close()
	n=open(args[0],'w');
	from nltk.tokenize import WhitespaceTokenizer
	line = 0
	for b in blines:
		outputty = ""
		c=WhitespaceTokenizer().tokenize(b)
		for word in c:
		    syn = wordnet.synsets(word)
		    if word not in stops and syn:
		    	# print syn[0].lemma_names[0]
		        outputty+=' '+syn[0].lemma_names[0]
		    else:
		        outputty +=' '+word
		outputty += "\n"
		print("line number : "+str(line))
		line = line+1
		n.write(outputty)
	n.close()

if __name__ == "__main__":
    main(sys.argv[1:])