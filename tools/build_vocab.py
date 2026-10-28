#!/usr/bin/env python3
"""Überträgt daten/vokabeln_greenline1.csv in den Datenblock von index.html.

Aufruf (aus dem Repo-Ordner):  python3 tools/build_vocab.py

- Die CSV ist die Master-Datei. Neue Zeilen dürfen eine leere id haben; das
  Skript vergibt dann eine feste id und schreibt sie in die CSV zurück.
- Eine einmal vergebene id NIE ändern: Der Lernstand hängt an der id.
- Akzeptierte Antworten werden aus der Spalte "englisch" abgeleitet
  (Klammern optional, "(= ...)" als Alternative, Kurzformen ausgeschrieben)
  plus alles aus "weitere_antworten" (mit | getrennt).
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "daten", "vokabeln_greenline1.csv")
HTML_PATH = os.path.join(ROOT, "index.html")
START = "/* VOCAB-DATA:START (generiert aus daten/vokabeln_greenline1.csv - nicht von Hand bearbeiten) */"
END = "/* VOCAB-DATA:END */"
FIELDS = ["id", "unit", "station", "englisch", "deutsch", "weitere_antworten", "quelle"]

# Kurzformen ohne Apostroph, die echte andere Wörter wären (we're -> "were")
BAD_SHORT = {"were", "well", "shell", "wed", "hed", "id", "ill", "shed"}
PRONOUN_IS = {"he", "she", "it", "that", "what", "there", "where", "who", "here", "how"}


def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'")
    s = s.replace("…", " ").replace("...", " ")
    s = re.sub(r"\b(sb|sth)\b", " ", s)
    s = re.sub(r"[.!?]", "", s)
    return re.sub(r"\s+", " ", s).strip(" /")


def expand_slashes(s):
    """'there is/are' -> ['there is', 'there are']"""
    out = [""]
    for tok in s.split(" "):
        alts = tok.split("/") if "/" in tok else [tok]
        out = [(o + " " + a).strip() for o in out for a in alts if a]
    return out


def expand_contractions(s):
    res = {s, s.replace("'", "")}
    long = s
    long = re.sub(r"\bcan't\b", "cannot", long)
    long = re.sub(r"\bwon't\b", "will not", long)
    long = re.sub(r"n't\b", " not", long)
    long = re.sub(r"'m\b", " am", long)
    long = re.sub(r"'re\b", " are", long)
    long = re.sub(r"'ll\b", " will", long)
    long = re.sub(r"'ve\b", " have", long)
    long = re.sub(r"\b(\w+)'s\b", lambda m: m.group(1) + " is" if m.group(1) in PRONOUN_IS else m.group(0), long)
    long = re.sub(r"\blet's\b", "let us", long)
    res.add(long)
    return res


def answers(englisch, weitere):
    main = englisch.replace("’", "'")
    alts = []
    for m in re.finditer(r"\(=\s*(.*?)\)", main):
        alts.append(m.group(1))
    main = re.sub(r"\(=\s*.*?\)", "", main)
    main = re.sub(r"\((pl|no pl|£)\)", "", main)
    parts = [p for p in main.split(",") if p.strip()] + alts
    out = []

    def add(x):
        x = norm(x)
        if x and "(" not in x and ")" not in x and x not in BAD_SHORT and x not in out:
            out.append(x)

    for p in parts:
        bases = set()
        if "(" in p:
            bases.add(re.sub(r"\(.*?\)", "", p))           # ohne Klammerinhalt
            bases.add(p.replace("(", "").replace(")", ""))  # mit Klammerinhalt
        else:
            bases.add(p)
        for b in sorted(bases, key=len):
            for v in expand_slashes(norm(b)):
                for c in sorted(expand_contractions(v), key=lambda z: (z != v, z)):
                    add(c)
    for w in (weitere or "").split("|"):
        if w.strip():
            add(w)
    return out


def show_text(englisch):
    s = re.sub(r"\s*\((pl|no pl)\)", "", englisch).replace(" ,", ",")
    return re.sub(r"\s+", " ", s).strip()


def slug(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"\((pl|no pl|= .*?)\)", "", s).split(",")[0]
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "x"


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = {r["id"].strip() for r in rows if r.get("id", "").strip()}
    dupes = [i for i in ids if sum(1 for r in rows if r["id"].strip() == i) > 1]
    if dupes:
        sys.exit("Doppelte id in der CSV: " + ", ".join(sorted(dupes)))
    changed = False
    for r in rows:
        for k in FIELDS:
            r[k] = (r.get(k) or "").strip()
        if not r["unit"] or not r["englisch"] or not r["deutsch"]:
            sys.exit("Zeile unvollständig (unit/englisch/deutsch fehlt): %r" % r)
        if not r["id"]:
            base = ".".join(p for p in (r["unit"], r["station"], slug(r["englisch"])) if p)
            new, n = base, 2
            while new in ids:
                new, n = "%s-%d" % (base, n), n + 1
            r["id"] = new
            ids.add(new)
            changed = True
    if changed:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows({k: r[k] for k in FIELDS} for r in rows)

    lines = []
    for r in rows:
        entry = {"id": r["id"], "u": r["unit"], "s": r["station"], "de": r["deutsch"],
                 "en": answers(r["englisch"], r["weitere_antworten"]), "show": show_text(r["englisch"])}
        lines.append("  " + json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + ",")
    block = START + "\nconst VOCAB = [\n" + "\n".join(lines) + "\n];\n" + END

    html = open(HTML_PATH, encoding="utf-8").read()
    a, b = html.find(START), html.find(END)
    if a < 0 or b < 0:
        sys.exit("Marker für den Datenblock in index.html nicht gefunden.")
    html = html[:a] + block + html[b + len(END):]
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("%d Vokabeln nach index.html übertragen%s." % (len(rows), " (neue ids in CSV ergänzt)" if changed else ""))


if __name__ == "__main__":
    main()
