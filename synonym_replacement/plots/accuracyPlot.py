import matplotlib.pyplot as plt
import numpy as np

x = [5,10,15,20]
#multitags
# y1 = [2095.2,2424.8,2591.8,2703.2]
# y2 = [2229.2,2511,2658.6,2762.4]
# y3 = [2227,2504.4,2659.2,2757.8]

#all
y1 = [2095.2,2424.8,2591.8,2703.2]
y2 = [2101.6,2411.2,2579.2,2684]
y3 = [2111.8,2408.2,2575,2680.6]

plt.xticks(np.arange(4, 21, 5))
plt.scatter(x,y1)
plt.scatter(x,y2)
plt.scatter(x,y3)
plt.plot(x,y1,'r', label = "Basic")
plt.plot(x,y2,'b', label = "Syn")
plt.plot(x,y3,'y', label = "Syn + Stem")
plt.ylabel('No. of correct recommendations')
plt.xlabel('Top k hashtags')
plt.legend(loc=2)
#plt.title("For tweets with multi-frequency hashtags")
plt.title("For all tweets")
plt.show()