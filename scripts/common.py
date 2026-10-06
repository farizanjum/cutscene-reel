"""Shared helpers: API keys, project file, HTTP."""
import json, os, sys, urllib.request, urllib.error


def key(name):
    """Read an API key from the environment, or from a .env file in the working directory."""
    if os.environ.get(name):
        return os.environ[name]
    if os.path.exists('.env'):
        for line in open('.env', encoding='utf-8'):
            if line.strip().startswith(name + '='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit(f'Missing {name}. Set it as an environment variable or put {name}=... in a .env file here.')


def project(path=None):
    path = path or (sys.argv[1] if len(sys.argv) > 1 else 'project.json')
    P = json.load(open(path, encoding='utf-8'))
    P.setdefault('dir', 'runs/' + P['name'])
    os.makedirs(P['dir'] + '/out', exist_ok=True)
    return P


def post_json(url, body, headers, timeout=900):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={**headers, 'Content-Type': 'application/json'})
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout)), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code} {e.read().decode(errors="replace")[:400]}'
