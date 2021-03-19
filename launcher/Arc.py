import math


class Arc:
    def __init__(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = x
        self.y2 = y

    def set_peakDest(self, x, y):
        self.x2 = x
        self.y2 = y
        return self

    def compute_distance(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return round(math.sqrt(x*x + y*y), 2)

    def get(self):
        print(self.x1, self.y1)
