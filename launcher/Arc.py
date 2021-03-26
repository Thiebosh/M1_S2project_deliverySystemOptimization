import math
from functools import lru_cache


@lru_cache(maxsize=None)
def distance(x, y):
    round(math.sqrt(x*x + y*y), 2)


class Arc:
    def __init__(self):
        self.x1 = 0.0
        self.y1 = 0.0
        self.x2 = 0.0
        self.y2 = 0.0

    def set_peakInit(self, x, y):
        self.x1 = x
        self.y1 = y
        return self

    def set_peakDest(self, x, y):
        self.x2 = x
        self.y2 = y
        return self

    def compute_distance(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return distance(x, y)

    def __repr__(self):
        return f"<({self.x1},{self.y1});({self.x2},{self.y2})>"
