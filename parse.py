from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno, LTText

import os, sys
import random
from tqdm import tqdm
import argparse
import json

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

def emit_words(stream):
    word = []
    space = False
    for x in stream:
        if x.get_text() == u'\t\r \xa0' or x.get_text() == '\n':
            if len(word):
                yield Word.fromChars(word)
                word = []
        else:
            word.append(x)

def gen_containers_from_page(page):
    for element in page:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                yield from text_line

parser = argparse.ArgumentParser(description="parser for SRD")
parser.add_argument("filepath", help="Path to the SRD 5.1")
parser.add_argument("output_dir", help="Output directory")
parser.add_argument("--page", "-p", type=int, help="Only parse this one page") 

args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

for page_num, page_layout in tqdm(enumerate(extract_pages( args.filepath  ), start=1), desc='parsing'):
    words = list( emit_words( gen_containers_from_page(page_layout)  ))
    with open(os.path.join(args.output_dir, 'page-%s.json' % str(page_num).zfill(4)), 'wt') as fpage:
        json.dump([x.toDict() for x in words], fpage)
