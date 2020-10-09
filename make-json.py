from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno, LTText

import os, sys
import random
from tqdm import tqdm
import argparse
import json
import string

from srd_parse.datastructs import Word

def emit_words(stream):
    word = []
    space = False
    pfont = None
    for x in stream:
        if hasattr(x,'fontname') and hasattr(x,'bbox'):
            font = x.fontname
            if x.get_text() == u'\t\r \xa0' or x.get_text() == '\n':
                if len(word):
                    yield Word.fromChars(word)
                    word = []
            elif font != pfont or x.get_text() == string.punctuation:
                # New 'term'
                if len(word):
                    yield Word.fromChars(word)
                word = [x]
            else:
                word.append(x)

            pfont = font

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
