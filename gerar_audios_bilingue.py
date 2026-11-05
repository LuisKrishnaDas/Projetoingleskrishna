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
MANIFEST_PATH = AUDIO_DIR / "manifest.json"
VOICE = "pt-BR-ThalitaMultilingualNeural"


def norm(text):
    text = unicodedata.normalize("NFD", str(text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_items(backup_path):
    data = json.loads(Path(backup_path).read_text(encoding="utf-8-sig"))
    cards = data.get("cards") if isinstance(data, dict) else None
    if not isinstance(cards, list):
        raise ValueError("Backup inválido: lista 'cards' não encontrada.")

    items = {}
    counts = {"en": 0, "pt": 0, "ex": 0}

    for card in cards:
        for field, language in (("en", "en"), ("pt", "pt"), ("ex", "en")):
            text = str(card.get(field) or "").strip()
            key_text = norm(text)
            if not text or not key_text:
                continue
            counts[field] += 1
            manifest_key = f"{language}|{key_text}"
            items.setdefault(manifest_key, (text, language))

    return items, counts, len(cards)


async def main():
    parser = argparse.ArgumentParser(
        description="Gera áudios em inglês e português para o Meu Inglês."
    )
    parser.add_argument("--backup", required=True, help="Caminho do backup JSON.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limita a quantidade de áudios para teste.")
    parser.add_argument("--workers", type=int, default=2,
                        help="Gera simultaneamente até 3 áudios.")
    args = parser.parse_args()

    items, counts, total_cards = load_items(args.backup)
    AUDIO_DIR.mkdir(exist_ok=True)

    # Mantém apenas chaves do novo formato bilíngue no manifesto.
    try:
        old_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if not isinstance(old_manifest, dict):
            old_manifest = {}
    except Exception:
        old_manifest = {}

    manifest = {
        key: value for key, value in old_manifest.items()
        if key.startswith("en|") or key.startswith("pt|")
    }

    pending = []
    for key, (text, language) in items.items():
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
        filename = f"{language}_{digest}.mp3"
        relative_path = f"audio/{filename}"
        target = ROOT / relative_path

        if target.exists():
            manifest[key] = relative_path
        else:
            pending.append((key, text, relative_path, target))

    if args.limit > 0:
        pending = pending[:args.limit]

    print(f"Cartões encontrados: {total_cards}")
    print(f"Expressões em inglês: {counts['en']}")
    print(f"Traduções em português: {counts['pt']}")
    print(f"Frases de exemplo em inglês: {counts['ex']}")
    print(f"Textos únicos por idioma: {len(items)}")
    print(f"Áudios pendentes: {len(pending)}")
    print(f"Voz usada nos dois idiomas: {VOICE}")

    if not pending:
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print("Nenhum áudio pendente. Manifesto conferido!")
        return

    confirm = input(f"\nGerar {len(pending)} áudios? [s/N] ").strip().lower()
    if confirm not in ("s", "sim"):
        print("Cancelado.")
        return

    semaphore = asyncio.Semaphore(max(1, min(args.workers, 3)))
    errors = []
    completed = 0

    async def generate(item):
        nonlocal completed
        key, text, relative_path, target = item
        async with semaphore:
            try:
                communicate = edge_tts.Communicate(
                    text,
                    VOICE,
                    rate="+0%"
                )
                await communicate.save(str(target))
                manifest[key] = relative_path
                completed += 1

                # Grava após cada áudio: se houver interrupção, o progresso fica salvo.
                MANIFEST_PATH.write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"Concluídos: {completed}/{len(pending)} — {text}")

            except Exception as exc:
                errors.append((text, str(exc)))
                print(f"Erro em '{text}': {exc}")

    await asyncio.gather(*(generate(item) for item in pending))

    print(f"\nFinalizado! {completed} áudios gerados.")
    print(f"Entradas no manifesto: {len(manifest)}")
    print(f"Manifesto: {MANIFEST_PATH}")

    if errors:
        print(f"\nFalhas: {len(errors)}")
        for text, error in errors[:30]:
            print(f"- {text}: {error}")
        print("\nExecute o mesmo comando novamente para tentar os áudios que faltaram.")


if __name__ == "__main__":
    asyncio.run(main())
