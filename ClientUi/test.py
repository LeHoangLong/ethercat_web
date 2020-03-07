import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
import time

data = np.random.random((2,10))

# To make a standalone example, I'm skipping initializing the 
# `Figure` and `FigureCanvas` and using `plt.figure()` instead...
# `plt.draw()` would work for this figure, but the rest is identical.
fig, ax = plt.subplots()
ax.set(title='Click to update the data')
#im = ax.imshow(data)
line, = ax.plot(data[0], data[1])

new_data = False

def update(event):
    global new_data
    new_data = True

def draw():
    global new_data
    while True:
        if new_data:
            new_data = False
            line.set_data(np.random.random((2,10)))
            fig.canvas.draw()
            time.sleep(1)

Thread(target=draw).start()

fig.canvas.mpl_connect('button_press_event', update)
plt.show()