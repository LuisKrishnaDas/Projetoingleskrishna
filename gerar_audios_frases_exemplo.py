#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera áudios EN/PT para frases completas de exemplo do Meu Inglês.

Entrada: frases_exemplo_bilingues.csv
Colunas obrigatórias: frase_en;frase_pt
A coluna frase_pt deve conter a tradução natural em português da frase inteira.
Instalação: py -m pip install edge-tts
Teste: py gerar_audios_frases_exemplo.py --limit 4
"""
import argparse, asyncio, csv, hashlib, json, re, unicodedata
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "frases_exemplo_bilingues.csv"
AUDIO_DIR = ROOT / "audio"
MANIFEST = AUDIO_DIR / "manifest.json"
VOICE = "pt-BR-ThalitaMultilingualNeural"
MAX_WORKERS = 3

def norm(value):
    value = unicodedata.normalize("NFD", str(value or "").lower())
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = value.replace("’", "'").replace("‘", "'")
    value = re.sub(r"[^a-z0-9' ]", "", value)
    return re.sub(r"\s+", " ", value).strip()

def load_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096); f.seek(0)
        try: dialect = csv.Sniffer().sniff(sample, delimiters=";,\\t")
        except csv.Error: dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))
    result=[]; seen=set()
    for line, row in enumerate(rows, start=2):
        en=(row.get("frase_en") or "").strip()
        pt=(row.get("frase_pt") or "").strip()
        if not en and not pt: continue
        if not en or not pt:
            raise ValueError(f"Linha {line}: preencha frase_en e frase_pt. Nenhum áudio foi gerado.")
        for lang, text in (("en",en),("pt",pt)):
            key=f"{lang}|{norm(text)}"
            if not norm(text): raise ValueError(f"Linha {line}: texto inválido.")
            if key not in seen:
                result.append((key,text,lang)); seen.add(key)
    if not result: raise ValueError("CSV sem frases bilingues válidas.")
    return result

def load_manifest():
    if not MANIFEST.exists(): return {}
    data=json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    if not isinstance(data,dict): raise ValueError("manifest.json não é um objeto JSON; arquivo preservado.")
    return data

def save_manifest(data):
    tmp=MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(MANIFEST)

def audio_target(key,lang):
    digest=hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    name=f"{lang}_{digest}.mp3"
    return f"audio/{name}", AUDIO_DIR/name

async def main():
    ap=argparse.ArgumentParser(description="Áudios bilíngues para frases completas de exemplo.")
    ap.add_argument("--lista",default=str(CSV_PATH),help="CSV bilíngue.")
    ap.add_argument("--limit",type=int,default=0,help="Máximo de novos MP3 (0 = todos).")
    ap.add_argument("--workers",type=int,default=2,help="Concorrência de 1 a 3.")
    args=ap.parse_args()
    if args.limit<0: ap.error("--limit não pode ser negativo")
    if not 1<=args.workers<=MAX_WORKERS: ap.error("--workers deve ser de 1 a 3")
    path=Path(args.lista)
    if not path.is_absolute() and not path.exists(): path=ROOT/path
    rows=load_rows(path)
    AUDIO_DIR.mkdir(parents=True,exist_ok=True)
    manifest=load_manifest()
    pending=[]; existing=0
    for key,text,lang in rows:
        rel,target=audio_target(key,lang)
        if target.is_file():
            manifest.setdefault(key,rel); existing+=1
        else: pending.append((key,text,lang,rel,target))
    if args.limit: pending=pending[:args.limit]
    sem=asyncio.Semaphore(args.workers)
    done=0
    async def generate(item):
        nonlocal done
        key,text,lang,rel,target=item
        async with sem:
            voice=VOICE
            communicate=edge_tts.Communicate(text,voice)
            await communicate.save(str(target))
        manifest[key]=rel
        save_manifest(manifest)
        done+=1
        print(f"[{done}] {lang.upper()} salvo: {target.name}")
    print(f"Frases/idiomas identificados: {len(rows)} | já existentes: {existing} | pendentes: {len(pending)}")
    if not pending:
        print("Nada a gerar. Verifique se o CSV tem traduções preenchidas.")
        return
    await asyncio.gather(*(generate(x) for x in pending))
    print(f"Concluído: {done} novos áudios. Manifesto atualizado sem apagar entradas anteriores.")

if __name__=="__main__":
    asyncio.run(main())
