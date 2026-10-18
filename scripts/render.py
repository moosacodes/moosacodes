from __future__ import annotations

import datetime
import io
import json
import os
import urllib.request
from collections import deque
from pathlib import Path
from statistics import median
from typing import Iterable, Sequence
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.getenv("PROFILE_USERNAME", "moosacodes")
API = "https://api.github.com/users/" + USERNAME
HEADERS = {"User-Agent": "readme-avatar-generator", "Accept": "application/vnd.github+json"}
token = os.getenv("GH_PROFILE_TOKEN") or os.getenv("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = "Bearer " + token

PORTRAIT_COLUMNS = 42
PORTRAIT_ROWS = 29
CHARACTER_WIDTH_RATIO = 0.6
PORTRAIT_LINE_HEIGHT = 12.7
PORTRAIT_CENTER_X = 203.5
ASCII_RAMP = " .,:;irsXA253hMHGS#9B&@"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()


def info() -> dict:
    try:
        return json.loads(fetch(API))
    except Exception as exc:
        print("Profile API unavailable; rendering bundled fallback metadata:", exc)
        return {"avatar_url": None, "public_repos": None, "followers": None, "name": "Moosa Alam"}


def lifetime_stats(meta: dict) -> dict:
    """Return all-time public repository stars and public contributions."""
    stats = {
        "repos": meta.get("public_repos"),
        "followers": meta.get("followers"),
        "stars": None,
        "contributions": None,
    }
    try:
        total = 0
        page = 1
        while page <= 20:
            url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner"
            rows = json.loads(fetch(url))
            if not isinstance(rows, list):
                raise ValueError("unexpected repository response")
            total += sum(int(row.get("stargazers_count", 0)) for row in rows if not row.get("fork"))
            if len(rows) < 100:
                break
            page += 1
        stats["stars"] = total
    except Exception as exc:
        print("Could not load total public repo stars:", exc)
    if token:
        try:
            start = int(str(meta.get("created_at", "2024"))[:4])
            end = datetime.datetime.now(datetime.timezone.utc).year
            if end - start > 30:
                raise ValueError("account age unexpectedly large")
            contributions = 0
            for year in range(start, end + 1):
                begin = f"{year}-01-01T00:00:00Z"
                until = f"{year + 1}-01-01T00:00:00Z"
                query = (
                    "query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login)"
                    "{contributionsCollection(from:$from,to:$to){contributionCalendar"
                    "{totalContributions}}}}"
                )
                payload = json.dumps(
                    {"query": query, "variables": {"login": USERNAME, "from": begin, "to": until}}
                ).encode()
                request = urllib.request.Request(
                    "https://api.github.com/graphql",
                    payload,
                    HEADERS | {"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=25) as response:
                    result = json.load(response)
                if result.get("errors"):
                    raise ValueError(str(result["errors"])[:350])
                contributions += result["data"]["user"]["contributionsCollection"]["contributionCalendar"][
                    "totalContributions"
                ]
            stats["contributions"] = contributions
        except Exception as exc:
            print("Lifetime contributions not available (may require token permissions):", exc)
    return stats


def _near_white(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return min(rgb) >= 172 and max(rgb) - min(rgb) <= 48 and (r + g + b) / 3 >= 190


def _background_mask(image: Image.Image) -> list[list[bool]]:
    """Find transparent/white pixels connected to the image border.

    Enclosed white pixels are deliberately retained, which keeps white eyes and
    other light facial details instead of treating every light pixel as a void.
    """
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    candidates = [[pixels[x, y][3] < 32 or _near_white(pixels[x, y][:3]) for x in range(width)] for y in range(height)]
    background = [[False] * width for _ in range(height)]
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        if candidates[0][x]:
            queue.append((x, 0))
        if candidates[height - 1][x]:
            queue.append((x, height - 1))
    for y in range(height):
        if candidates[y][0]:
            queue.append((0, y))
        if candidates[y][width - 1]:
            queue.append((width - 1, y))
    while queue:
        x, y = queue.popleft()
        if background[y][x]:
            continue
        background[y][x] = True
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and candidates[ny][nx] and not background[ny][nx]:
                queue.append((nx, ny))
    return background


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def _content_dimensions(width: int, height: int) -> tuple[int, int, int, int]:
    """Fit an image into the character canvas without changing its aspect ratio."""
    source_aspect = width / height
    logical_aspect = CHARACTER_WIDTH_RATIO
    content_columns = PORTRAIT_COLUMNS
    content_rows = max(1, round(content_columns / source_aspect * logical_aspect))
    if content_rows > PORTRAIT_ROWS:
        content_rows = PORTRAIT_ROWS
        content_columns = max(1, round(content_rows * source_aspect / logical_aspect))
    offset_x = (PORTRAIT_COLUMNS - content_columns) // 2
    offset_y = (PORTRAIT_ROWS - content_rows) // 2
    return content_columns, content_rows, offset_x, offset_y


def _cell_rows(image: Image.Image) -> list[list[tuple[str, str]]]:
    rgba = image.convert("RGBA")
    mask = _background_mask(rgba)
    width, height = rgba.size
    content_columns, content_rows, offset_x, offset_y = _content_dimensions(width, height)
    resized = rgba.resize((content_columns, content_rows), Image.Resampling.LANCZOS)
    mask_image = Image.new("L", (width, height))
    mask_image.putdata([0 if mask[y][x] else 255 for y in range(height) for x in range(width)])
    small_mask = mask_image.resize((content_columns, content_rows), Image.Resampling.BILINEAR)
    pixels = resized.load()
    luminances: list[float] = []
    for y in range(content_rows):
        for x in range(content_columns):
            if small_mask.getpixel((x, y)) > 80 and pixels[x, y][3] > 24:
                r, g, b = pixels[x, y][:3]
                luminances.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
    low = _percentile(luminances, 0.04)
    high = _percentile(luminances, 0.96)
    span = max(high - low, 1.0)
    result = [[(" ", "#000000") for _ in range(PORTRAIT_COLUMNS)] for _ in range(PORTRAIT_ROWS)]
    for y in range(content_rows):
        for x in range(content_columns):
            r, g, b, alpha = pixels[x, y]
            visible = alpha > 24 and small_mask.getpixel((x, y)) > 52
            if not visible:
                continue
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            density = max(0.0, min(1.0, (high - luminance) / span))
            neighbors = []
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < content_columns and 0 <= ny < content_rows:
                    nr, ng, nb = pixels[nx, ny][:3]
                    neighbors.append(0.2126 * nr + 0.7152 * ng + 0.0722 * nb)
            edge = min(1.0, abs(luminance - median(neighbors)) / 90) if neighbors else 0
            index = min(len(ASCII_RAMP) - 1, max(1, round((density * 0.78 + edge * 0.22) * (len(ASCII_RAMP) - 1))))
            result[offset_y + y][offset_x + x] = (ASCII_RAMP[index], f"#{r:02x}{g:02x}{b:02x}")
    return result


def _fallback_art() -> list[list[tuple[str, str]]]:
    return [[(" ", "#000000") for _ in range(PORTRAIT_COLUMNS)] for _ in range(PORTRAIT_ROWS)]


def portrait(meta: dict) -> list[list[tuple[str, str]]]:
    avatar = meta.get("avatar_url")
    if not avatar:
        return _fallback_art()
    try:
        cache_key = meta.get("updated_at") or meta.get("avatar_url")
        separator = "&" if "?" in avatar else "?"
        raw = fetch(f"{avatar}{separator}profile_updated={cache_key}")
        image = Image.open(io.BytesIO(raw))
        return _cell_rows(ImageOps.exif_transpose(image))
    except Exception as exc:
        print("Avatar download unavailable; retaining previous portrait:", exc)
        fallback = ROOT / "assets" / "portrait.txt"
        if fallback.exists():
            return [[(char, "#d6dee8") for char in line[:PORTRAIT_COLUMNS].ljust(PORTRAIT_COLUMNS)] for line in fallback.read_text().splitlines()]
        return _fallback_art()


def _svg_portrait(rows: Iterable[list[tuple[str, str]]]) -> list[str]:
    output = []
    for index, row in enumerate(rows):
        runs: list[tuple[str, str]] = []
        for char, color in row:
            if runs and runs[-1][1] == color:
                runs[-1] = (runs[-1][0] + char, color)
            else:
                runs.append((char, color))
        tspans = "".join(
            f'<tspan fill="{color}">{escape(text)}</tspan>' for text, color in runs if text
        )
        output.append(
            f'<text x="{PORTRAIT_CENTER_X}" text-anchor="middle" y="{116 + index * PORTRAIT_LINE_HEIGHT:.1f}" class="portrait arrive" '
            f'style="animation-delay:{index * .025:.3f}s">{tspans}</text>'
        )
    return output


def svg(mode: str, art: list[list[tuple[str, str]]], meta: dict, stats: dict) -> str:
    dark = mode == "dark"
    bg = "#0d1117" if dark else "#f6f8fa"
    fg = "#d6dee8" if dark else "#24292f"
    muted = "#778399" if dark else "#64748b"
    accent = "#7ee787" if dark else "#1a7f37"
    value = "#a5d6ff" if dark else "#0550ae"
    line = "#30363d" if dark else "#d8dee4"
    repos, followers = stats.get("repos"), stats.get("followers")
    stars, contributions = stats.get("stars"), stats.get("contributions")
    fields = [
        ("OS", "Linux / Windows"), ("Host", "University of Guelph"),
        ("Kernel", "Computer Science + Co-op"), ("Focus", "Software / Cloud / Security"),
        ("Languages", "Python, C, Java, TypeScript"), ("Infrastructure", "AWS, Docker, Terraform, Linux"),
        ("Observability", "Prometheus, Grafana, ELK"), ("Editor", "VS Code / Terminal"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="565" viewBox="0 0 980 565" '
        'role="img" aria-label="Moosa Alam developer profile with animated color ASCII rendering of current GitHub avatar">',
        f'<rect width="980" height="565" rx="12" fill="{bg}"/>',
        f'<rect x="1" y="1" width="978" height="563" rx="11" fill="none" stroke="{line}"/>',
        '<style>text{font-family:Consolas,\'DejaVu Sans Mono\',monospace} .mono{font-size:15px} .tiny{font-size:12px} '
        '.portrait{font-size:12px;white-space:pre;letter-spacing:0} .cursor{animation:blink 1.2s steps(1,end) infinite} '
        '.arrive{animation:up .8s ease both} @keyframes blink{50%{opacity:0}} '
        '@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}} '
        '@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>',
        '<circle cx="35" cy="28" r="5" fill="#ff5f57"/><circle cx="53" cy="28" r="5" fill="#febc2e"/><circle cx="71" cy="28" r="5" fill="#28c840"/>',
        f'<text x="95" y="32" fill="{muted}" class="tiny">moosa@github — profile</text>',
        f'<line x1="0" y1="49" x2="980" y2="49" stroke="{line}"/>',
        f'<text x="32" y="83" fill="{accent}" class="tiny">$ avatar --source github --mode color-ascii</text>',
        f'<rect x="26" y="100" width="355" height="403" rx="7" fill="{line}" opacity=".12"/>',
        f'<text x="32" y="522" fill="{muted}" class="tiny">avatar: github.com/{escape(USERNAME)} · auto-synced daily</text>',
        f'<text x="418" y="102" fill="{accent}" font-size="20" font-weight="bold">moosa@{escape(USERNAME)}</text>',
        f'<line x1="418" y1="115" x2="943" y2="115" stroke="{line}"/>',
    ]
    out.extend(_svg_portrait(art))
    y = 151
    for label, value_text in fields:
        out.append(f'<text x="418" y="{y}" class="mono"><tspan fill="{accent}">{escape(label)}</tspan><tspan fill="{muted}">  : </tspan><tspan fill="{value}">{escape(value_text)}</tspan></text>')
        y += 32
    out.extend([
        f'<line x1="418" y1="414" x2="943" y2="414" stroke="{line}"/>',
        f'<text x="418" y="442" fill="{fg}" class="mono">GitHub <tspan fill="{muted}">/</tspan> {escape(USERNAME)}</text>',
        f'<text x="418" y="465" fill="{muted}" class="mono">Repos <tspan fill="{value}">{repos if repos is not None else "—"}</tspan>    Stars <tspan fill="{value}">{stars if stars is not None else "—"}</tspan>    Followers <tspan fill="{value}">{followers if followers is not None else "—"}</tspan></text>',
        f'<text x="418" y="486" fill="{muted}" class="tiny">All-time GitHub contributions: <tspan fill="{value}">{format(contributions, ",") if contributions is not None else "unavailable"}</tspan></text>',
        f'<text x="418" y="520" fill="{accent}" class="mono">$ building systems that actually ship<tspan class="cursor">_</tspan></text>',
        "</svg>",
    ])
    return "\n".join(out) + "\n"


def main() -> None:
    (ROOT / "assets").mkdir(exist_ok=True)
    meta = info()
    art = portrait(meta)
    stats = lifetime_stats(meta)
    text_art = ["".join(char for char, _ in row) for row in art]
    (ROOT / "assets" / "portrait.txt").write_text("\n".join(text_art) + "\n", encoding="utf-8")
    for theme in ("dark", "light"):
        (ROOT / "assets" / f"{theme}.svg").write_text(svg(theme, art, meta, stats), encoding="utf-8")
    print("Generated both SVGs. avatar:", meta.get("avatar_url"))


if __name__ == "__main__":
    main()
