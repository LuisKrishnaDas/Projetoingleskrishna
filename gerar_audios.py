#!/usr/bin/env python3
"""Gera MP3s de pronúncia em lote com a API da ElevenLabs.

A chave é solicitada sem eco no terminal e não é gravada em arquivo.
Lê o backup JSON exportado pelo Meu Inglês e cria audio/manifest.json.
"""
import argparse, concurrent.futures, getpass, hashlib, json, os, re, sys, time, unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = 'https://api.elevenlabs.io/v1'
ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / 'audio'
MODEL = 'eleven_multilingual_v2'


def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = s.replace('’', "'").replace('‘', "'")
    s = re.sub(r"[^a-z0-9' ]", '', s)
    return re.sub(r'\s+', ' ', s).strip()


def api(method, url, key, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = Request(url, data=data, method=method, headers={
        'xi-api-key': key,
        'Accept': 'application/json' if method == 'GET' else 'audio/mpeg',
        'Content-Type': 'application/json',
    })
    with urlopen(req, timeout=90) as response:
        return response.read(), response.headers.get('Content-Type', '')


def get_key(args):
    key = args.api_key or os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        key = input('Cole sua chave API da ElevenLabs: ').strip()
    if not key:
        print('Chave API não informada.', file=sys.stderr); sys.exit(2)
    return key


def list_voices(key):
    raw, _ = api('GET', BASE + '/voices', key)
    data = json.loads(raw.decode('utf-8'))
    print('\nVOZES DISPONÍVEIS NA SUA CONTA\n')
    for v in data.get('voices', []):
        labels = v.get('labels') or {}
        accent = labels.get('accent', '')
        gender = labels.get('gender', '')
        desc = ' · '.join(x for x in [gender, accent, v.get('category', '')] if x)
        print(f"{v.get('name','(sem nome)')}\n  ID: {v.get('voice_id','')}\n  {desc}\n")


def load_cards(path, include_examples=True):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    cards = data.get('cards') if isinstance(data, dict) else None
    if not isinstance(cards, list):
        raise ValueError('O JSON não parece ser um backup do Meu Inglês (não encontrei a lista cards).')
    words, examples, unique = set(), set(), {}
    for card in cards:
        for field, bucket in (('en', words), ('ex', examples)):
            if field == 'ex' and not include_examples:
                continue
            text = str(card.get(field) or '').strip()
            key = norm(text)
            if text and key:
                bucket.add(key)
                unique.setdefault(key, text)
    return unique, len(words), len(examples), len(cards)


def main():
    p = argparse.ArgumentParser(description='Gera os áudios de pronúncia do Meu Inglês em lote.')
    p.add_argument('--backup', help='Caminho do backup JSON exportado pelo aplicativo')
    p.add_argument('--voice-id', help='ID da voz escolhida na ElevenLabs')
    p.add_argument('--api-key', help='Evite usar esta opção; prefira digitar a chave no prompt')
    p.add_argument('--listar-vozes', action='store_true', help='Mostra as vozes disponíveis na sua conta')
    p.add_argument('--workers', type=int, default=2, help='Gera até este número de áudios em paralelo (padrão: 2)')
    p.add_argument('--limit', type=int, default=0, help='Limita a geração aos primeiros N áudios (teste)')
    p.add_argument('--dry-run', action='store_true', help='Mostra quantidade e caracteres, sem gerar áudios')
    p.add_argument('--only-words', action='store_true', help='Gera apenas os áudios das expressões dos cartões, sem as frases de exemplo')
    args = p.parse_args()
    if args.listar_vozes:
        key = get_key(args)
        try: list_voices(key)
        except Exception as e: print(f'Erro ao consultar vozes: {e}', file=sys.stderr); sys.exit(1)
        return
    if not args.backup:
        p.error('Informe --backup caminho-do-backup.json')
    if not args.voice_id:
        p.error('Informe --voice-id com o ID da voz escolhida na ElevenLabs')
    try:
        items, word_count, example_count, card_count = load_cards(args.backup, include_examples=not args.only_words)
    except Exception as e:
        print(f'Não consegui ler o backup: {e}', file=sys.stderr); sys.exit(1)
    total_chars = sum(len(t) for t in items.values())
    AUDIO_DIR.mkdir(exist_ok=True)
    manifest_path = AUDIO_DIR / 'manifest.json'
    try: manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception: manifest = {}
    pending = []
    for key_text, text in items.items():
        filename = hashlib.sha256(key_text.encode('utf-8')).hexdigest()[:20] + '.mp3'
        rel = 'audio/' + filename
        if not (ROOT / rel).exists(): pending.append((key_text, text, filename, rel))
        else: manifest[key_text] = rel
    if args.limit > 0:
    	pending = pending[:args.limit]
    print(f'Cartões no backup: {card_count}')
    print(f'Expressões dos cartões: {word_count}')
    print(f'Frases de exemplo: {example_count}')
    print(f'Textos únicos para áudio: {len(items)}')
    print(f'Caracteres de texto a sintetizar: {total_chars:,}')
    print(f'Áudios já existentes: {len(items)-len(pending)} | Pendentes: {len(pending)}')
    if args.dry_run:
        print('\nPrévia concluída. Nenhum áudio foi gerado e nenhuma chave foi solicitada.'); return
    print('\nA geração usa sua conta ElevenLabs. Confira os créditos disponíveis antes de continuar.')
    confirm = input(f'Gerar {len(pending)} arquivos MP3 agora? [s/N] ').strip().lower()
    if confirm not in ('s', 'sim', 'y', 'yes'):
        print('Cancelado. Nenhum novo áudio foi gerado.'); return
    key = get_key(args)

    def generate(item):
        key_text, text, filename, rel = item
        url = f"{BASE}/text-to-speech/{quote(args.voice_id, safe='')}?output_format=mp3_44100_128"
        payload = {
            'text': text,
            'model_id': MODEL,
            'voice_settings': {'stability': 0.48, 'similarity_boost': 0.78, 'style': 0.15, 'use_speaker_boost': True}
        }
        for attempt in range(5):
            try:
                audio, _ = api('POST', url, key, payload)
                target = AUDIO_DIR / filename
                target.write_bytes(audio)
                return key_text, rel, len(audio), None
            except HTTPError as e:
                detail = e.read().decode('utf-8', 'replace')[:500]
                if e.code == 429 or 500 <= e.code < 600:
                    time.sleep(min(3 * (attempt + 1), 15)); continue
                return key_text, rel, 0, f'HTTP {e.code}: {detail}'
            except (URLError, TimeoutError, OSError) as e:
                time.sleep(min(3 * (attempt + 1), 15))
                if attempt == 4: return key_text, rel, 0, str(e)
        return key_text, rel, 0, 'Falha após várias tentativas'

    errors, done, total_bytes = [], 0, 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 3))) as pool:
        futures = [pool.submit(generate, item) for item in pending]
        for future in concurrent.futures.as_completed(futures):
            key_text, rel, size, error = future.result()
            if error: errors.append((key_text, error))
            else: manifest[key_text] = rel; done += 1; total_bytes += size
            if (done + len(errors)) % 10 == 0 or done + len(errors) == len(pending):
                print(f'Progresso: {done + len(errors)}/{len(pending)} processados · {done} concluídos · {len(errors)} erros')
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nConcluído! {done} áudios gerados ({total_bytes/1024/1024:.1f} MB).')
    print(f'Manifesto: {manifest_path}')
    if errors:
        print(f'\n{len(errors)} falhas (rode o mesmo comando novamente para tentar só os que faltaram):')
        for word, err in errors[:20]: print(f' - {word}: {err}')
    print('\nAgora publique a pasta inteira meu_ingles_netlify no Netlify. Não envie sua chave API para o site.')

if __name__ == '__main__': main()
