#!/usr/bin/env python3
"""Pasiklausyti to paties sakinio keliais balsais - issirinkti geriausia lietuviu kalbai.

    python3 balsai.py                     # bando sakini su problematiskais zodziais
    python3 balsai.py "savas tekstas"     # bando tavo sakini
    python3 balsai.py --balsas Charlotte  # tik vienas balsas

Issirinkus:  python3 build-audio.py lt --force --voice <id>
(arba parasyk Claude balso varda - jis perrasys viska).
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import server  # noqa: E402

# vieši ElevenLabs balsai, prieinami visoms paskyroms
VOICES = [
    ("Lily",      "pFZP5JQG7iQjIQuC4Bku", "dabartinis, anglų"),
    ("Charlotte", "XB0fDUnXU5powFXDhCwa", "švediškas atspalvis – dažnai geriau su Europos kalbomis"),
    ("Matilda",   "XrExE9yKIg1WjnnlVkGX", "šilta, neutrali"),
    ("Laura",     "FGY2WhTYpPnrIDTdsKH5", "gyvesnė, jaunesnė"),
    ("Alice",     "Xb7hH8MSUJpSbSDYk0k2", "aiški, britiška"),
    ("Daniel",    "onwK4e9ZLuTAKqWW03F9", "vyriškas, ramus"),
]

DEFAULT = ("Misijoje Artemis du keturi astronautai skrenda aplink Mėnulį. "
           "Visas fazių ratas trunka apie dvidešimt devynias su puse paros.")


def main():
    argv = sys.argv[1:]
    only = None
    if "--balsas" in argv:
        i = argv.index("--balsas")
        only = argv[i + 1].lower() if i + 1 < len(argv) else None
        del argv[i:i + 2]
    text = argv[0] if argv else DEFAULT

    print("Sakinys: %s\n" % text)
    for name, vid, note in VOICES:
        if only and name.lower() != only:
            continue
        print("  %-10s %s" % (name, note))
        server.EL_STATE["voice"] = vid
        try:
            data = server.el_tts(text, "lt")
        except Exception as e:
            print("     nepavyko: %s" % e)
            continue
        tmp = os.path.join(tempfile.gettempdir(), "balsas-%s.mp3" % name)
        open(tmp, "wb").write(data)
        subprocess.run(["afplay", tmp], check=False)
    print("\nPatikus:  python3 build-audio.py lt --force --voice <id>")
    for name, vid, _ in VOICES:
        print("    %-10s %s" % (name, vid))


if __name__ == "__main__":
    main()
