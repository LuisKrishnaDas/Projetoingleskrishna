"""Gera MP3 para frases de um .txt (uma por linha) e registra no audio/manifest.json.

Uso (na pasta do app, ao lado de audio/):
    pip install edge-tts
    python gerar_audios_lista.py frases_aulas_sem_audio.txt
    python gerar_audios_lista.py frases_aulas_sem_audio.txt --dry-run   (só mostra o que faria)
"""
import argparse, asyncio, hashlib, json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
MANIFEST = AUDIO_DIR / "manifest.json"
VOICE = "pt-BR-ThalitaMultilingualNeural"  # mesma voz do gerar_audios_bilingue.py
LANG = "en"


def norm(text):  # idêntico ao norm() do app e dos outros scripts
    text = unicodedata.normalize("NFD", str(text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    frases = [l.strip() for l in Path(a.arquivo).read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig")) if MANIFEST.exists() else {}
    AUDIO_DIR.mkdir(exist_ok=True)

    pendentes = []
    for texto in frases:
        chave = f"{LANG}|{norm(texto)}"
        rel = f"audio/{LANG}_{hashlib.sha256(chave.encode('utf-8')).hexdigest()[:20]}.mp3"
        if (ROOT / rel).exists():
            manifest[chave] = rel          # arquivo já existe: só registra
        elif chave not in manifest:
            pendentes.append((chave, texto, rel))

    print(f"{len(frases)} frases, {len(pendentes)} para gerar.")
    if a.dry_run:
        for _, t, r in pendentes[:5]:
            print("  ", r, "<-", t)
        return

    import edge_tts
    for i, (chave, texto, rel) in enumerate(pendentes, 1):
        try:
            await edge_tts.Communicate(texto, VOICE, rate="+0%").save(str(ROOT / rel))
            manifest[chave] = rel
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{i}/{len(pendentes)} {texto}")
        except Exception as e:
            print(f"Erro em '{texto}': {e}")
    print("Pronto. Publique de novo a pasta inteira (com audio/ e manifest.json).")


asyncio.run(main())
