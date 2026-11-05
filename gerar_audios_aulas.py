"""Gera os MP3 das frases das Aulas (lista em frases_aulas_sem_audio.txt)
e registra tudo no audio/manifest.json, no mesmo formato dos outros scripts.

Uso (na pasta do projeto):
    python gerar_audios_aulas.py --dry-run     # só mostra o que falta
    python gerar_audios_aulas.py --limit 4     # teste com 4 áudios
    python gerar_audios_aulas.py               # gera e registra
Requer:  pip install edge-tts
"""
import argparse
import asyncio
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
MANIFEST_PATH = AUDIO_DIR / "manifest.json"
LISTA = ROOT / "frases_aulas_sem_audio.txt"
VOICE = "pt-BR-ThalitaMultilingualNeural"  # mesma voz do gerar_audios_bilingue.py


def norm(text):
    text = unicodedata.normalize("NFD", str(text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="gera só N áudios (teste)")
    args = ap.parse_args()

    frases = [l.strip() for l in LISTA.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig")) if MANIFEST_PATH.exists() else {}

    pending = []
    for texto in frases:
        key = "en|" + norm(texto)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
        rel = f"audio/en_{digest}.mp3"
        target = ROOT / rel
        if target.exists():
            manifest[key] = rel          # arquivo já existe: só registra
        else:
            pending.append((key, texto, rel, target))

    if args.limit > 0:
        pending = pending[:args.limit]
    print(f"Frases na lista: {len(frases)} | MP3 a gerar: {len(pending)}")
    if args.dry_run:
        for _, t, rel, _ in pending[:10]:
            print(" ", rel, "<-", t)
        return

    import edge_tts  # importado aqui para o --dry-run funcionar sem a biblioteca
    AUDIO_DIR.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(3)

    async def gerar(item):
        key, texto, rel, target = item
        async with sem:
            await edge_tts.Communicate(texto, VOICE, rate="+0%").save(str(target))
            manifest[key] = rel
            print("OK:", texto)

    await asyncio.gather(*(gerar(i) for i in pending), return_exceptions=False)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Manifesto atualizado:", len(manifest), "entradas")


if __name__ == "__main__":
    asyncio.run(main())
