import datetime
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np

start = datetime.datetime(2017, 1, 1)
end = datetime.datetime(2017, 1, 31)
f = web.DataReader("AMD", 'google', start, end)
print(type(f))
