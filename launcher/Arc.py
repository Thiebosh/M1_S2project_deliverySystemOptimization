import math
from functools import lru_cache


@lru_cache(maxsize=None)
def distance(x, y):
    return round(math.sqrt(x*x + y*y), 2)


class Arc:
    def __init__(self, lat, long):
        self.lat1 = lat
        self.long1 = long
        self.lat2= lat
        self.long2 = long
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
        self.lat2 = x
        self.long2 = y
        return self

    def compute_distance(self):
        phi1 = self.lat1*math.pi/180
        phi2 = self.lat2*math.pi/180
        deltaPhi = (self.lat2-self.lat1)*math.pi/180
        deltaLambda = (self.long2-self.long1)*math.pi/180
        a = math.sin(deltaPhi/2)*math.sin(deltaPhi/2)+math.cos(phi1)*math.cos(phi2)*math.sin(deltaLambda/2)*math.sin(deltaLambda/2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        r = 6371
        return r * c

    def __repr__(self):
        return f"<({self.x1},{self.y1});({self.x2},{self.y2})>"
