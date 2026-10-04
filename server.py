#!/usr/bin/env python3
"""moon-pamoka: statinis serveris + /tts (lietuviškas / angliškas balsas).

macOS neturi lietuviško sintezės balso, todėl /tts paima garsą iš Google
Translate TTS serverio puse (naršyklei tiesiogiai jis neleidžia). Tekstas
siunčiamas tik pamokos sakinių pavidalu, be jokių asmens duomenų.
"""
import http.server, socketserver, urllib.parse, urllib.request, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = {}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# --- ElevenLabs (nebutinas) -------------------------------------------------
# Raktas: failas elevenlabs-key.txt salia sio failo arba ELEVENLABS_API_KEY.
# I HTML raktas niekada nepatenka - visada lieka serverio puseje.
# Nebutini: ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL.
ROOT_KEY_FILE = "elevenlabs-key.txt"


def _read_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if k:
        return k
    try:
        for line in open(os.path.join(ROOT, ROOT_KEY_FILE), encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    except Exception:
        pass
    return ""


EL_KEY = _read_key()
EL_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
EL_MODEL = os.environ.get("ELEVENLABS_MODEL", "").strip()
# naujesnis modelis - pirmiau; sarasas imamas is paciu ElevenLabs, ne is atminties
MODEL_PREFERENCE = ("v4", "v3", "multilingual_v2", "turbo_v2_5", "flash_v2_5")
# jei raktui neduota teisiu i /v1/models, bandome siuos is eiles
KNOWN_MODELS = ("eleven_v3", "eleven_turbo_v2_5", "eleven_multilingual_v2", "eleven_flash_v2_5")
EL_STATE = {"voice": EL_VOICE, "model": EL_MODEL or None, "off": not EL_KEY}


def el_get(path, timeout=20):
    req = urllib.request.Request("https://api.elevenlabs.io" + path,
                                 headers={"xi-api-key": EL_KEY})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def el_voices():
    return el_get("/v1/voices").get("voices", [])


def voice_for_lang(lang):
    """Balsas tai kalbai is balsai.json (jei yra)."""
    try:
        with open(os.path.join(ROOT, "balsai.json"), encoding="utf-8") as f:
            v = json.load(f).get(lang) or {}
        return v.get("id", "")
    except Exception:
        return ""


def voice_from_manifest():
    """Balsas, kuriuo jau irasyta pamoka (audio/<kalba>/manifest.json)."""
    for lang in ("en", "lt"):
        try:
            with open(os.path.join(ROOT, "audio", lang, "manifest.json"), encoding="utf-8") as f:
                v = json.load(f).get("voice")
            if v:
                return v
        except Exception:
            pass
    return ""


def el_voice_id(lang=None):
    if EL_STATE["voice"]:
        return EL_STATE["voice"]
    v = voice_for_lang(lang) if lang else ""
    if v:
        return v
    v = voice_from_manifest()
    if v:
        EL_STATE["voice"] = v
        return v
    try:
        voices = el_voices()
    except Exception as e:
        raise RuntimeError(
            "Nepavyko gauti balsu saraso (%s). Jei raktas apribotas tik i Text to Speech, "
            "nurodyk balsa: ELEVENLABS_VOICE_ID=<id> arba build-audio.py --voice <id>." % e)
    if not voices:
        raise RuntimeError("ElevenLabs: paskyroje nera balsu")
    EL_STATE["voice"] = voices[0]["voice_id"]
    sys.stderr.write("ElevenLabs balsas: %s\n" % voices[0].get("name", "?"))
    return EL_STATE["voice"]


def el_model_list(lang="en"):
    """Modeliai, mokantys sia kalba - geriausias pirmas."""
    out = []
    try:
        for m in el_get("/v1/models"):
            if not m.get("can_do_text_to_speech", True):
                continue
            langs = {l.get("language_id") for l in (m.get("languages") or [])}
            if langs and lang not in langs:
                continue
            out.append(m["model_id"])
    except Exception as e:
        sys.stderr.write("Nepavyko gauti modeliu saraso: %s\n" % e)
    ranked = []
    for pref in MODEL_PREFERENCE:
        ranked += [m for m in out if pref in m and m not in ranked]
    ranked += [m for m in out if m not in ranked]
    return ranked or list(KNOWN_MODELS)


def el_supports(lang):
    """Ar paskyra turi modeli, mokanti sia kalba (pvz. 'lt')."""
    try:
        return [m for m in el_model_list(lang)] if EL_KEY else []
    except Exception:
        return []


def el_tts(text, lang="en"):
    vid = el_voice_id(lang)
    models = [EL_STATE["model"]] if EL_STATE["model"] else el_model_list(lang)
    last = None
    for m in models:
        try:
            req = urllib.request.Request(
                "https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128" % vid,
                data=json.dumps({"text": text, "model_id": m}).encode("utf-8"),
                headers={"Content-Type": "application/json", "xi-api-key": EL_KEY,
                         "Accept": "audio/mpeg"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if EL_STATE["model"] != m:
                sys.stderr.write("ElevenLabs modelis: %s\n" % m)
            EL_STATE["model"] = m
            return data
        except Exception as e:
            last = e
            sys.stderr.write("Modelis %s neveike: %s\n" % (m, e))
    raise last or RuntimeError("ElevenLabs neveikia")


def chunks(text, n=170):
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out or [""]


def google_tts(text, tl):
    parts, data = chunks(text), b""
    for i, p in enumerate(parts):
        url = "https://translate.google.com/translate_tts?" + urllib.parse.urlencode({
            "ie": "UTF-8", "client": "tw-ob", "tl": tl, "q": p,
            "idx": i, "total": len(parts), "textlen": len(p)})
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            data += r.read()
    return data


def fetch(text, tl):
    key = tl + "|" + text
    if key in CACHE:
        return CACHE[key]
    data = None
    if not EL_STATE["off"]:
        try:
            data = el_tts(text, tl)
        except Exception as e:
            sys.stderr.write("ElevenLabs isjungtas, naudojam Google: %s\n" % e)
            EL_STATE["off"] = True
    if data is None:
        data = google_tts(text, tl)
    CACHE[key] = data
    return data


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if self.path.startswith("/tts"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            text = (qs.get("q") or [""])[0].strip()
            tl = (qs.get("tl") or ["lt"])[0]
            if tl not in ("lt", "en"):
                tl = "lt"
            if not text:
                self.send_error(400, "no text"); return
            try:
                data = fetch(text, tl)
            except Exception as e:
                sys.stderr.write("TTS failed: %s\n" % e)
                self.send_error(502, "tts unavailable"); return
            try:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        return super().do_GET()

    def end_headers(self):
        # puslapio ir tekstu nekesuojam (kad redaguojant nerodytu seno),
        # garso irasus - kesuojam
        if not self.path.startswith("/audio/"):
            self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8755
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    except OSError as e:
        if getattr(e, "errno", None) == 48:
            print("Serveris jau veikia. Atidaryk narsykleje: http://localhost:%d" % port)
            print("(diagnostika: http://localhost:%d/?diag=1)" % port)
            sys.exit(0)
        raise
    with httpd:
        print("moon-pamoka -> http://localhost:%d  (balsas: %s)" % (port, "ElevenLabs" if not EL_STATE["off"] else "Google"), flush=True)
        httpd.serve_forever()
