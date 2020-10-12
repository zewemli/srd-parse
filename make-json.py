from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno, LTText

import os, sys
import random
from tqdm import tqdm
import argparse
import json
import string
from itertools import groupby

from srd_parse.datastructs import Word

def is_ok_tok(t):
    return hasattr(t,'fontname') and hasattr(t,'bbox')

def emit_words(stream):
    for _y, xchars in groupby(filter(is_ok_tok, stream), key=lambda c: c.y0):
        for _font, fchars in groupby(xchars, key=lambda c: c.fontname):
            yield Word.fromChars(list(fchars))
        
def emit_blocks(word_stream):

    head = None
    for w in word_stream:
        if head is None:
            head = w
        else:
            lines = head.joinLines(w)
            if len(lines) == 2:
                yield lines[0]
            head = lines[-1]
    
    yield head

def gen_containers_from_page(page):
    for element in page:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                yield from text_line

parser = argparse.ArgumentParser(description="parser for SRD")
parser.add_argument("filepath", help="Path to the SRD 5.1")
parser.add_argument("output_dir", help="Output directory")
parser.add_argument("--page", "-p", type=int, help="Only parse this one page")
parser.add_argument("--gap", default=5.0, type=float, help="Setting for the maximum gap between words in a line")

args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

for page_num, page_layout in tqdm(enumerate(extract_pages( args.filepath  ), start=1), desc='parsing'):
    words = list( emit_blocks(emit_words( gen_containers_from_page(page_layout))  ))
    with open(os.path.join(args.output_dir, 'page-%s.json' % str(page_num).zfill(4)), 'wt') as fpage:
        json.dump([x.toDict() for x in words], fpage)
