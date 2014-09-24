import sys
import re
# Returns a list of common english terms (words)
def InitializeWords():
    wordlist = str(sys.argv[1]) # A file containing common english words
    content = None
    with open(wordlist) as f:
        content = f.readlines()
    l = [word.rstrip('\n') for word in content]
    return [word[:-1] for word in l]


def ParseTag(term, wordlist):
    words = []
    # Remove hashtag, split by dash
    tags = term[1:].split('-')
    for tag in tags:
        word = FindWord(tag, wordlist)    
        while word != None and len(tag) > 0:
            words += [word]            
            if len(tag) == len(word): # Special case for when eating rest of word
                break
            tag = tag[len(word):]
            word = FindWord(tag, wordlist)
        if not word:
            words += [tag]
    return words


# finds the longest match for the token in the wordlist
def FindWord(token, wordlist):
    i = len(token) + 1
    while i > 1:
        i -= 1
        # print token[:i]
        if token[:i] in wordlist:
            return token[:i]
    return None 


def splitHashtag(hashtag, wordlist):
    # try to see if capitalization exists, if no then parse. 
    tags = [a for a in re.split(r'([A-Z][a-z]*\d*)', hashtag[1:]) if a]
    if len(tags)>1:
        return tags
    else:
        return ParseTag(hashtag.lower(), wordlist)

# awesome-dayofmylife because #iamgreat
wordlist = InitializeWords()
hashtag = "#iamgreat"
print splitHashtag(hashtag, wordlist)