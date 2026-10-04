# Mėnulio pamoka

**Išbandyk: https://krisisok.github.io/moon-lesson/**

Pamoka mokiniui apie Mėnulio fazes: sukasi vizualas, balsas pasakoja, gale — trys klausimai, į kuriuos atsakoma balsu. Pritaikyta disleksiją turintiems vaikams: pirmiausia vaizdas ir garsas, tekstas paryškinamas žodis po žodžio tiems, kas skaito.

Du mygtukai: **LT/EN** ir **Start / Stop**. Pamoką pradeda ir Mėnulio palietimas. Apatinė juosta peršoka į bet kurią dalį.

Maža pamoka mokiniui: vizualas + balsas + klausimai balsu.
Pritaikyta disleksiją turintiems vaikams (vaizdas ir garsas pirmiau, tekstas — tik kas gerai skaito).

## Kaip paleisti

```bash
python3 "/Users/kristina/Downloads/editai-2026-09-10/01-vizualizaciju-tipai/moon-pamoka/server.py" 8755
```
Tada naršyklėje: http://localhost:8755

Mikrofonas veikia tik per `localhost` arba `https` — Chrome ar Safari paprašys leidimo.

## Kas iš kur

- **Vizualas** — `../moon/index.html` variklis (three.js, NASA CGI Moon Kit tekstūros).
- **Turinys** — EditAI bibliotekos projektas „Artemis II: The 10-Day Survival Challenge"
  (Year 6 · The World Around Us): 4 astronautai, 10 parų, kelionė aplink Mėnulį.

## Balsas

Geriausias variantas — **įrašyti pamoką ElevenLabs balsu į failus**:

```bash
# 1. raktą įklijuok į elevenlabs-key.txt (šalia server.py)
python3 build-audio.py --list     # pažiūrėti balsus ir modelius
python3 build-audio.py            # įrašyti audio/en/*.mp3
```

Tada garsas groja iš failų — ir vietoje, ir publikuotame puslapyje: serverio ir rakto
ten nebereikia. Pakeitus pamokos tekstą paleisk `build-audio.py --force` iš naujo.

Atsarginė grandinė, jei įrašų nėra: `server.py` → ElevenLabs → Google balsas →
naršyklės sistemos balsas.

Balsą galima pasirinkti: `ELEVENLABS_VOICE_ID`. Modelį skriptas parenka pats
(naujesnis — pirmiau), bet galima nurodyti `ELEVENLABS_MODEL`.

## Tarimas (kirčiavimas)

Jei balsas kurį žodį kirčiuoja ne taip, keičiamas **tik tai, ką balsas skaito** —
mokinys ekrane mato tą patį tekstą:

```bash
python3 tarimas.py lt b2                       # pasiklausyti, kaip skamba dabar
python3 tarimas.py lt b2 "kitoks rašymas"      # pabandyti variantą
python3 tarimas.py lt b2 "kitoks rašymas" --saugoti   # išsaugoti ir perrašyti mp3
```

Techniškai: `lines.lt.json` eilutė tampa `{"text": rodoma, "say": skaitoma}`.

## Pamokos eiga

5 pasakojimo dalys → 3 klausimai balsu. Neteisingai atsakius — paaiškina kodėl.
Jei mikrofono nėra, klausimas parodo atsakymų mygtukus.

## Mygtukai

Du: **LT/EN** ir **Start / Stop / Resume**. Pamoką taip pat pradeda palietus Mėnulį.

## Kalbos

Abi: anglų ir lietuvių. Balsas — ElevenLabs **Lily**, modelis **eleven_v4** (85 kalbos, tarp jų lietuvių).
Sakiniai: `lines.en.json`, `lines.lt.json`. Garsas: `audio/en/`, `audio/lt/`.
