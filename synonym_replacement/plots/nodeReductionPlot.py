import matplotlib.pyplot as plt
import numpy as np

x1 = ['No Processing', 'Syn-Repl', 'Syn-Repl + Stem']
x = [5,15,25]
y1 = [24820.8,20595.8,19502]
y2 = [35340.4,30906.8,29853.2]

plt.axis([0, 30, 15000, 40000])
plt.xticks(x, x1)
plt.scatter(x,y1)
plt.scatter(x,y2)
plt.plot(x,y1,'r', label = "Multi-tags")
plt.plot(x,y2,'b', label = "All-tags")
plt.ylabel('No. of nodes')
plt.xlabel('Processing type')
plt.legend(loc=2)
plt.title("Node reduction plot")
plt.show()