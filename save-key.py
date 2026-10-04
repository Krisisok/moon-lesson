#!/usr/bin/env python3
"""Irasyti ElevenLabs rakta i elevenlabs-key.txt - tik jei ElevenLabs ji priima.

Raktas nerodomas ekrane ir nelieka terminalo istorijoje.
Sprendzia pats ElevenLabs serveris, ne formato taisykle.
"""
import getpass, os, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "elevenlabs-key.txt")


def check(key):
    """(ok, zinute) - tikra uzklausa i ElevenLabs."""
    last = "ElevenLabs nepriemė rakto"
    for path in ("/v1/user", "/v1/models", "/v1/voices"):
        req = urllib.request.Request("https://api.elevenlabs.io" + path,
                                     headers={"xi-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=20):
                return True, "raktas veikia"
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return True, "raktas veikia (apribotas tik i Text to Speech - tai gerai)"
            last = "ElevenLabs sako: neteisingas raktas" if e.code == 401 else "ElevenLabs klaida %d" % e.code
        except Exception as e:
            return False, "nepavyko pasiekti ElevenLabs: %s" % e
    return False, last


def shape(key):
    parts = key.split("_")
    return "%d simboliai, %d dalis (-ys) atskirtos _, pradzia %s..." % (
        len(key), len(parts), key[:3])


def main():
    key = getpass.getpass("Iklijuok ElevenLabs rakta ir spausk Enter (teksto nesimatys): ").strip()
    if not key:
        sys.exit("Nieko neiklijuota - failo nekeiciu.")

    print("Tikrinu...")
    ok, msg = check(key)
    if not ok:
        print("\nNeirasiau: %s." % msg)
        print("Tai, ka iklijavai: %s" % shape(key))
        print("Tikras raktas atrodo kaip sk_ + viena istisine eilute be tarpu, ~67 simboliai.")
        print("\nKa daryti:")
        print("  1. ElevenLabs -> Settings -> API Keys -> Create API Key")
        print("  2. spausk kopijavimo mygtuka salia rakto (ne pele zymek)")
        print("  3. paleisk si skripta ir klijuok VIENA karta (cmd+V), tada Enter")
        sys.exit(1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write("# ElevenLabs raktas. Lieka tik siame kompiuteryje.\n")
        f.write(key + "\n")
    os.chmod(PATH, 0o600)
    print("Gerai - %s. Irasyta." % msg)
    print("Dabar parasyk Claude 'yra'.")


if __name__ == "__main__":
    main()
