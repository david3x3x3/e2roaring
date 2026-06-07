from collections import defaultdict
from pyroaring import BitMap
import math
import os
import psutil
import random
import sys

_proc = psutil.Process(os.getpid())

def mem_mb():
    return _proc.memory_info().rss / 1024 / 1024

def fmt_duration(seconds):
    ms = int(seconds * 1000) % 1000
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f'{h}h {m}m {s}s {ms}ms'

def print_solution(rows):
    for row in rows:
        print([(p, pieces[p]) for p in row])
    print('')

def top_edges(row):
    return ''.join(pieces[p][0] for p in row)

def bottom_edges(row):
    return ''.join(pieces[p][2] for p in row)

# puzzdata = 'aabc/aacb/aacc/aacd/abeb/abfd/abgd/abib/abid/abkb/abkc/ablb/ablc/aceb/acec/aced/acjb/acjc/ackd/adec/aded/adfb/adfc/adjb/adjd/adkc/adlb/adld/efeh/efkg/egfj/eghf/egkj/ehej/ehfg/eihl/eikk/ejgf/ejgi/ekli/elhk/elig/fffi/fflk/fgkk/fhfk/fhgj/figg/fjgg/fjil/flih/ggil/ghih/ghlh/gihj/gjkh/gkhi/hijl/hjkl/hkki/hkll/hlji/hljj/iijl'
puzzdata = 'aabb/aabd/aacc/aacd/abgb/abgc/abib/abic/abid/aceb/acfb/acgc/acgd/achd/adec/aded/adfb/adgc/adhb/adic/eehf/efff/efii/eggh/eghi/ehgf/ehhf/ehhh/eifg/eifh/eihg/eihi/fgfh/fggi/fghi/figi'

width = int(math.sqrt(len(puzzdata.split('/'))))
height = width

print(f'width = {width}')

pieces0 = ['aaaa'] + puzzdata.split('/')

pieces = dict()
for i, p in enumerate(pieces0):
    for rot in range(4):
        pieces[(i, rot)] = p
        p = p[3] + p[:3]

# For row building: keyed by left edge.
# row_fit: pieces where right edge is not 'a' (interior columns)
# row_fit_last: pieces where right edge is 'a' (rightmost column)
row_fit = defaultdict(list)
row_fit_last = defaultdict(list)
for key1, val in pieces.items():
    left = val[3]
    if val[1] == 'a':
        row_fit_last[left].append(key1)
    else:
        row_fit[left].append(key1)

def build_bitmaps():
    print(len(pieces0), pieces0)
    Q = [([(0, 0)], set(range(1, len(pieces0))))]
    solcount = 0
    nodes = 0
    top_edge_bm = defaultdict(BitMap)
    bottom_edge_bm = defaultdict(BitMap)
    piece_bm = [None] + [BitMap() for _ in range(len(pieces0))]
    arrangements = []
    while Q:
        solution, remain = Q.pop()
        nodes += 1
        if len(solution) == 1 + width:
            row = solution[1:]
            if solcount % 100000 == 0:
                print(f'found #{solcount} - mem={mem_mb():.1f}MB')
            arrangements.append(row)
            for p in row:
                piece_bm[p[0]].add(solcount)
            top_edge_bm[top_edges(row)].add(solcount)
            bottom_edge_bm[bottom_edges(row)].add(solcount)
            solcount += 1
        else:
            left = pieces[solution[-1]][1]
            is_last = len(solution) == width
            lookup = row_fit_last if is_last else row_fit
            for p in lookup.get(left, []):
                piecenum, rot = p
                if piecenum in remain:
                    Q.append((solution + [p], remain - {piecenum}))
    print(f'{solcount} row arrangements', flush=True)
    print(f'{nodes} nodes', flush=True)
    return arrangements, top_edge_bm, bottom_edge_bm, piece_bm

def search(arrangements, top_edge_bm, bottom_edge_bm, piece_bm):
    nodes = [0] * height
    solution_count = [0]
    last_row_bm = bottom_edge_bm['a' * width]

    def fill_row(depth, chosen, forbidden, candidates):
        for ri in candidates:
            row = arrangements[ri]
            nodes[depth] += 1

            if depth == 0 and ri % 1000 == 0:
                print(f'trying row {ri} at top - mem={mem_mb():.1f}MB')
                print(f'nodes = {nodes}', flush=True)

            new_forbidden = forbidden.copy()
            for p in row:
                new_forbidden = new_forbidden.union(piece_bm[p[0]])

            if depth == height - 1:
                solution_count[0] += 1
                all_rows = [arrangements[i] for i in chosen] + [row]
                print(f'\nsolution #{solution_count[0]}')
                print_solution(all_rows)
                flat = [p for r in all_rows for p in r]
                print('solution=' + ' '.join([f'{p[0]}/{p[1]}' for p in flat]), flush=True)
            else:
                next_candidates = top_edge_bm[bottom_edges(row)] - new_forbidden
                if depth == height - 2:
                    next_candidates = next_candidates & last_row_bm
                fill_row(depth + 1, chosen + [ri], new_forbidden, next_candidates)

    print('bitmaps complete, starting search')
    # only try top rows that use the first corner piece
    first_row_candidates = BitMap(
        i for i, s in enumerate(arrangements) if s[0][0] == 1
    ) & top_edge_bm['a' * width]
    fill_row(0, [], BitMap(), first_row_candidates)
    print(f'nodes = {nodes}')
    return solution_count[0]

if __name__ == '__main__':
    import time
    t0 = time.monotonic()
    arrangements, top_edge_bm, bottom_edge_bm, piece_bm = build_bitmaps()
    t1 = time.monotonic()
    print(f'build_bitmaps: {fmt_duration(t1-t0)}', flush=True)
    search(arrangements, top_edge_bm, bottom_edge_bm, piece_bm)
    t2 = time.monotonic()
    print(f'search: {fmt_duration(t2-t1)}', flush=True)
