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
        self.text = ("".join( c.get_text() for c in chars )).strip()


        bchars = list(filter(lambda x: hasattr(x, "bbox"), chars))
        if len(bchars):
            x0,y0,x1,y1 = bchars[0].bbox
            for c in bchars[1:]:
                x0 = min(c.x0, x0)
                x1 = max(c.x1, x1)
                y0 = min(c.y0, y0)
                y1 = max(c.y1, y1)
             
            self.x0 = x0
            self.x1 = x1
            self.y0 = y0
            self.y1 = y1
            self.bbox = (x0, y0, x1, y1)
            self.width = x1 - x0
            self.height = y1 - y0
            self.sbox = ((x0, y0), (self.width, self.height))
        
            self.fonts = sorted(set(getattr(c, "fontname", None) for c in bchars))
        
        return self

    def setDims(self):
        self.bbox = (self.x0, self.y0, self.x1, self.y1)
        self.width = self.x1 - self.x0
        self.height = self.y1 - self.y0
        self.sbox = ((self.x0, self.y0), (self.width, self.height))
        self.midpoint = ((self.x0 + self.x1)/2.0, (self.y0 + self.y1)/2.0)
        return self

    def toDict(self):
        return {"text": self.text,
                "fonts": list(self.fonts),
                "box": [self.x0, self.y0, self.x1, self.y1]}

    @classmethod
    def fromDict(Type, d):
        self = Type()
        self.x0, self.y0, self.x1, self.y1 = d['box']
        self.fonts = d['fonts']
        self.text = d['text']
        return self