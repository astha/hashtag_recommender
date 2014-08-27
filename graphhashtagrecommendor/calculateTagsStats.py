import operator
import sys

def main(argv):
    hashTags = {}
    hashtagFile = open(argv[0],'r')
    line = hashtagFile.readline()
    while line:
        line = line.strip(' \n')
        line = line.split(' ')
        for tag in line:
            if tag in hashTags:
                hashTags[tag] += 1
            else:
                hashTags[tag] = 1
        line = hashtagFile.readline()

    sorted_tags = sorted(hashTags.iteritems(), key=operator.itemgetter(1), reverse=True)
    totalTags = len(sorted_tags)
    index = 0
    thirtyOrMore = 0
    twentyOrMore = 0
    TenOrMore = 0
    fiveOrMore = 0
    twoOrMore = 0
    Unique = 0
    for (key,value) in sorted_tags:
        if value >= 30:
            thirtyOrMore += 1
        if value >= 20:
            twentyOrMore += 1
        if value >= 10:
            TenOrMore += 1
        if value >= 5:
            fiveOrMore += 1
        if value >= 2:
            twoOrMore += 1
        if value == 1:
            Unique = totalTags - index
            break
        index += 1

    print "Total Tags: %d" % totalTags
    print "Tags with frequency >= 30:  %d" % thirtyOrMore
    print "Tags with frequency >= 20:  %d" % twentyOrMore
    print "Tags with frequency >= 10:  %d" % TenOrMore
    print "Tags with frequency >= 5: %d" % fiveOrMore
    print "Tags with frequency >= 2: %d" % twoOrMore
    print "Unique Tags: %d" % Unique

if __name__ == "__main__":
    main(sys.argv[1:])


# NEW DATABASE:
# --------------
# Total Tags: 8708
# Tags with frequency >= 30:  122
# Tags with frequency >= 20:  191
# Tags with frequency >= 10:  405
# Tags with frequency >= 5: 863
# Tags with frequency >= 2: 2458
# Unique Tags: 6250
