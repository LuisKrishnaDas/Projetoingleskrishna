#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera áudios bilíngues para o Meu Inglês a partir de palavras_novas.txt.

Formato de cada linha:
    actually — na verdade

Instalação:
    py -m pip install edge-tts

Exemplo:
    py gerar_lista_bilingue_thalita.py --limit 4 --workers 2
"""

import argparse
import asyncio
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
DEFAULT_LIST = ROOT / "palavras_novas.txt"
AUDIO_DIR = ROOT / "audio"
MANIFEST_PATH = AUDIO_DIR / "manifest.json"
VOICE = "pt-BR-ThalitaMultilingualNeural"
MAX_WORKERS = 3


def norm(text):
    """Normaliza textos para formar chaves estáveis no manifesto."""
    text = unicodedata.normalize("NFD", str(text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_list_path(value):
    """Resolve --lista: primeiro relativo à pasta atual, depois à pasta do script."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return ROOT / path


def load_items(list_path):
    """
    Lê linhas no formato inglês — português.
    Retorna itens únicos por chave de manifesto, preservando a grafia original.
    """
    path = Path(list_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {path}\n"
            "Crie palavras_novas.txt na mesma pasta do script ou use --lista."
        )

    items = {}
    ignored = 0
    duplicates = 0

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Aceita o travessão solicitado (—) e também meia-risca (–).
        parts = re.split(r"\s+[—–]\s+", line, maxsplit=1)
        if len(parts) != 2:
            print(
                f"Aviso: linha {line_number} ignorada "
                "(use: expressão em inglês — tradução em português)."
            )
            ignored += 1
            continue

        english = parts[0].strip()
        portuguese = parts[1].strip()
        en_norm = norm(english)
        pt_norm = norm(portuguese)

        if not english or not portuguese or not en_norm or not pt_norm:
            print(f"Aviso: linha {line_number} ignorada (texto vazio ou inválido).")
            ignored += 1
            continue

        for language, text, normalized in (
            ("en", english, en_norm),
            ("pt", portuguese, pt_norm),
        ):
            key = f"{language}|{normalized}"
            if key in items:
                duplicates += 1
            else:
                items[key] = (text, language)

    return items, ignored, duplicates


def load_manifest():
    """Carrega o manifesto existente sem descartar nenhuma entrada anterior."""
    if not MANIFEST_PATH.exists():
        return {}

    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"O manifesto existente não contém JSON válido: {MANIFEST_PATH}\n"
            "Por segurança, ele não será substituído. Corrija ou restaure o arquivo."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"O manifesto precisa ser um objeto JSON: {MANIFEST_PATH}\n"
            "Por segurança, ele não será substituído."
        )
    return data


