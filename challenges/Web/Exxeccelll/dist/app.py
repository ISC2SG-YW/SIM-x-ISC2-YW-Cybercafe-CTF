import os
import re
import secrets
import zipfile
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from color_helpers import resolve_cellid_to_color, parser as UNSAFE_XML_PARSER

GRID_COLS = 32
GRID_ROWS = 12

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

UPLOADS = {}


# Helper functions

def col_letter(n: int) -> str:
    s = []
    while n > 0:
        n, r = divmod(n - 1, 26)
        s.append(chr(65 + r))
    return "".join(reversed(s))

_cell_ref_re = re.compile(r"^([A-Z]+)(\d+)$")

def col_letters_to_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n

def in_grid(addr: str) -> bool:
    m = _cell_ref_re.match(addr or "")
    if not m:
        return False
    letters, row_str = m.groups()
    row = int(row_str)
    col_idx = col_letters_to_index(letters)
    return 1 <= row <= GRID_ROWS and 1 <= col_idx <= GRID_COLS

def get_upload_bytes():
    tok = session.get("xlsx_token")
    return UPLOADS.get(tok) if tok else None


# Routes

@app.get("/")
def index():
    return render_template(
        "index.html",
        grid_cols=GRID_COLS,
        grid_rows=GRID_ROWS,
        col_letter=col_letter,
    )

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return redirect(url_for("index"))

    fname = secure_filename(f.filename)
    if not fname.lower().endswith(".xlsx"):
        return redirect(url_for("index"))

    try:
        data = f.read()
        if not data or len(data) > 25 * 1024 * 1024:  # 25MB soft cap
            return redirect(url_for("index"))
        tok = secrets.token_urlsafe(16)
        UPLOADS[tok] = data
        session["xlsx_token"] = tok
    except Exception:
        pass 
    return redirect(url_for("index"))

@app.get("/fillmap")
def fillmap():
    data = get_upload_bytes()
    if not data:
        return jsonify({})

    fmap = {}
    try:
        results = resolve_cellid_to_color(BytesIO(data))
        for item in results:
            (addr, hexclr) = next(iter(item.items()))
            if hexclr and in_grid(addr):
                fmap[addr] = hexclr
    except Exception:
        fmap = {}

    return jsonify(fmap)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7676)
