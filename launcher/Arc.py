import math
from functools import lru_cache


@lru_cache(maxsize=None)
def distance(a):
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371
    return r * c


@lru_cache(maxsize=None)
def deg_2_rad(deg):
    return deg*math.pi/180


class Arc:
    def __init__(self):
        self.lat1 = 0.0
        self.long1 = 0.0
        self.lat2 = 0.0
        self.long2 = 0.0

    def set_peakInit(self, lat, long):
        self.lat1 = lat
        self.long1 = long
        return self

    def set_peakDest(self, lat, long):
        self.lat2 = lat
        self.long2 = long
        return self

    def compute_distance(self):
        phi1 = deg_2_rad(self.lat1)
        phi2 = deg_2_rad(self.lat2)
        deltaPhi = deg_2_rad(self.lat2-self.lat1)
        deltaLambda = deg_2_rad(self.long2-self.long1)
        a = math.sin(deltaPhi/2)*math.sin(deltaPhi/2)+math.cos(phi1)*math.cos(phi2)*math.sin(deltaLambda/2)*math.sin(deltaLambda/2)
        return distance(a)

    def __repr__(self):
        return f"<({self.lat1},{self.long1});({self.lat2},{self.long2})>"
