from e2quad import build_bitmaps, search
from e2row import build_bitmaps as row_build_bitmaps, search as row_search

def test_q4_solution_count():
    arrangements, right_edge_bm, down_edge_bm, piece_bm = build_bitmaps()
    count = search(arrangements, right_edge_bm, down_edge_bm, piece_bm)
    assert count == 65

def test_row_solution_count():
    arrangements, top_edge_bm, bottom_edge_bm, piece_bm = row_build_bitmaps()
    count = row_search(arrangements, top_edge_bm, bottom_edge_bm, piece_bm)
    assert count == 65
