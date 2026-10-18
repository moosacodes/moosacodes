from __future__ import annotations
import io, json, os, re, urllib.request, datetime
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.getenv('PROFILE_USERNAME', 'moosacodes')
API = 'https://api.github.com/users/' + USERNAME
HEADERS = {'User-Agent':'readme-avatar-generator','Accept':'application/vnd.github+json'}
token = os.getenv('GH_PROFILE_TOKEN') or os.getenv('GITHUB_TOKEN')
if token: HEADERS['Authorization']='Bearer ' + token

def fetch(url):
    req=urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as res: return res.read()

def info():
    try: return json.loads(fetch(API))
    except Exception as exc:
        print('Profile API unavailable; rendering bundled fallback metadata:',exc)
        return {'avatar_url':None,'public_repos':None,'followers':None,'name':'Moosa Alam'}

def lifetime_stats(meta):
    """All-time public repository stars and public GitHub contributions.

    GitHub's contribution graph is only complete for counts GitHub exposes
    to this token; unavailable totals are omitted rather than invented.
    """
    count = meta.get('public_repos')
    stats = {'repos': count, 'followers': meta.get('followers'), 'stars': None, 'contributions': None}
    try:
        total = 0
        page = 1
        while page <= 20:
            url = f'https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner'
            rows = json.loads(fetch(url))
            if not isinstance(rows, list): raise ValueError('unexpected repository response')
            total += sum(int(r.get('stargazers_count', 0)) for r in rows if not r.get('fork'))
            if len(rows) < 100: break
            page += 1
        stats['stars'] = total
    except Exception as exc:
        print('Could not load total public repo stars:', exc)
    if token:
        try:
            start = int(str(meta.get('created_at', '2024'))[:4])
            end = datetime.datetime.now(datetime.timezone.utc).year
            if end - start > 30: raise ValueError('Account age unexpectedly large')
            contributions = 0
            for year in range(start, end + 1):
                begin = f'{year}-01-01T00:00:00Z'
                until = f'{year + 1}-01-01T00:00:00Z'
                query = 'query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions}}}}' .strip()
                payload = json.dumps({'query':query,'variables':{'login':USERNAME,'from':begin,'to':until}}).encode()
                req = urllib.request.Request('https://api.github.com/graphql', payload, HEADERS | {'Content-Type':'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=25) as response:
                    result=json.load(response)
                if result.get('errors'): raise ValueError(str(result['errors'])[:350])
                contributions += result['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
            stats['contributions'] = contributions
        except Exception as exc:
            print('Lifetime contributions not available (may require token permissions):', exc)
    return stats

def portrait(meta):
    avatar=meta.get('avatar_url')
    if not avatar: return [' ' * 35 for _ in range(24)]
    try:
        raw=fetch(avatar)
        im=Image.open(io.BytesIO(raw)).convert('RGB')
        # A slightly taller crop keeps faces recognizable in monospace art.
        im=ImageOps.fit(im,(240,240),method=Image.Resampling.LANCZOS)
        im=ImageEnhance.Contrast(im).enhance(1.36)
        im=ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=2)
        im=im.resize((35,24),Image.Resampling.LANCZOS)
        chars='@%#*+=-:. '
        result=[]
        for y in range(im.height):
            line=''.join(chars[min(len(chars)-1,int(im.getpixel((x,y))*len(chars)/256))] for x in range(im.width))
            result.append(line)
        return result
    except Exception as exc:
        print('Avatar download unavailable; retaining previous portrait:',exc)
        f=ROOT/'assets'/'portrait.txt'
        return f.read_text().splitlines() if f.exists() else [' ' * 35 for _ in range(24)]

def svg(mode, art, meta, stats):
    dark=mode=='dark'
    bg='#0d1117' if dark else '#f6f8fa'
    fg='#d6dee8' if dark else '#24292f'
    muted='#778399' if dark else '#64748b'
    accent='#7ee787' if dark else '#1a7f37'
    value='#a5d6ff' if dark else '#0550ae'
    line='#30363d' if dark else '#d8dee4'
    repos=stats.get('repos')
    followers=stats.get('followers')
    stars=stats.get('stars')
    contributions=stats.get('contributions')
    fields=[('OS','Linux / Windows'),('Host','University of Guelph'),('Kernel','Computer Science + Co-op'),('Focus','Software / Cloud / Security'),('Languages','Python, C, Java, TypeScript'),('Infrastructure','AWS, Docker, Terraform, Linux'),('Observability','Prometheus, Grafana, ELK'),('Editor','VS Code / Terminal')]
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="980" height="565" viewBox="0 0 980 565" role="img" aria-label="Moosa Alam developer profile with animated ASCII rendering of current GitHub avatar">',
         f'<rect width="980" height="565" rx="12" fill="{bg}"/>',
         f'<rect x="1" y="1" width="978" height="563" rx="11" fill="none" stroke="{line}"/>',
         '<style>text{font-family:Consolas,\'DejaVu Sans Mono\',monospace} .mono{font-size:15px} .tiny{font-size:12px} .portrait{font-size:16px;white-space:pre;letter-spacing:0} .cursor{animation:blink 1.2s steps(1,end) infinite} .arrive{animation:up .8s ease both} .glow{animation:pulse 5s ease-in-out infinite} @keyframes blink{50%{opacity:0}} @keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}} @keyframes pulse{50%{opacity:.35}} @media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>',
         f'<circle cx="35" cy="28" r="5" fill="#ff5f57"/><circle cx="53" cy="28" r="5" fill="#febc2e"/><circle cx="71" cy="28" r="5" fill="#28c840"/>',
         f'<text x="95" y="32" fill="{muted}" class="tiny">moosa@github — profile</text>',
         f'<line x1="0" y1="49" x2="980" y2="49" stroke="{line}"/>',
         f'<text x="32" y="83" fill="{accent}" class="tiny">$ avatar --source github --mode ascii</text>',
         f'<rect x="26" y="100" width="355" height="403" rx="7" fill="{line}" opacity=".12"/>',
         f'<text x="32" y="522" fill="{muted}" class="tiny">avatar: github.com/{escape(USERNAME)} · auto-synced daily</text>',
         f'<text x="418" y="102" fill="{accent}" font-size="20" font-weight="bold">moosa@{escape(USERNAME)}</text>',
         f'<line x1="418" y1="115" x2="943" y2="115" stroke="{line}"/>']
    # Each line fades in gently, top-to-bottom, creating terminal scan-style emergence.
    for i,row in enumerate(art[:24]):
        out.append(f'<text x="42" y="{128+i*15.1:.1f}" fill="{fg}" class="portrait arrive" style="animation-delay:{i*.035:.3f}s">{escape(row)}</text>')
    y=151
    for label,v in fields:
        out.append(f'<text x="418" y="{y}" class="mono"><tspan fill="{accent}">{escape(label)}</tspan><tspan fill="{muted}">  : </tspan><tspan fill="{value}">{escape(v)}</tspan></text>')
        y+=32
    out.extend([f'<line x1="418" y1="414" x2="943" y2="414" stroke="{line}"/>',
                f'<text x="418" y="442" fill="{fg}" class="mono">GitHub <tspan fill="{muted}">/</tspan> {escape(USERNAME)}</text>',
                f'<text x="418" y="465" fill="{muted}" class="mono">Repos <tspan fill="{value}">{repos if repos is not None else "—"}</tspan>    Stars <tspan fill="{value}">{stars if stars is not None else "—"}</tspan>    Followers <tspan fill="{value}">{followers if followers is not None else "—"}</tspan></text>',
                f'<text x="418" y="486" fill="{muted}" class="tiny">All-time GitHub contributions: <tspan fill="{value}">{format(contributions, ",") if contributions is not None else "unavailable"}</tspan></text>', 
                f'<text x="418" y="520" fill="{accent}" class="mono">$ building systems that actually ship<tspan class="cursor">_</tspan></text>',
                '</svg>'])
    return '\n'.join(out)+'\n'

def main():
    (ROOT/'assets').mkdir(exist_ok=True)
    meta=info()
    art=portrait(meta)
    stats=lifetime_stats(meta)
    (ROOT/'assets'/'portrait.txt').write_text('\n'.join(art)+'\n', encoding='utf-8')
    for theme in ('dark','light'):
        (ROOT/'assets'/f'{theme}.svg').write_text(svg(theme,art,meta,stats),encoding='utf-8')
    print('Generated both SVGs. avatar:',meta.get('avatar_url'))

if __name__=='__main__': main()
