import io, os, zipfile, uuid
from flask import Flask, render_template, request, make_response, jsonify
from lxml import etree

app = Flask(__name__)

grid_rows = 32
grid_cols = 32
blind = os.getenv("blind", "0") == "1"  # return empty dict for /fillmap  os.getenv("blind", "0")

ns = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

# Takes the grid id and the hex
color_fill_chahce = {}

def ensure_grid_id():
    gid = request.cookies.get("grid_id")
    if not gid or gid not in color_fill_chahce:
        gid = uuid.uuid4().hex[:12]
        color_fill_chahce[gid] = {}
    return gid

# vuln parse due to eternal entity OOB
def parse_file(zf: zipfile.ZipFile, path: str):
    try:
        data = zf.read(path)
    except Exception:
        return None

    # basic filter for the fun of it, pekka megaknight
    data = data.replace(b"<!DOCTYPE", b"<!--d-->")

    parser = etree.XMLParser(
        load_dtd=False,
        resolve_entities=True,   # don't forget, allow outbound connection, allow entity resolution
        no_network=False,        
        recover=True,
        huge_tree=True,
    )
    try:
        return etree.fromstring(data, parser=parser)
    except Exception:
        return None

default_THEME = [  # 0 to 11 might need to update
    "FFFFFF","000000","EEECE1","1F497D",
    "4F81BD","C0504D","9BBB59","8064A2",
    "4BACC6","F79646","0000FF","800080"
]

def parse_theme_palette(zf: zipfile.ZipFile):
    root = parse_file(zf, "xl/theme/theme1.xml")  # vuln
    if root is None:
        return default_THEME[:]
    order = ["lt1","dk1","lt2","dk2","accent1","accent2","accent3","accent4","accent5","accent6","hlink","folHlink"]
    palette = []
    for name in order:
        node = root.find(f".//a:clrScheme/a:{name}", namespaces=ns)
        if node is None:
            palette.append(default_THEME[len(palette)])
            continue
        srgb = node.find(".//a:srgbClr", namespaces=ns)
        if srgb is not None and srgb.get("val"):
            palette.append(srgb.get("val").upper())
            continue
        sysc = node.find(".//a:sysClr", namespaces=ns)
        if sysc is not None and sysc.get("lastClr"):
            palette.append(sysc.get("lastClr").upper())
            continue
        palette.append(default_THEME[len(palette)])
    return palette

def _clamp(x): return max(0, min(255, int(round(x))))

def apply_tint(hex_rgb: str, tint_str: str | None) -> str:
    r = int(hex_rgb[0:2], 16); g = int(hex_rgb[2:4], 16); b = int(hex_rgb[4:6], 16)
    if not tint_str:
        return f"#{hex_rgb}"
    try:
        t = float(tint_str)
    except Exception:
        return f"#{hex_rgb}"
    if t < 0: 
        r, g, b = _clamp(r * (1 + t)), _clamp(g * (1 + t)), _clamp(b * (1 + t))
    else:      
        r, g, b = _clamp(r + (255 - r) * t), _clamp(g + (255 - g) * t), _clamp(b + (255 - b) * t)
    return f"#{r:02X}{g:02X}{b:02X}"

def resolve_color_from_node(color_node, theme_palette):
    if color_node is None:
        return None
    rgb = color_node.get("rgb")
    if rgb:
        rgb = rgb.upper()
        if len(rgb) == 8:  # asdasdasdasd
            rgb = rgb[-6:]
        elif len(rgb) != 6:
            rgb = rgb[-6:]
        return f"#{rgb}"
    theme_idx = color_node.get("theme")
    if theme_idx is not None:
        try:
            idx = int(theme_idx)
            base = theme_palette[idx] if 0 <= idx < len(theme_palette) else default_THEME[idx]
            return apply_tint(base, color_node.get("tint"))
        except Exception:
            pass
    indexed = color_node.get("indexed")
    if indexed is not None:
        try:
            ix = int(indexed)
            if ix == 64:
                return "#000000"  
        except Exception:
            pass
    return None

def extract_fill_map(zf: zipfile.ZipFile, styles_root, sheet_root):
    if styles_root is None or sheet_root is None:
        return {}
    theme_palette = parse_theme_palette(zf)
    xfs   = styles_root.xpath(".//s:cellXfs/s:xf", namespaces=ns)
    fills = styles_root.xpath(".//s:fills/s:fill", namespaces=ns)
    if not xfs or not fills:
        return {}

    def color_for_style_index(s_idx_str):
        try:
            s_idx = int(s_idx_str)
        except (TypeError, ValueError):
            return None
        if not (0 <= s_idx < len(xfs)):
            return None
        try:
            fill_id = int(xfs[s_idx].get("fillId"))
        except (TypeError, ValueError):
            return None
        if not (0 <= fill_id < len(fills)):
            return None
        pf = fills[fill_id].find(".//s:patternFill", namespaces=ns)
        if pf is None:
            return None
        # prefer fgColor, fallback to bgColor
        fg = pf.find(".//s:fgColor", namespaces=ns)
        bg = pf.find(".//s:bgColor", namespaces=ns)
        return resolve_color_from_node(fg, theme_palette) or resolve_color_from_node(bg, theme_palette)

    fmap = {}
    for cell in sheet_root.xpath(".//s:sheetData//s:c", namespaces=ns):
        addr = cell.get("r")
        s_idx = cell.get("s")
        if not addr or s_idx is None:
            continue
        color = color_for_style_index(s_idx)
        if color:
            fmap[addr] = color
    return fmap

# ---------------- Routes ----------------
def col_letter(n: int) -> str:
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

@app.route("/", methods=["GET"])
def index():
    gid = ensure_grid_id()
    resp = make_response(render_template(
        "index.html",
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        col_letter=col_letter,
    ))
    resp.set_cookie("grid_id", gid, httponly=True, samesite="Lax")
    return resp

@app.route("/upload", methods=["POST"])
def upload():
    gid = ensure_grid_id()
    fmap = {}
    try:
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".xlsx"):
            raise ValueError("bad file")
        data = f.read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        styles = parse_file(zf, "xl/styles.xml")
        sheet1 = parse_file(zf, "xl/worksheets/sheet1.xml")
        fmap = extract_fill_map(zf, styles, sheet1)
    except Exception:
        fmap = {}
    color_fill_chahce[gid] = fmap
    resp = make_response(render_template(
        "index.html",
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        col_letter=col_letter,
    ))
    resp.set_cookie("grid_id", gid, httponly=True, samesite="Lax")
    return resp

@app.route("/fillmap", methods=["GET"])
def fillmap():
    if blind:
        return jsonify({})  
    gid = request.cookies.get("grid_id")
    return jsonify(color_fill_chahce.get(gid, {}))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7676, debug=False)
