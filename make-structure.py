import json
import os,sys
import argparse

from math import log

import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict, Counter

from srd_parse.datastructs import Word

def load_page(from_path):
    with open(from_path,"rt") as fp:
        page_num = int(os.path.basename(from_path).split("-")[1].split(".")[0])
        return page_num, list(map(Word.fromDict, json.load(fp)))[:-24]

def make_grid( elements, ops ):

    hmax = max(e.height for e in elements)

    grid = nx.Graph()

    for kind, kOp in ops.items():
        groups = defaultdict(list)
        for e in elements:
            groups[ int(kOp(e)) ].append(e)
        
        for kVal, kItems in groups.items():
            if len(kItems) > 1:
                for a in kItems:
                    a_dists = sorted([ (a.dist(b), b) for b in kItems if a != b])[:2]
                    for ab_dist, b in a_dists:
                        if hmax >= ab_dist:
                            grid.add_edge(a, b, kind = ab_dist)

    return grid

def f_x0(e):
    return e.x0

def f_midX(e):
    return e.midpoint[0]

def f_midY(e):
    return e.midpoint[1]

class AdjustPoint:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right 
        self.top = top
        self.bottom = bottom

        self.w = self.right - self.left
        self.h = self.top - self.bottom

    def __call__(self, o):
        x,y = o.x0, o.y0

        return ((x - self.left) / self.w,
                1.0 - ((y - self.bottom) / self.h))

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Build structure from a page.json")
    parser.add_argument("pages", nargs="+", type=load_page, help="Page json to load")
    args = parser.parse_args()

    for i, page in args.pages:

        G = make_grid( page, {
            "x0": f_x0,
            "midX": f_midX,
            "midY": f_midY 
        } )

        left = min(e.x0 for e in page)
        right = max(e.x1 for e in page)
        top = min(e.y0 for e in page)
        bottom = max(e.y1 for e in page)

        adjustPoint = AdjustPoint(left, right, top, bottom)

        pos = {
            e : adjustPoint(e)
            for e in page
        }

        labels = { e: str(e) for e in page }

        plt.show(block=False)
        nx.draw(G, pos=pos, labels=labels, node_size = 10, font_size=7)
        plt.savefig(f"page-{i:04d}.png", format="PNG")

        px = page[0]
        cm = Counter()
        for x in page:
            if x.y0 == px.y0:
                cm[ int(x.x0 - px.x1) ] += 1
            px = x
        
        kerning, _ = cm.most_common(1)[0]
        print(cm.most_common())

        pe = page[0]
        lines = [ [pe] ]

        for e in page:
            if e.y0 == pe.y0: # and int(e.x0 - pe.x1) == kerning:
                lines[-1].append( e )
            else:
                lines.append([e])
            pe = e
        
        for line in lines:
            print(" ".join(map(str, line)))