"""The widgets' 3x5 pixel font, as an OWL map literal (glyph rows, x lit, . dark).

Lowercase text is upper()-ed before drawing; accented capitals map to their plain glyph here.
"""
FONT = {
    " ": "...|...|...|...|...",
    "A": ".x.|x.x|xxx|x.x|x.x", "B": "xx.|x.x|xx.|x.x|xx.", "C": ".xx|x..|x..|x..|.xx",
    "D": "xx.|x.x|x.x|x.x|xx.", "E": "xxx|x..|xxx|x..|xxx", "F": "xxx|x..|xx.|x..|x..",
    "G": ".xx|x..|x.x|x.x|.xx", "H": "x.x|x.x|xxx|x.x|x.x", "I": "xxx|.x.|.x.|.x.|xxx",
    "J": "..x|..x|..x|x.x|.x.", "K": "x.x|x.x|xx.|x.x|x.x", "L": "x..|x..|x..|x..|xxx",
    "M": "x.x|xxx|xxx|x.x|x.x", "N": "xx.|x.x|x.x|x.x|x.x", "O": ".x.|x.x|x.x|x.x|.x.",
    "P": "xx.|x.x|xx.|x..|x..", "Q": ".x.|x.x|x.x|xx.|.xx", "R": "xx.|x.x|xx.|x.x|x.x",
    "S": ".xx|x..|.x.|..x|xx.", "T": "xxx|.x.|.x.|.x.|.x.", "U": "x.x|x.x|x.x|x.x|xxx",
    "V": "x.x|x.x|x.x|x.x|.x.", "W": "x.x|x.x|xxx|xxx|x.x", "X": "x.x|x.x|.x.|x.x|x.x",
    "Y": "x.x|x.x|.x.|.x.|.x.", "Z": "xxx|..x|.x.|x..|xxx",
    "0": "xxx|x.x|x.x|x.x|xxx", "1": ".x.|xx.|.x.|.x.|xxx", "2": "xxx|..x|xxx|x..|xxx",
    "3": "xxx|..x|xxx|..x|xxx", "4": "x.x|x.x|xxx|..x|..x", "5": "xxx|x..|xxx|..x|xxx",
    "6": "xxx|x..|xxx|x.x|xxx", "7": "xxx|..x|..x|..x|..x", "8": "xxx|x.x|xxx|x.x|xxx",
    "9": "xxx|x.x|xxx|..x|xxx",
    "°": ".x.|x.x|.x.|...|...", "-": "...|...|xxx|...|...", "↑": ".x.|xxx|.x.|.x.|.x.",
    "↓": ".x.|.x.|.x.|xxx|.x.", ".": "...|...|...|...|.x.", ",": "...|...|...|.x.|x..",
    ":": "...|.x.|...|.x.|...", "/": "..x|..x|.x.|x..|x..", "'": ".x.|.x.|...|...|...",
    "(": ".x.|x..|x..|x..|.x.", ")": ".x.|..x|..x|..x|.x.", "+": "...|.x.|xxx|.x.|...",
    "%": "x.x|..x|.x.|x..|x.x", "@": "xxx|x.x|x.x|x..|.xx", "·": "...|...|.x.|...|...",
    "_": "...|...|...|...|xxx", "!": ".x.|.x.|.x.|...|.x.", "?": "xx.|..x|.x.|...|.x.",
    "#": "x.x|xxx|x.x|xxx|x.x", "&": ".x.|x.x|.x.|x.x|.xx", "=": "...|xxx|...|xxx|...",
    "<": "..x|.x.|x..|.x.|..x", ">": "x..|.x.|..x|.x.|x..", "[": "xx.|x..|x..|x..|xx.",
    "]": ".xx|..x|..x|..x|.xx", "*": "...|x.x|.x.|x.x|...", "~": "...|.x.|x.x|...|...",
    "↗": ".xx|..x|.x.|x..|...",
}
for plain, accented in {"A": "ÀÁÂÃÄÅ", "C": "Ç", "E": "ÈÉÊË", "I": "ÌÍÎÏ", "N": "Ñ", "O": "ÒÓÔÕÖ", "U": "ÙÚÛÜ", "Y": "Ý"}.items():
    for ch in accented:
        FONT[ch] = FONT[plain]
UNKNOWN = "x.x|.x.|x.x|.x.|x.x"

if __name__ == "__main__":
    for c, g in FONT.items():
        rows = g.split("|")
        assert len(rows) == 5 and all(len(r) == 3 and set(r) <= {"x", "."} for r in rows), c
    esc = lambda c: c.replace("\\", "\\\\").replace('"', '\\"')
    items = ['"%s": [%s]' % (esc(c), ", ".join('"%s"' % r for r in g.split("|"))) for c, g in FONT.items()]
    print("  let font = {")
    for i in range(0, len(items), 3):
        print("    " + ", ".join(items[i:i + 3]) + ("," if i + 3 < len(items) else ""))
    print("  }")
    print('  let unknownGlyph = [%s]' % ", ".join('"%s"' % r for r in UNKNOWN.split("|")))
