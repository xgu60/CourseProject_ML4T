import numpy as np
import csv

out = csv.writer(open("Data/best4KNN.csv", "w"), delimiter=',',quoting=csv.QUOTE_NONE)



a = np.random.randint(0, 100, 10)
b = np.random.randint(0, 100, 10)
c = np.random.randint(0, 100, 10)
for i in range(100):
    for j in range(10):
        out.writerow((a[j], b[j], c[j]))
        





 



