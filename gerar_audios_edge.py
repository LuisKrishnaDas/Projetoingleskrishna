
import argparse
import asyncio
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
VOICE = "en-US-AriaNeural"


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[^a-z0-9' ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def load_cards(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    cards = data.get("cards") if isinstance(data, dict) else None

    if not isinstance(cards, list):
        raise ValueError("Backup inválido: lista cards não encontrada.")

    items = {}
    words = set()
    examples = set()

    for card in cards:
        for field, bucket in (("en", words), ("ex", examples)):
            text = str(card.get(field) or "").strip()
            key = norm(text)
            if text and key:
                bucket.add(key)
                items.setdefault(key, text)

    return items, len(words), len(examples), len(cards)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    items, words, examples, cards = load_cards(args.backup)

    AUDIO_DIR.mkdir(exist_ok=True)
    manifest_path = AUDIO_DIR / "manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        manifest = {}

    pending = []

    for key, text in items.items():
        filename = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20] + ".mp3"
        rel = "audio/" + filename
        target = ROOT / rel

        if target.exists():
            manifest[key] = rel
        else:
            pending.append((key, text, filename, rel))

    if args.limit > 0:
        pending = pending[:args.limit]

    print(f"Cartões: {cards}")
    print(f"Expressões: {words}")
    print(f"Frases de exemplo: {examples}")
    print(f"Textos únicos: {len(items)}")
    print(f"Áudios pendentes neste lote: {len(pending)}")
    print(f"Voz: {VOICE}")

    if not pending:
        print("Nenhum áudio pendente!")
        return

    confirm = input(f"\nGerar {len(pending)} áudios? [s/N] ").strip().lower()

    if confirm not in ("s", "sim"):
        print("Cancelado.")
        return

    semaphore = asyncio.Semaphore(max(1, min(args.workers, 3)))
    errors = []
    done = 0

    async def generate(item):
        nonlocal done
        key, text, filename, rel = item
        target = AUDIO_DIR / filename

        async with semaphore:
            try:
                communicate = edge_tts.Communicate(
                    text,
                    VOICE,
                    rate="+0%"
                )
                await communicate.save(str(target))

                manifest[key] = rel
                done += 1

                manifest_path.write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )

                print(f"Concluídos: {done}/{len(pending)}")

            except Exception as e:
                errors.append((text, str(e)))
                print(f"Erro em '{text}': {e}")

    await asyncio.gather(*(generate(item) for item in pending))

    print(f"\nFinalizado! {done} áudios gerados.")

    if errors:
        print(f"\nFalhas: {len(errors)}")
        for text, error in errors[:20]:
            print(f"- {text}: {error}")

    print(f"Manifesto: {manifest_path}")


if __name__ == "__main__":
    asyncio.run(main())
