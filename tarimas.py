#!/usr/bin/env python3
"""Pasiklausyti, kaip balsas pasako sakini - ir issaugoti pataisyta tarima.

    python3 tarimas.py lt b2
        pasako, kaip skamba dabar

    python3 tarimas.py lt b2 "Todėl Mėnulis tarsi keičia formą..."
        pasako tavo varianta (nieko neissaugo - gali bandyti kiek nori)

    python3 tarimas.py lt b2 --modelis eleven_v3
        pasako kitu modeliu (v4, v4_turbo, v3, v3_conversational)

    python3 tarimas.py lt b2 "..." --saugoti
        issaugo si varianta kaip tarima ir perirašo ta viena mp3.
        Mokinys ekrane ir toliau mato originalu teksta.

Sakiniu raktai: b0-b4 (pasakojimas), q0-q2 (klausimai),
ok0-ok2 (teisingai), no0-no2 (paaiskinimai), again, tap, done0-done3.
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import server  # noqa: E402


def lines_path(lang):
    return os.path.join(ROOT, "lines.%s.json" % lang)


def load(lang):
    with open(lines_path(lang), encoding="utf-8") as f:
        return json.load(f)


def shown(item):
    return item["text"] if isinstance(item, dict) else item


def spoken(item):
    return (item.get("say") or item["text"]) if isinstance(item, dict) else item


def take_flag(argv, name):
    """--name reiksme -> reiksme (ir isima is saraso)."""
    if name in argv:
        i = argv.index(name)
        val = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
        return val
    return None


def main():
    argv = sys.argv[1:]
    model = take_flag(argv, "--modelis") or take_flag(argv, "--model")
    if model:
        server.EL_STATE["model"] = model
    args = [a for a in argv if a != "--saugoti"]
    save = "--saugoti" in argv
    if len(args) < 2:
        sys.exit(__doc__)
    lang, key = args[0], args[1]
    if lang not in ("lt", "en"):
        sys.exit("Pirma nurodyk kalba: lt arba en.")
    data = load(lang)
    if key not in data:
        sys.exit("Nera tokio sakinio: %s. Yra: %s" % (key, ", ".join(data)))

    variant = args[2] if len(args) > 2 else spoken(data[key])
    print("Mokinys mato : %s" % shown(data[key]))
    print("Balsas skaito: %s" % variant)
    print("Modelis      : %s" % (server.EL_STATE["model"] or "naujausias, kuri turi paskyra"))
    print("Generuoju...")
    try:
        audio = server.el_tts(variant, lang)
    except Exception as e:
        sys.exit("Nepavyko: %s" % e)

    tmp = os.path.join(tempfile.gettempdir(), "tarimas-%s-%s.mp3" % (lang, key))
    open(tmp, "wb").write(audio)
    try:
        subprocess.run(["afplay", tmp], check=False)
    except FileNotFoundError:
        print("(negaliu groti; failas: %s)" % tmp)

    if not save:
        print("\nJei tinka, pakartok su --saugoti gale.")
        return

    item = data[key]
    text = shown(item)
    data[key] = {"text": text, "say": variant} if variant != text else text
    with open(lines_path(lang), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    out = os.path.join(ROOT, "audio", lang, key + ".mp3")
    open(out, "wb").write(audio)
    print("\nIsaugota. Perrasyta: %s" % out)
    print("Perkrauk puslapi - pamoka jau su nauju tarimu.")


if __name__ == "__main__":
    main()
