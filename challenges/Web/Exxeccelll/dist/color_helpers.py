import zipfile
from lxml import etree
from io import StringIO, BytesIO

parser = etree.XMLParser(
    resolve_entities=True,
    no_network=False,
    load_dtd=True
)


NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NS_A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

theme_index_names = [
        "lt1", "dk1", "lt2", "dk2",
        "accent1", "accent2", "accent3",
        "accent4", "accent5", "accent6",
        "hlink", "folHlink"
    ]

def extract_styles_and_sheet1(xlsx_path, sheet_filename="sheet1.xml"):
    with zipfile.ZipFile(xlsx_path, "r") as zf:
        styles_bytes = zf.read("xl/styles.xml")
        sheet_bytes = zf.read(f"xl/worksheets/{sheet_filename}")
        theme_bytes = zf.read("xl/theme/theme1.xml")
    return BytesIO(styles_bytes), BytesIO(sheet_bytes), BytesIO(theme_bytes)




def find_all_cells(sheet_bytes):
    # returns a list with a dict of cell id to style id
    root = etree.parse(sheet_bytes, parser)
    out = []
    for c in root.findall(".//s:sheetData/s:row/s:c[@s]", namespaces=NS):
        r = c.get("r")
        s_attr = c.get("s")
        if r is not None and s_attr is not None:
            try:
                out.append({r: int(s_attr)})
            except ValueError:
                out.append({r: s_attr})
    return out


def find_all_cellxfs(styles_bytes):
    # returns a list of dicitonary for each xf entry
    root = etree.parse(styles_bytes, parser)
    cellxfs = root.find(".//s:cellXfs", namespaces=NS)
    out = []
    if cellxfs is None:
        return out
    for i, xf in enumerate(cellxfs.findall("s:xf", namespaces=NS)):
        d = {"index": i}
        # capture common attrs if present
        for k in ("numFmtId", "fontId", "fillId", "borderId", "xfId"):
            v = xf.get(k)
            if v is not None:
                try:
                    d[k] = int(v)
                except ValueError:
                    d[k] = v
        for k in ("applyFill", "applyFont", "applyNumberFormat", "applyBorder", "applyAlignment", "applyProtection"):
            v = xf.get(k)
            if v is not None:
                d[k] = v
        out.append(d)
    return out


def find_all_fills(styles_bytes):
    # return a list of dicitonary of the colors
    root = etree.parse(styles_bytes, parser)
    fills = root.find(".//s:fills", namespaces=NS)
    out = []
    if fills is None:
        return out
    for idx, fill in enumerate(fills.findall("s:fill", namespaces=NS)):
        entry = {"fillId": idx}
        pat = fill.find("s:patternFill", namespaces=NS)
        if pat is not None:
            pt = pat.get("patternType")
            if pt:
                entry["patternType"] = pt
            fg = pat.find("s:fgColor", namespaces=NS)
            if fg is not None:
                fg_d = {}
                for k in ("rgb", "theme", "tint", "indexed"):
                    v = fg.get(k)
                    if v is not None:
                        # normalize types where sensible
                        if k in ("theme", "indexed"):
                            try:
                                v = int(v)
                            except ValueError:
                                pass
                        elif k == "tint":
                            try:
                                v = float(v)
                            except ValueError:
                                pass
                        fg_d[k] = v
                if fg_d:
                    entry["fgColor"] = fg_d
            bg = pat.find("s:bgColor", namespaces=NS)
            if bg is not None:
                bg_d = {}
                for k in ("rgb", "theme", "tint", "indexed"):
                    v = bg.get(k)
                    if v is not None:
                        if k in ("theme", "indexed"):
                            try:
                                v = int(v)
                            except ValueError:
                                pass
                        elif k == "tint":
                            try:
                                v = float(v)
                            except ValueError:
                                pass
                        bg_d[k] = v
                if bg_d:
                    entry["bgColor"] = bg_d
        out.append(entry)
    return out


def find_all_theme_clrscheme(theme_bytes):
    # return a list of dictionary where each dict is e.g. {"dk1": "#000000"}
    root = etree.parse(theme_bytes, parser)
    scheme = root.find(".//a:clrScheme", namespaces=NS_A)
    out = []
    if scheme is None:
        return out
    for child in scheme:
        name = etree.QName(child).localname  # e.g. dk1, lt1, accent1...
        srgb = child.find("a:srgbClr", namespaces=NS_A)
        sysc = child.find("a:sysClr", namespaces=NS_A)
        if srgb is not None and "val" in srgb.attrib:
            val = srgb.get("val")
        elif sysc is not None and "lastClr" in sysc.attrib:
            val = sysc.get("lastClr")
        else:
            val = None
        if val:
            val = val.strip().lstrip("#").upper()
            if len(val) == 6:
                out.append({name: f"#{val}"})
            else:
                # if anything odd like AARRGGBB, coerce to RRGGBB
                if len(val) == 8:
                    out.append({name: f"#{val[2:]}".upper()})
                else:
                    out.append({name: val})
    return out

