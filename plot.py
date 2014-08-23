import sys


filename = sys.argv[1]
fvec = sys.argv[2]
f = open(filename,'r')

lines = f.readlines()

for k in range(5,25,5):
	hist[k] = []

for line in lines:
	arr = line.split()
	if(arr[0] == fvec):
		rankApproach = arr[1]
		k = arr[2]
		percent = arr[3]
		hist[k].append(percent)

n_groups = 4
index = np.arange(n_groups)
bar_width = 0.35
rects = []
colors = ['r','g','b','c']
rankApproach = ['Tweet Score Based','Local Freq', 'Global Freq']

count   = 0
for key in hist.keys():
	r = plt.bar(index, hist[key], bar_width,
                 color=colors[count],
                 label='Men')
	rects.append()


