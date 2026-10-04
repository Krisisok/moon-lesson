#!/usr/bin/env python3
"""Sugeneruoti ir pagroti kelis tos pacios frazes variantus - issirinkti tarima.

    python3 variantai.py b3          # pagroja visus b3 variantus is eiles
    python3 variantai.py b3 b4 q2    # kelis raktus
    python3 variantai.py b4 2 --saugoti    # issaugoti b4 varianta nr. 2

Variantai aprasyti variantai.lt.json. Kiekvienas turi "text" (ka mokinys mato)
ir "say" (ka skaito balsas) - jie gali skirtis.
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import server  # noqa: E402

LANG = "lt"
VAR_PATH = os.path.join(ROOT, "variantai.%s.json" % LANG)
LINES_PATH = os.path.join(ROOT, "lines.%s.json" % LANG)


def play(data):
    tmp = os.path.join(tempfile.gettempdir(), "variantas.mp3")
    open(tmp, "wb").write(data)
    subprocess.run(["afplay", tmp], check=False)


def main():
    argv = sys.argv[1:]
    save = "--saugoti" in argv
    argv = [a for a in argv if a != "--saugoti"]
    variants = json.load(open(VAR_PATH, encoding="utf-8"))

    if save:
        key, num = argv[0], int(argv[1])
        v = variants[key][num - 1]
        lines = json.load(open(LINES_PATH, encoding="utf-8"))
        lines[key] = {"text": v["text"], "say": v["say"]} if v["say"] != v["text"] else v["text"]
        json.dump(lines, open(LINES_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        data = server.el_tts(v["say"], LANG)
        open(os.path.join(ROOT, "audio", LANG, key + ".mp3"), "wb").write(data)
        print("Issaugota %s variantas %d." % (key, num))
        print("  mato  : %s" % v["text"])
        print("  skaito: %s" % v["say"])
        return

    keys = argv or list(variants)
    for key in keys:
        print("\n=== %s ===" % key)
        for i, v in enumerate(variants[key], 1):
            print("  [%d] %s" % (i, v["note"]))
            print("      skaito: %s" % v["say"])
            play(server.el_tts(v["say"], LANG))
    print("\nIssaugoti:  python3 variantai.py <raktas> <numeris> --saugoti")


if __name__ == "__main__":
    main()