def resolve_cellid_to_color(excel_file_path):
    # Initializes all of the function to gather to info needed, it should then return a list of a dictionary of the cell_id map to its color
    def _hex_to_rgb_tuple(hexstr):
        h = hexstr.strip().lstrip("#").upper()
        if len(h) == 8:  # AARRGGBB -> use RGB
            h = h[2:]
        if len(h) != 6:
            return None
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def _rgb_to_hex(rgb):
        r, g, b = rgb
        r = max(0, min(255, int(round(r))))
        g = max(0, min(255, int(round(g))))
        b = max(0, min(255, int(round(b))))
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    def _apply_tint(rgb, tint):
        # Excel tint: if tint >= 0 => towards 255, else scale down
        r, g, b = rgb
        if tint is None:
            tint = 0.0
        try:
            tint = float(tint)
        except Exception:
            tint = 0.0
        if tint >= 0:
            return (r*(1 - tint) + 255*tint,
                    g*(1 - tint) + 255*tint,
                    b*(1 - tint) + 255*tint)
        else:
            return (r*(1 + tint),
                    g*(1 + tint),
                    b*(1 + tint))

    # 1) read parts
    styles_io, sheet_io, theme_io = extract_styles_and_sheet1(excel_file_path, "sheet1.xml")

    # 2) parse sheet cells (cell_id -> style index)
    cells_list = find_all_cells(sheet_io)

    # 3) parse cellXfs and fills (need fresh buffers because parses consume streams)
    styles_io2, _, _ = extract_styles_and_sheet1(excel_file_path, "sheet1.xml")
    xfs_list = find_all_cellxfs(styles_io2)

    styles_io3, _, _ = extract_styles_and_sheet1(excel_file_path, "sheet1.xml")
    fills_list = find_all_fills(styles_io3)

    # 4) parse theme -> build index map 0..11 -> hex
    _, _, theme_io2 = extract_styles_and_sheet1(excel_file_path, "sheet1.xml")
    theme_kv = find_all_theme_clrscheme(theme_io2)  # list of {name: "#RRGGBB"}
    theme_map = {}
    for d in theme_kv:
        for k, v in d.items():
            theme_map[k.lower()] = v

    theme_colors = [theme_map.get(n) for n in theme_index_names]  # index -> hex or None

    # helper: resolve a single fill entry to final hex
    def _resolve_fill_to_hex(fill_entry):
        if not fill_entry:
            return None
        if fill_entry.get("patternType") != "solid":
            return None
        fg = fill_entry.get("fgColor")
        if not fg:
            return None

        # direct rgb
        if "rgb" in fg:
            tup = _hex_to_rgb_tuple(str(fg["rgb"]))
            return _rgb_to_hex(tup) if tup else None

        # theme + optional tint
        if "theme" in fg:
            idx = fg.get("theme")
            if isinstance(idx, int) and 0 <= idx < len(theme_colors):
                base_hex = theme_colors[idx]
                if base_hex:
                    base_rgb = _hex_to_rgb_tuple(base_hex)
                    if base_rgb:
                        tinted = _apply_tint(base_rgb, fg.get("tint"))
                        return _rgb_to_hex(tinted)
            return None

        # indexed palette (64 is "automatic")
        if "indexed" in fg:
            if fg.get("indexed") == 64:
                return None
            # legacy palette not implemented
            return None

        return None

    # 5) build map: style index -> fillId
    style_to_fillid = {}
    for xf in xfs_list:
        i = xf.get("index")
        fid = xf.get("fillId", 0)
        if i is not None:
            style_to_fillid[int(i)] = int(fid) if isinstance(fid, int) else 0

    # 6) build map: fillId -> hex
    fillid_to_hex = {}
    for f in fills_list:
        fid = f.get("fillId")
        if fid is None:
            continue
        fillid_to_hex[int(fid)] = _resolve_fill_to_hex(f)

    # 7) resolve each cell
    out = []
    for item in cells_list:
        # item is {cell_ref: s}
        (cell_ref, s_idx) = next(iter(item.items()))
        try:
            s_idx_int = int(s_idx)
        except Exception:
            s_idx_int = 0
        fill_id = style_to_fillid.get(s_idx_int, 0)
        color_hex = fillid_to_hex.get(fill_id)
        out.append({cell_ref: color_hex})

    return out


if __name__ == "__main__":
    test_file = r"Web\Exxeccelll\sol\demo.xlsx"
    styles_io, sheet_io, theme_io = extract_styles_and_sheet1(test_file, "sheet1.xml")
    cells_list = find_all_cells(sheet_io)
    print("cells (r -> s):")
    for item in cells_list:
        print(item)

    xfs_list = find_all_cellxfs(styles_io)
    print("\ncellXfs:")
    for xf in xfs_list:
        print(xf)

    fills_list = find_all_fills(styles_io)
    print("\nfills:")
    for fill in fills_list:
        print(fill)

    theme_list = find_all_theme_clrscheme(theme_io)
    print("\nclrScheme (theme):")
    for t in theme_list:
        print(t)

    print("\ncell -> color:")
    for item in resolve_cellid_to_color(test_file):
        print(item)
