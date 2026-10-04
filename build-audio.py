#!/usr/bin/env python3
"""Irasyti visa pamokos garsa i failus ElevenLabs balsu.

    python3 build-audio.py            # irasyti truksamus (abi kalbos)
    python3 build-audio.py lt         # tik lietuviskai
    python3 build-audio.py --force    # perirasyti viska
    python3 build-audio.py --list     # parodyti balsus ir modelius (ir ar yra lietuviu k.)
    python3 build-audio.py --voice <id>   # jei raktas apribotas tik i Text to Speech

Raktas imamas is elevenlabs-key.txt (arba ELEVENLABS_API_KEY).
Balsas: ELEVENLABS_VOICE_ID arba pirmas paskyros balsas.

Po to audio/en/*.mp3 groja ir vietoje, ir publikuotame puslapyje – serverio
ir rakto ten nebereikia. Pakeitus pamokos teksta index.html, paleisk is naujo:
skriptas pats issitraukia sakinius is index.html i lines.en.json.
"""
import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ("en", "lt")
sys.path.insert(0, ROOT)
import server  # noqa: E402  (raktas, balso parinkimas, el_tts)


def load_lines(lang):
    """Sakiniai imami is lines.<lang>.json - tas pats failas, kuri skaito ir appsas."""
    with open(os.path.join(ROOT, "lines.%s.json" % lang), encoding="utf-8") as f:
        return json.load(f)


def list_voices():
    print("Balsai paskyroje:")
    try:
        for v in server.el_voices():
            labels = v.get("labels") or {}
            print("  %-24s %s  %s" % (v.get("name", "?"), v["voice_id"],
                                      ", ".join("%s=%s" % kv for kv in labels.items())))
    except Exception as e:
        print("  (saraso gauti negalima - raktui neduota Voices teisiu: %s)" % e)
        print("  Balsa nurodyk ranka: build-audio.py --voice <id>")
    print("\nModeliai anglu kalbai (geriausias pirmas):")
    for m in server.el_model_list("en"):
        print("  " + m)
    lt = server.el_model_list("lt")
    print("\nModeliai lietuviu kalbai: %s" % (", ".join(lt) if lt else "nera"))


def build(lang, force):
    print("  %s balsas: %s" % (lang, server.el_voice_id(lang)))
    out = os.path.join(ROOT, "audio", lang)
    os.makedirs(out, exist_ok=True)
    lines = load_lines(lang)
    made = kept = 0
    for key, item in lines.items():
        if key == "intro":                 # ivadas tik rodomas, nekalbamas
            continue
        # eilute gali buti tekstas arba {"text": rodomas, "say": skaitomas}
        text = item.get("say") or item["text"] if isinstance(item, dict) else item
        path = os.path.join(out, key + ".mp3")
        if os.path.exists(path) and not force:
            kept += 1
            continue
        open(path, "wb").write(server.el_tts(text, lang))
        made += 1
        print("  %s/%-7s %s" % (lang, key, text[:56]))
    ids = sorted(k[:-4] for k in os.listdir(out) if k.endswith(".mp3"))
    json.dump({"voice": server.EL_STATE["voice"], "model": server.EL_STATE["model"], "ids": ids},
              open(os.path.join(out, "manifest.json"), "w", encoding="utf-8"), indent=2)
    size = sum(os.path.getsize(os.path.join(out, i + ".mp3")) for i in ids)
    print("  %s: irasyta %d, seni %d, viso %d (%.1f MB)" % (lang, made, kept, len(ids), size / 1048576))


def main():
    force = "--force" in sys.argv
    if "--voice" in sys.argv:                    # jei raktas apribotas tik i Text to Speech
        server.EL_STATE["voice"] = sys.argv[sys.argv.index("--voice") + 1]
    for flag in ("--modelis", "--model"):
        if flag in sys.argv:
            server.EL_STATE["model"] = sys.argv[sys.argv.index(flag) + 1]
    if not server.EL_KEY:
        raise SystemExit("Nera ElevenLabs rakto. Paleisk: python3 save-key.py")
    if "--list" in sys.argv:
        return list_voices()

    langs = [a for a in sys.argv[1:] if a in LANGS] or list(LANGS)
    print("Modelis: %s" % (server.EL_STATE["model"] or "naujausias, kuri turi paskyra"))
    for lang in langs:
        build(lang, force)


if __name__ == "__main__":
    main()
