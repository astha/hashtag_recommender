import numpy as np
import sys
import matplotlib.pyplot as plt

filename = sys.argv[1]
fvec = sys.argv[2]
f = open(filename,'r')

lines = f.readlines()
f.close()
hist={}

for rankApproach in range(1,4):
	hist[rankApproach] = []

for line in lines:
	arr = line.split()
	if(arr[0] == fvec):
		rankApproach = int(arr[1])
		k = int(arr[2])
		percent = float(arr[3])
		hist[rankApproach].append(percent)

n_groups = 4
index = np.arange(n_groups)
bar_width = 0.25
rects = []
colors = ['r','y','cyan']
rankApproach = ['Tweet Score Based','Local Freq', 'Global Freq']

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%1.1f'%float(height),
                ha='center', va='bottom')

for i in range(len(hist.keys())):
	key = hist.keys()[i]
	r = plt.bar(index+bar_width*i, hist[key], bar_width,
                 color=colors[i],
                 label=rankApproach[i])
	autolabel(r)

plt.xlabel('Size of recommended hashtags')
plt.ylabel('Score in %')
plt.title('% of tweets for which recommended tags comprised actual hashtags\n('+fvec+' feature Vector)')
plt.xticks(index + bar_width, range(5,25,5))
plt.grid()
plt.legend(loc=2)
plt.show()