def save_manifest(manifest):
    """Grava todas as entradas, antigas e novas, sem filtrar chaves."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_audio_path(key, language):
    """Usa SHA-256 da chave completa, truncado em 20 caracteres."""
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    filename = f"{language}_{digest}.mp3"
    return f"audio/{filename}", AUDIO_DIR / filename


async def main():
    parser = argparse.ArgumentParser(
        description=(
            "Gera áudios em inglês e português com a voz "
            f"{VOICE} para o aplicativo Meu Inglês."
        )
    )
    parser.add_argument(
        "--lista",
        default=str(DEFAULT_LIST),
        help="Arquivo TXT de entrada (padrão: palavras_novas.txt ao lado do script).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limita a quantidade de novos arquivos MP3 nesta execução (0 = sem limite).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Quantidade de tarefas simultâneas (de 1 a 3; padrão: 2).",
    )
    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit não pode ser negativo.")
    if not 1 <= args.workers <= MAX_WORKERS:
        parser.error("--workers deve ser um número entre 1 e 3.")

    list_path = resolve_list_path(args.lista)
    items, ignored, duplicates = load_items(list_path)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    pending = []
    existing_count = 0

    # Verifica os dois idiomas separadamente e registra no manifesto qualquer
    # arquivo que já esteja presente, sem sobrescrevê-lo.
    for key, (text, language) in items.items():
        relative_path, target = build_audio_path(key, language)
        if target.is_file():
            manifest[key] = relative_path
            existing_count += 1
        else:
            pending.append((key, text, relative_path, target))

    total_identified = len(items)
    total_pending_before_limit = len(pending)
    if args.limit:
        pending = pending[:args.limit]

    print("\n=== Meu Inglês | Gerador bilíngue Thalita ===")
    print(f"Lista utilizada: {list_path}")
    print(f"Linhas válidas (pares inglês/português): {total_identified // 2}")
    print(f"Textos/áudios identificados: {total_identified}")
    print(f"Áudios já existentes: {existing_count}")
    print(f"Novos áudios pendentes: {total_pending_before_limit}")
    if args.limit:
        print(f"Limite desta execução: {args.limit}")
        print(f"Áudios selecionados nesta execução: {len(pending)}")
    print(f"Linhas ignoradas: {ignored}")
    print(f"Textos repetidos ignorados: {duplicates}")
    print(f"Tarefas simultâneas: {args.workers}")
    print(f"Voz única nos dois idiomas: {VOICE}")

    if not pending:
        # Sincroniza no manifesto os arquivos que já existiam.
        save_manifest(manifest)
        print("\nNenhum áudio novo pendente. Manifesto conferido.")
        return

    confirm = input(
        f"\nDeseja gerar {len(pending)} arquivo(s) MP3? [s/N] "
    ).strip().lower()
    if confirm not in ("s", "sim"):
        print("Operação cancelada. Nenhum áudio novo foi gerado.")
        return

    semaphore = asyncio.Semaphore(args.workers)
    manifest_lock = asyncio.Lock()
    errors = []
    completed = 0
    total_to_generate = len(pending)

    async def generate(item, index):
        nonlocal completed
        key, text, relative_path, target = item
        temp_target = target.with_name(target.stem + ".part.mp3")

        async with semaphore:
            try:
                # Se outro processo/execução já criou o destino, não sobrescreve.
                if target.exists():
                    async with manifest_lock:
                        manifest[key] = relative_path
                        save_manifest(manifest)
                    completed += 1
                    print(
                        f"[{index}/{total_to_generate}] Já existia; preservado: "
                        f"{relative_path}"
                    )
                    return

                communicate = edge_tts.Communicate(
                    text=text,
                    voice=VOICE,
                    rate="+0%",
                )
                await communicate.save(str(temp_target))

                # Publica o arquivo somente depois de a geração terminar.
                # Se já houver destino, mantém o arquivo antigo intacto.
                if target.exists():
                    temp_target.unlink(missing_ok=True)
                else:
                    temp_target.replace(target)

                async with manifest_lock:
                    manifest[key] = relative_path
                    # Salva após cada novo áudio para permitir retomada.
                    save_manifest(manifest)

                completed += 1
                print(
                    f"[{index}/{total_to_generate}] OK — "
                    f"{key} -> {relative_path}"
                )

            except Exception as exc:
                try:
                    temp_target.unlink(missing_ok=True)
                except OSError:
                    pass
                errors.append((key, text, str(exc)))
                print(f"[{index}/{total_to_generate}] FALHA — {key}: {exc}")

    await asyncio.gather(
        *(generate(item, index) for index, item in enumerate(pending, start=1))
    )

    print("\n=== Resultado ===")
    print(f"Novos áudios concluídos: {completed}/{total_to_generate}")
    print(f"Entradas totais no manifesto: {len(manifest)}")
    print(f"Manifesto: {MANIFEST_PATH}")

    if errors:
        print(f"\nFalhas individuais: {len(errors)}")
        for key, text, error in errors:
            print(f"- {key} ({text}): {error}")
        print(
            "\nExecute novamente o mesmo comando. "
            "Os arquivos concluídos serão preservados e somente os faltantes "
            "serão tentados novamente."
        )
    else:
        print("\nTodos os áudios selecionados foram processados com sucesso.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário. "
              "O manifesto mantém o progresso salvo até o último áudio concluído.")
    except Exception as exc:
        print(f"\nERRO: {exc}")
        raise
