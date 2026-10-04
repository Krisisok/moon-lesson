#!/usr/bin/env python3
"""Perklausyti jau irasyta pamoka ir rasti, kur tarimas negeras.

    python3 klausyk.py lt            # visa pamoka is eiles
    python3 klausyk.py lt b3 b4 q2   # tik nurodytus sakinius
    python3 klausyk.py lt --nuo b3   # nuo si sakinio iki galo

Nieko negeneruoja - groja audio/<kalba>/*.mp3. Prie kiekvieno parodo rakta,
kuri paskui nurodysi taisant: python3 tarimas.py lt b4 "kitoks rasymas"
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ORDER = (["b%d" % i for i in range(5)]
         + sum([["q%d" % i, "ok%d" % i, "no%d" % i] for i in range(3)], [])
         + ["again", "tap", "done3"])


def main():
    argv = sys.argv[1:]
    lang = argv[0] if argv and argv[0] in ("lt", "en") else "lt"
    rest = [a for a in argv if a not in ("lt", "en")]
    start = None
    if "--nuo" in rest:
        i = rest.index("--nuo")
        start = rest[i + 1] if i + 1 < len(rest) else None
        del rest[i:i + 2]

    keys = rest or list(ORDER)
    if start and start in keys:
        keys = keys[keys.index(start):]

    with open(os.path.join(ROOT, "lines.%s.json" % lang), encoding="utf-8") as f:
        lines = json.load(f)

    print("Groju %d sakinius. Uzsirasyk raktus, kurie skamba blogai.\n" % len(keys))
    for key in keys:
        item = lines.get(key)
        if item is None:
            continue
        text = item["text"] if isinstance(item, dict) else item
        path = os.path.join(ROOT, "audio", lang, key + ".mp3")
        if not os.path.exists(path):
            print("  %-7s (nera iraso)" % key)
            continue
        print("  %-7s %s" % (key, text))
        subprocess.run(["afplay", path], check=False)
    print("\nTaisymas:  python3 tarimas.py %s <raktas> \"kitoks rasymas\"" % lang)


if __name__ == "__main__":
    main()
