import numpy as np
import csv

out = csv.writer(open("Data/best4linreg.csv", "w"), delimiter=',',quoting=csv.QUOTE_NONE)

p = 0.0
rd = np.random.randint(0, 10, 1)
rd = rd[0]

for i in range(1000):
    p += rd
    out.writerow((p, p*2, p*3))
    rd *=1.5


