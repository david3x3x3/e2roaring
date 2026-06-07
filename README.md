# e2roaring

A puzzle solver for quadrant-based tile puzzles, using [PyRoaring](https://github.com/Ezibenroc/PyRoaring) bitmaps to efficiently search for valid piece arrangements.

## How it works

The solver operates in two phases:

1. **Quadrant search** — finds all valid arrangements of pieces within a single quadrant, indexing them by their edge signatures.
2. **Full puzzle assembly** — uses bitmap intersection to quickly find four quadrants whose edges align, then assembles them into a complete solution.

## Setup

```bash
python -m venv venv
venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Usage

```bash
python e2quad.py
```
