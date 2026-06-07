from e2quad import build_bitmaps, search

def test_q4_solution_count():
    arrangements, right_edge_bm, down_edge_bm, piece_bm = build_bitmaps()
    count = search(arrangements, right_edge_bm, down_edge_bm, piece_bm)
    assert count == 65
