#!/usr/bin/env python3
import argparse
import secrets
import sys
import zipfile
from pathlib import Path

#Edit this if you wnat to change where it is injected
SHEET1_PATH = "xl/worksheets/sheet1.xml"

def replace_sheet(in_path: Path, out_path: Path, sheet_payload: bytes) -> None:
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    with zipfile.ZipFile(in_path, "r") as zin, zipfile.ZipFile(out_path, "w") as zout:
        found = False
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == SHEET1_PATH:
                found = True
                zi = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                zi.create_system = info.create_system
                zout.writestr(zi, sheet_payload)
            else:
                zout.writestr(info, data)
        if not found:
            zi = zipfile.ZipInfo(filename=SHEET1_PATH)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, sheet_payload)

def read_payload_interactive() -> str:
    print("\n=== Paste your sheet1.xml payload or payload for any file (end with Ctrl+Z+Enter on Windows or Ctrl+D on macOS/Linux).")
    print("=== Or type a single line 'EOF' to finish. Leave empty to use the default payload.\n")
    buf = []
    try:
        # If something piped in, read it all.
        if not sys.stdin.isatty():
            return sys.stdin.read()
        # Otherwise, read this line-by-line until EOF sentinel or OS EOF. (Crtl+Z on windows)
        while True:
            line = sys.stdin.readline()
            if not line:
                break  # OS EOF
            if line.strip() == "EOF":
                break
            buf.append(line)
    except KeyboardInterrupt:
        pass
    content = "".join(buf).strip()
    return content

def main(argv=None):
    p = argparse.ArgumentParser(description="Replace xl/worksheets/sheet1.xml in an .xlsx with your payload (interactive-friendly).")
    p.add_argument("input", nargs="?", type=Path, default=Path("demo.xlsx"), help="Source .xlsx (default: demo.xlsx)")
    args = p.parse_args(argv)

    out = args.input.with_suffix(".xxe.xlsx")

    # 1) Decide payload texts
    if args.input:
        pasted = read_payload_interactive()
        if pasted:
            sheet_text = pasted

    # 2) Write output file with replacement
    replace_sheet(args.input, out, sheet_text.encode("utf-8"))

    print(f"\n[+] Wrote: {out}")
    print(f"[+] Replaced: {SHEET1_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
