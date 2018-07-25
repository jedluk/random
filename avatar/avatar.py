import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from random import random
from math import sin, cos, ceil, pi, isclose

class AvatarGenerator:
    
    def __init__(self, N):
        self.size = N
        self.image = np.ones((N, N))    

    def save_image(self, name):
        array = self.image*255.
        fig = plt.figure()
        plt.imsave(name, array.astype('uint8'), cmap=matplotlib.cm.gray, vmin=0, vmax=255)
        plt.close(fig)

    def decimal_range(self, start, stop, increment):
        while start < stop and not isclose(start, stop): # Py>3.5
            yield start
            start += increment

    def scale(self, x):
        MIN, MAX = 0, self.size-1
        # min_range_x, max_range_x = -1, 1
        return (MAX - MIN) * (x + 1) / (2 + MIN)

    def generate(self):
        image = np.ones((self.size,self.size))
        R, r, d = [random() for i in range(0,3)]
        k = (R - r) 
        m = (k / r)
        print(R, r, d) 
        for t in self.decimal_range(0, 20 * pi, 0.0001):
            x = k * cos(t) + d * cos(m * t)
            y = k * sin(t) - d * sin(m * t)
            x,y = ceil(self.scale(x)), ceil(self.scale(y))
            if x >= self.size:
                x = self.size - 1
            if y >= self.size:
                y = self.size - 1
            image[x, y] = 0
        self.image = image


if __name__ == "__main__":
    generator = AvatarGenerator(256)
    generator.generate()
    generator.save_image("avatar" + str(random()) + ".png")