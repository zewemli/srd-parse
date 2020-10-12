import string
import math
from itertools import product

def get_text(c):
    t = c.get_text()
    if t == u'\t\r \xa0':
        return u" "
    else:
        return t

def euclidean(a,b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return math.sqrt( (dx * dx) + (dy * dy) )

class Word:
    def __init__(self):
        self.text = None
        self.x0 = None
        self.x1 = None
        self.y0 = None
        self.y1 = None
        self.bbox = None
        self.sbox = None
        self.width = None
        self.height = None
        self.fonts = None
        
    @classmethod
    def fromChars(Type, chars):

        self = Type()
        self.text = "".join(map(get_text, chars )).strip()

        x0,y0,x1,y1 = chars[0].bbox
        for c in chars[1:]:
            x0 = min(c.x0, x0)
            x1 = max(c.x1, x1)
            y0 = min(c.y0, y0)
            y1 = max(c.y1, y1)
         
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.font = chars[0].fontname
        self.setDims()
        
        return self

    @classmethod
    def fromWords(Type, *others):
        s = Type()
        s.text = " ".join(x.text for x in others)
        s.font = others[0].font
        s.x0 = min(c.x0 for c in others)
        s.x1 = min(c.x1 for c in others)
        s.y0 = min(c.y0 for c in others)
        s.y1 = min(c.y1 for c in others)
        
        s.setDims()
        return s
        

    def __str__(self):
        return self.text

    def __hash__(self):
        return hash(f"{self.text}-{self.bbox}")

    def __eq__(self, other):
        return (self.text == other.text) and (self.bbox == other.bbox)

    def __lt__(self, other):
        return self.text < other.text

    def points(self):
        yield self.x0, self.y0
        yield self.x0, self.y1
        yield self.x1, self.y0 
        yield self.x1, self.y1
        yield self.midpoint

    def dist(self, to):
        my_points = list(self.points())
        to_points = list(to.points())
        return min( euclidean( a,b ) for a,b in product(my_points, to_points) )
           
    def setDims(self):
        self.bbox = (self.x0, self.y0, self.x1, self.y1)
        self.width = self.x1 - self.x0
        self.height = self.y1 - self.y0
        self.sbox = ((self.x0, self.y0), (self.width, self.height))
        self.midpoint = ((self.x0 + self.x1)/2.0, (self.y0 + self.y1)/2.0)
        return self

    def toDict(self):
        return {"text": self.text,
                "font": self.font,
                "box": [self.x0, self.y0, self.x1, self.y1]}

    @classmethod
    def fromDict(Type, d):
        self = Type()
        self.x0, self.y0, self.x1, self.y1 = d['box']
        self.font = d['font']
        self.text = d['text']
        self.setDims()
        return self

    def joinLines(self, other):
        if self.x0 == other.x0 and self.font == other.font:
            # Merge
            return [Word.fromWords( self, other )]
        else:
            return [self, other]