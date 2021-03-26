import math


class Arc:
    def __init__(self, lat, long):
        self.lat1 = lat
        self.long1 = long
        self.lat2= lat
        self.long2 = long

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

    def print(self):
        print(self.lat1, self.long)
