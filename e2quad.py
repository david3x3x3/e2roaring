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

def print_quad(s, wid):
    for rownum in range(len(s)//wid):
        row = s[rownum*wid:(rownum+1)*wid]
        print([(p, pieces[p]) for p in row])
    print('')

def lr_join_quad(s1, s2):
    res = []
    for rownum in range(width):
        res += s1[rownum*width:(rownum+1)*width]
        res += s2[rownum*width:(rownum+1)*width]
    return res
        
def rot_quad(s, times):
    res = []
    for col in range(width):
        for row in range(width-1, -1, -1):
            piece = s[row*width+col]
            res += [(piece[0], (piece[1]+1)%4)]
    if times == 1:
        return res
    return rot_quad(res, times-1)

def right_edges(s):        
    right_index = ''
    for rownum in range(width):
        row = s[rownum*width:(rownum+1)*width]
        right_index += str(pieces[row[-1]][1])
    return right_index

def down_edges(s):        
    down_index = ''.join(pieces[p][2] for p in s[-width:])
    return down_index

# puzzdata = 'aabc/aacb/aacc/aacd/abeb/abfd/abgd/abib/abid/abkb/abkc/ablb/ablc/aceb/acec/aced/acjb/acjc/ackd/adec/aded/adfb/adfc/adjb/adjd/adkc/adlb/adld/efeh/efkg/egfj/eghf/egkj/ehej/ehfg/eihl/eikk/ejgf/ejgi/ekli/elhk/elig/fffi/fflk/fgkk/fhfk/fhgj/figg/fjgg/fjil/flih/ggil/ghih/ghlh/gihj/gjkh/gkhi/hijl/hjkl/hkki/hkll/hlji/hljj/iijl'
puzzdata = 'aabb/aabd/aacc/aacd/abgb/abgc/abib/abic/abid/aceb/acfb/acgc/acgd/achd/adec/aded/adfb/adgc/adhb/adic/eehf/efff/efii/eggh/eghi/ehgf/ehhf/ehhh/eifg/eifh/eihg/eihi/fgfh/fggi/fghi/figi'

width = int(math.sqrt(len(puzzdata.split('/')))//2)
height = width
    
print(f'width = {width}')

pieces0 = ['aaaa'] + puzzdata.split('/')

pieces = dict()
for i, p in enumerate(pieces0):
    p2 = []
    for rot in range(4):
        pieces[(i, rot)] = p
        p = p[3] + p[:3]
fit = dict()
for key1, val in pieces.items():
    key2 = (val[0], val[3], val[1] == 'a', val[2] == 'a')
    if not fit.get(key2):
        fit[key2] = [key1]
    else:
        fit[key2].insert(0, key1)
def build_bitmaps():
    print(len(pieces0), pieces0)
    # for k in fit:
    #     random.shuffle(fit[k])
    Q = [([(0, 0)]*width, set(range(1,len(pieces0))))]
    solcount = 0
    nodes = 0
    best = 0
    right_edge_bm = defaultdict(BitMap)
    down_edge_bm = defaultdict(BitMap)
    piece_bm = [None,]
    for p in range(width*height*4):
        piece_bm += [BitMap()]
    print(piece_bm)
    arrangements = []
    while Q:
        solution, remain = Q.pop()
        nodes += 1
        # if nodes % 1000000 == 0:
        #     print(f'nodes = {nodes}')
        if len(solution) == width+int(width*width):
            s = solution[width:]
            if solcount % 100000 == 0:
                disp = ' '.join([f'{p[0]}/{p[1]}' for p in solution[width:]])
                print(f'found #{solcount} - mem={mem_mb():.1f}MB')
                right_index = ''
                print_quad(s, width)
                for rownum in range(width):
                    row = s[rownum*width:(rownum+1)*width]
                print(f'right_index = {right_edges(s)}')
                print(f'down_index = {down_edges(s)}')
            arrangements += [s]
            for p in s:
                piece_bm[p[0]].add(solcount)
            right_edge_bm[right_edges(s)].add(solcount)
            down_edge_bm[down_edges(s)].add(solcount)

            solcount += 1
        else:
            up = pieces[solution[-width]][2]
            if len(solution) % width == 0:
                left = 'a'
            else:
                left = pieces[solution[-1]][1]
            for p in fit.get((up, left, False, False),[]):
                (piecenum, rot) = p
                if piecenum in remain:
                    Q += [(solution + [p], remain - set([piecenum]))]
    print(str(solcount) + ' solutions', flush=True)
    print(str(nodes) + ' nodes', flush=True)
    return arrangements, right_edge_bm, down_edge_bm, piece_bm

def search(arrangements, right_edge_bm, down_edge_bm, piece_bm):
    nodes = [0] * 4
    solution_count = [0]

    def fill_quadrant(depth, chosen, forbidden, candidates, q1_down_bm):
        for qi in candidates:
            s = arrangements[qi]
            nodes[depth] += 1

            if depth == 0:
                if qi % 1000 == 0:
                    print(f'trying arrangement {qi} in NW - mem={mem_mb():.1f}MB')
                    print(f'nodes = {nodes}', flush=True)
                next_q1_down_bm = right_edge_bm[down_edges(s)]
            else:
                next_q1_down_bm = q1_down_bm

            new_forbidden = forbidden.copy()
            for p in s:
                new_forbidden = new_forbidden.union(piece_bm[p[0]])

            if depth == 3:
                solution_count[0] += 1
                s1, s2, s3, s4 = arrangements[chosen[0]], arrangements[chosen[1]], arrangements[chosen[2]], s
                print(f'\nq4 solution #{solution_count[0]} ({chosen[0]},{chosen[1]},{chosen[2]},{qi})')
                solution = lr_join_quad(s1, rot_quad(s2, 1)) + \
                    lr_join_quad(rot_quad(s4, 3), rot_quad(s3, 2))
                print_quad(solution, width * 2)
                print('solution=' + ' '.join([f'{p[0]}/{p[1]}' for p in solution]), flush=True)
            else:
                next_candidates = down_edge_bm[right_edges(s)] - new_forbidden
                if depth == 2:
                    next_candidates = next_candidates.intersection(q1_down_bm)
                fill_quadrant(depth + 1, chosen + [qi], new_forbidden, next_candidates, next_q1_down_bm)

    print('bitmaps complete, starting search')
    # only try arrangements in first quadrant that use the first corner piece
    q1_candidates = BitMap(i for i, s in enumerate(arrangements) if s[0][0] == 1)
    fill_quadrant(0, [], BitMap(), q1_candidates, None)
    print(f'nodes = {nodes}')
    return solution_count[0]

if __name__ == '__main__':
    import time
    t0 = time.monotonic()
    arrangements, right_edge_bm, down_edge_bm, piece_bm = build_bitmaps()
    t1 = time.monotonic()
    print(f'build_bitmaps: {fmt_duration(t1-t0)}', flush=True)
    search(arrangements, right_edge_bm, down_edge_bm, piece_bm)
    t2 = time.monotonic()
    print(f'search: {fmt_duration(t2-t1)}', flush=True)
