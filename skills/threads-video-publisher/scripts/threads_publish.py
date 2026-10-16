"""Single-video Threads publishing through Zernio; dry-run by default."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE = 'https://zernio.com/api/v1'


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_env(path):
    if path:
        for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
            s = raw.strip()
            if s and not s.startswith('#') and '=' in s:
                key, value = s.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('\"').strip("'"))
    if not os.environ.get('ZERNIO_API_KEY'):
        raise ValueError('ZERNIO_API_KEY is not configured; use an approved environment file')


def api(method, endpoint, body=None, idem=None):
    headers = {'Authorization': 'Bearer ' + os.environ['ZERNIO_API_KEY'], 'Content-Type': 'application/json'}
    if idem:
        headers['Idempotency-Key'] = idem
    data = json.dumps(body).encode('utf-8') if body is not None else None
    request = Request(BASE + endpoint, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=600 if method == 'POST' and endpoint == '/posts' else 60) as response:
            return json.load(response)
    except HTTPError as e:
        raise RuntimeError(f'{method} {endpoint}: HTTP {e.code}; inspect provider response privately') from None


def validate(video, caption, target=None):
    video = Path(video).resolve()
    if video.suffix.lower() != '.mp4' or not video.is_file():
        raise ValueError('A local MP4 file is required')
    if not caption.strip() or len(caption.encode('utf-16-le')) // 2 > 500:
        raise ValueError('Caption must be nonempty and at most 500 UTF-16 units including links/tags')
    if not 0 < video.stat().st_size <= 1_000_000_000:
        raise ValueError('Video exceeds the conservative 1 GB limit or is empty')
    raw = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_type,codec_name,width,height,r_frame_rate', '-of', 'json', str(video)])
    info = json.loads(raw)
    duration = float(info['format']['duration'])
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), {})
    a = next((s for s in info['streams'] if s['codec_type'] == 'audio'), {})
    if v.get('codec_name') != 'h264' or a.get('codec_name') != 'aac':
        raise ValueError('Delivery requires H.264 video and AAC audio')
    if not 0 < duration <= 300:
        raise ValueError('Threads video must be positive and at most 300 seconds')
    if target is not None and abs(duration - float(target)) > .25:
        raise ValueError('Video runtime does not match the requested duration (tolerance 0.25s)')
    return {'path': str(video), 'sha256': digest(video), 'duration': duration,
        'bytes': video.stat().st_size, 'width': v['width'], 'height': v['height'],
        'frame_rate': v['r_frame_rate']}


def unpack(raw):
    return raw.get('post') or raw.get('data') or raw


def check_manifest(manifest):
    info = validate(manifest['video']['path'], manifest['caption'], manifest.get('target_seconds'))
    fingerprint = hashlib.sha256(json.dumps([info['sha256'], manifest['caption'], manifest['account']],
        ensure_ascii=False).encode('utf-8')).hexdigest()
    if info['sha256'] != manifest['video']['sha256'] or fingerprint != manifest['fingerprint']:
        raise ValueError('Manifest is stale or changed; prepare and inspect a new manifest')
    return info


def record_post(raw, state, manifest):
    p = unpack(raw)
    platform = next((x for x in p.get('platforms', []) if x.get('platform') == 'threads'), {})
    data = platform.get('platformSpecificData') or {}
    state.update(status=p.get('status'), platform_status=platform.get('status'),
        url=platform.get('platformPostUrl') or data.get('platformPostUrl') or state.get('url'),
        error=platform.get('error') or data.get('error') or p.get('error'))
    actual = platform.get('customContent')
    if actual is None:
        actual = p.get('content')
    state['registered_caption'] = actual
    state['caption_matches'] = actual == manifest['caption']
    registered = [x.get('url') for x in p.get('mediaItems', [])]
    state['media_matches'] = state.get('media_url') in registered if registered else None
    state['checked_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    return state


def verify(manifest, state_path, rounds=1):
    state = json.loads(state_path.read_text(encoding='utf-8'))
    if state.get('fingerprint') != manifest['fingerprint']:
        raise ValueError('Verification state belongs to a different manifest')
    if not state.get('post_id'):
        raise ValueError('No post ID: reconcile any uncertain create request before creating again')
    for i in range(rounds):
        state = record_post(api('GET', '/posts/' + state['post_id']), state, manifest)
        write(state_path, state)
        if state.get('error') or state.get('status') == 'failed' or state.get('platform_status') == 'failed':
            raise RuntimeError('Provider reports failure; inspect the saved state before any retry')
        published = state.get('platform_status') == 'published' or (state.get('status') == 'published' and not state.get('platform_status'))
        if published and state.get('url'):
            parsed = urlparse(state['url'])
            if parsed.scheme != 'https' or parsed.hostname not in {'www.threads.com', 'threads.com', 'www.threads.net', 'threads.net'}:
                raise ValueError('Unexpected platform URL; inspect before claiming completion')
            if not state['caption_matches'] or state.get('media_matches') is False:
                raise ValueError('Registered caption or media differs from the authorized manifest')
            try:
                with urlopen(Request(state['url'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
                    state['public_http_status'] = response.status
            except HTTPError as e:
                state['public_http_status'] = e.code
            except OSError:
                state['public_http_status'] = None
            state['publication_verified'] = True
            state['playback_reviewed'] = False
            write(state_path, state)
            return state
        if i + 1 < rounds:
            time.sleep(15)
    state['publication_verified'] = False
    write(state_path, state)
    return state


def publish(manifest, state_path):
    info = check_manifest(manifest)
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding='utf-8'))
        if state.get('fingerprint') != manifest['fingerprint']:
            raise ValueError('State belongs to another artifact; do not overwrite it')
        if state.get('post_id'):
            return verify(manifest, state_path, rounds=40)
        if state.get('create_started'):
            raise ValueError('Uncertain prior create: reconcile it in Zernio and save its post_id; no new create sent')
    accounts = api('GET', '/accounts').get('accounts', [])
    chosen = [a for a in accounts if a.get('platform') == 'threads' and a.get('isActive')
        and not a.get('needsReconnection') and manifest['account'] in
        {str(a.get('_id')), str(a.get('username', '')).lstrip('@')}]
    if len(chosen) != 1:
        raise ValueError('Destination must match exactly one active Threads account')
    account = chosen[0]
    pre = api('POST', '/media/presign', {'filename': Path(info['path']).name,
        'contentType': 'video/mp4', 'size': info['bytes']}, manifest['fingerprint'] + '-media')
    with open(info['path'], 'rb') as media:
        request = Request(pre['uploadUrl'], data=media, method='PUT', headers={
            'Content-Type': 'video/mp4', 'Content-Length': str(info['bytes'])})
        with urlopen(request, timeout=600) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError('Media upload failed; no post was created')
    state = {'fingerprint': manifest['fingerprint'], 'account_id': account['_id'],
        'account': account.get('username'), 'media_url': pre['publicUrl'], 'create_started': True}
    write(state_path, state)  # Persist uncertainty marker before the mutating request.
    body = {'content': manifest['caption'], 'platforms': [{'platform': 'threads',
        'accountId': account['_id'], 'customContent': manifest['caption']}],
        'mediaItems': [{'type': 'video', 'url': pre['publicUrl']}], 'publishNow': True}
    raw = api('POST', '/posts', body, manifest['fingerprint'] + '-post')
    p = unpack(raw)
    state['post_id'] = p.get('_id') or p.get('id')
    write(state_path, state)
    if not state['post_id']:
        raise RuntimeError('Create returned no ID: reconcile the saved uncertain request')
    return verify(manifest, state_path, rounds=40)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    accounts = sub.add_parser('accounts'); accounts.add_argument('--env-file')
    prep = sub.add_parser('prepare')
    for name in ['video', 'caption-file', 'account', 'output']:
        prep.add_argument('--' + name, required=True)
    prep.add_argument('--target-seconds', type=float)
    for name in ['publish', 'verify']:
        p = sub.add_parser(name); p.add_argument('manifest'); p.add_argument('--env-file')
        if name == 'publish':
            p.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.command == 'prepare':
        caption = Path(args.caption_file).read_text(encoding='utf-8-sig').strip()
        info = validate(args.video, caption, args.target_seconds)
        account = args.account.lstrip('@')
        if not account:
            raise ValueError('Account is required')
        fingerprint = hashlib.sha256(json.dumps([info['sha256'], caption, account],
            ensure_ascii=False).encode('utf-8')).hexdigest()
        manifest = {'version': 1, 'account': account, 'video': info, 'caption': caption,
            'target_seconds': args.target_seconds, 'fingerprint': fingerprint}
        write(args.output, manifest)
        print('LOCAL MANIFEST READY: no upload or publication')
        return
    if args.command == 'accounts':
        load_env(args.env_file)
        print(json.dumps([{k: a.get(k) for k in ['_id', 'platform', 'username', 'isActive', 'needsReconnection']}
            for a in api('GET', '/accounts').get('accounts', []) if a.get('platform') == 'threads'], ensure_ascii=False))
        return
    source = Path(args.manifest).resolve()
    manifest = json.loads(source.read_text(encoding='utf-8'))
    state_path = source.with_name(source.stem + '.state.json')
    if args.command == 'publish' and not args.execute:
        check_manifest(manifest)
        print('LOCAL CHECK PASSED: no network request, upload or publication')
        return
    load_env(args.env_file)
    result = publish(manifest, state_path) if args.command == 'publish' else verify(manifest, state_path)
    print(json.dumps({k: result.get(k) for k in ['account', 'post_id', 'status', 'platform_status',
        'url', 'caption_matches', 'media_matches', 'publication_verified', 'public_http_status', 'playback_reviewed']}, ensure_ascii=False))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
