import math


class Arc:
    def __init__(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = 0
        self.y2 = 0

    def set_peakDest(self, x, y):
        self.x2 = x
        self.y2 = y
        return self

    def compute_distance(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return round(math.sqrt(x*x + y*y), 2)

    def __repr__(self):
        return f"<({self.x1},{self.y1});({self.x2},{self.y2})>"
