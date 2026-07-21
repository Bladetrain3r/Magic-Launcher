"""Magic Launcher Server - a read-only web renderer of shortcuts.json.

Serves the shortcut tree as a tappable tile grid so any browser on the
LAN (phone, tablet, old laptop) becomes a Stream Deck for this machine.

The native tkinter launcher stays the source of truth: it owns all
create/edit/delete. This server never writes shortcuts.json - it reads
the config fresh on every request and launches on tap.

Security model: the client sends an IDENTIFIER (a path into the tree,
e.g. "Games/DOSBox"), never a command. The server resolves that id
against the locally-loaded shortcuts.json and runs the entry it finds
there via Launcher.launch(). There is no code path that executes a
string taken from the request.

Usage (same convention as app.py):
    python3 path_to/Magic-Launcher/launcher/server.py
    python3 launcher/server.py --host 0.0.0.0 --port 8180   # expose to LAN

No auth in v1 - network scope (localhost/LAN binding) is the boundary.
"""

import argparse
import json
import html
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, parse_qs, urlparse

from constants import CONFIG_FILE, ICONS_DIR, APP_NAME_PATH, COLORS, VERSION
from models import item_from_dict, BaseItem, Shortcut, Folder
from utils.launcher import Launcher, is_valid_target, clear_validity_cache
from utils.logger import logger

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8180

MAX_BODY_BYTES = 64 * 1024


def get_app_name() -> str:
    """Read the title bar file the native app uses, without touching config.py
    (whose import creates directories - this server stays a pure reader)."""
    try:
        if APP_NAME_PATH.exists():
            return APP_NAME_PATH.read_text().strip() or "Magic Launcher"
    except Exception as e:
        logger.error(f"Error reading app name: {e}")
    return "Magic Launcher"


def load_tree() -> dict:
    """Fresh-read shortcuts.json into the model tree.

    Returns {} on a missing or broken file. Unlike ConfigManager, this
    never falls back to writing defaults - the server does not write.
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.warning(f"No config file at {CONFIG_FILE} - serving empty grid")
        return {}
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading config: {e}")
        return {}
    return {name: item_from_dict(name, item_data) for name, item_data in data.items()}


def decode_id(item_id: str) -> str:
    """Turn an encoded tree-path id back into a readable path for display."""
    return '/'.join(unquote(seg) for seg in item_id.split('/'))


def encode_id(segments) -> str:
    """Encode a list of item names into a URL-safe tree-path id.

    Each segment is fully percent-encoded so names containing '/' can't
    forge extra path levels."""
    return '/'.join(quote(seg, safe='') for seg in segments)


def resolve(tree: dict, item_id: str):
    """Walk the trusted tree to the item named by an encoded id.

    Returns the BaseItem, or None if any segment doesn't resolve."""
    if not item_id:
        return None
    item = None
    items = tree
    for seg in item_id.split('/'):
        if not isinstance(items, dict):
            return None
        item = items.get(unquote(seg))
        if item is None:
            return None
        items = item.items if isinstance(item, Folder) else None
    return item


# --- Launch tracking (the per-tile status dots) ---

class LaunchTracker:
    """Remembers each tile's latest launch so /status can report it.

    Status per tile: 'running' while the process is alive, then 'ok'
    (exit 0) or 'fail' (nonzero exit, or the launch never spawned).
    Transitions are also appended to an in-memory event log, capped so
    the server can't grow without bound.
    """

    def __init__(self, history: int = 200):
        self._lock = threading.Lock()
        self._latest = {}  # canonical item id -> launch record
        self.events = deque(maxlen=history)  # (timestamp, id, status)

    def start(self, item_id: str, proc) -> str:
        status = 'running' if proc is not None else 'fail'
        with self._lock:
            self._latest[item_id] = {'proc': proc, 'status': status}
            self.events.append((time.time(), item_id, status))
        return status

    def statuses(self) -> dict:
        """Current status per tile, polling any still-running processes."""
        with self._lock:
            for item_id, rec in self._latest.items():
                if rec['status'] != 'running':
                    continue
                code = rec['proc'].poll()
                if code is not None:
                    rec['status'] = 'ok' if code == 0 else 'fail'
                    self.events.append((time.time(), item_id, rec['status']))
            return {item_id: rec['status']
                    for item_id, rec in self._latest.items()}

    def log(self) -> list:
        """Chronological copy of the event log (oldest first)."""
        self.statuses()  # settle any just-finished processes first
        with self._lock:
            return list(self.events)


tracker = LaunchTracker()


# --- HTML rendering (the bbs_page.py move: config in, page out) ---

PAGE_STYLE = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: {COLORS['black']};
    color: {COLORS['white']};
    font-family: 'Courier New', Courier, monospace;
    touch-action: manipulation;
}}
header {{
    background: {COLORS['dark_gray']};
    border-bottom: 3px solid {COLORS['light_gray']};
    padding: 8px 12px;
    display: flex;
    align-items: baseline;
    gap: 12px;
    flex-wrap: wrap;
}}
header h1 {{ font-size: 1.1em; color: {COLORS['yellow']}; }}
nav {{ font-size: 0.95em; }}
nav a {{ color: {COLORS['light_cyan']}; text-decoration: none; }}
nav a:hover {{ text-decoration: underline; }}
nav span {{ color: {COLORS['light_gray']}; }}
main {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(112px, 1fr));
    gap: 10px;
    padding: 14px;
}}
.tile {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    background: none;
    border: none;
    padding: 6px 2px;
    cursor: pointer;
    text-decoration: none;
    color: {COLORS['white']};
    font-family: inherit;
    font-size: 0.85em;
    width: 100%;
}}
.tile .box {{
    width: 84px;
    height: 84px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px outset {COLORS['light_gray']};
    font-size: 2em;
    font-weight: bold;
    color: {COLORS['black']};
    position: relative;
}}
.tile:active .box {{ border-style: inset; }}
.tile .box img {{ width: 64px; height: 64px; image-rendering: pixelated; }}
.shortcut .box {{ background: {COLORS['light_gray']}; }}
.folder .box {{ background: {COLORS['yellow']}; }}
.tile .name {{
    max-width: 108px;
    overflow-wrap: break-word;
    text-align: center;
}}
.broken .box::after {{
    content: '\\2715';
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4em;
    color: {COLORS['light_red']};
}}
.tile.ok .box {{ outline: 3px solid {COLORS['light_green']}; }}
.tile.fail .box {{ outline: 3px solid {COLORS['light_red']}; }}
.badge {{
    position: absolute;
    top: 4px;
    left: 4px;
    width: 14px;
    height: 14px;
    border: 2px solid {COLORS['black']};
    display: none;
}}
.badge.st-running {{ display: block; background: {COLORS['yellow']}; }}
.badge.st-ok {{ display: block; background: {COLORS['light_green']}; }}
.badge.st-fail {{ display: block; background: {COLORS['light_red']}; }}
.empty {{ color: {COLORS['light_gray']}; padding: 20px; grid-column: 1 / -1; }}
header .loglink {{ margin-left: auto; }}
table.log {{
    border-collapse: collapse;
    margin: 14px;
    width: calc(100% - 28px);
    font-size: 0.9em;
}}
.log th, .log td {{
    border: 1px solid {COLORS['dark_gray']};
    padding: 5px 10px;
    text-align: left;
}}
.log th {{ background: {COLORS['dark_gray']}; color: {COLORS['yellow']}; }}
.log td {{ color: {COLORS['light_gray']}; }}
.log td.st-running {{ color: {COLORS['yellow']}; }}
.log td.st-ok {{ color: {COLORS['light_green']}; }}
.log td.st-fail {{ color: {COLORS['light_red']}; }}
footer {{
    color: {COLORS['dark_gray']};
    font-size: 0.8em;
    padding: 8px 14px;
}}
"""

# Tap a shortcut tile -> POST its id, flash the tile green/red.
# Corner badges show each tile's latest launch state (yellow running,
# green exited 0, red failed) and refresh from /status every 2s.
# Without JS the plain form submit still works (server 303s back) and
# badges are rendered server-side on each page load.
PAGE_SCRIPT = """
document.querySelectorAll('form.launch').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var tile = form.querySelector('.tile');
        fetch('/launch', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded',
                      'Accept': 'application/json'},
            body: 'id=' + encodeURIComponent(form.elements.id.value)
        }).then(function (r) { return r.json(); })
          .then(function (data) {
              flash(tile, data.ok);
              setBadge(tile, data.status);
          })
          .catch(function () { flash(tile, false); });
    });
});
function flash(tile, ok) {
    tile.classList.add(ok ? 'ok' : 'fail');
    setTimeout(function () { tile.classList.remove('ok', 'fail'); }, 500);
}
function setBadge(tile, status) {
    var badge = tile.querySelector('.badge');
    if (badge) badge.className = 'badge' + (status ? ' st-' + status : '');
}
function pollStatus() {
    if (document.hidden) return;
    fetch('/status', {headers: {'Accept': 'application/json'}})
        .then(function (r) { return r.json(); })
        .then(function (statuses) {
            document.querySelectorAll('.tile.shortcut').forEach(function (tile) {
                setBadge(tile, statuses[tile.dataset.id]);
            });
        })
        .catch(function () {});
}
setInterval(pollStatus, 2000);
"""


def render_icon(item: BaseItem) -> str:
    """The icon box for a tile - BMP image if the native app has one,
    else the same text-icon rule as widgets.py."""
    icon = item.icon or ''
    if icon.endswith('.bmp') and (ICONS_DIR / Path(icon).name).is_file():
        return f'<img src="/icon/{quote(Path(icon).name)}" alt="">'
    text = icon[:2] if 0 < len(icon) <= 2 else item.name[:1].upper()
    return html.escape(text)


def render_tile(item: BaseItem, segments, statuses: dict) -> str:
    item_id = encode_id(segments)
    name = html.escape(item.name)
    if isinstance(item, Folder):
        return (f'<a class="tile folder" href="/folder/{item_id}">'
                f'<span class="box">{render_icon(item)}</span>'
                f'<span class="name">{name}</span></a>')
    broken = '' if is_valid_target(item.path) else ' broken'
    status = statuses.get(item_id)
    badge_class = f'badge st-{status}' if status else 'badge'
    return (f'<form class="launch" method="POST" action="/launch">'
            f'<input type="hidden" name="id" value="{html.escape(item_id)}">'
            f'<button class="tile shortcut{broken}" type="submit" '
            f'data-id="{html.escape(item_id)}">'
            f'<span class="box">{render_icon(item)}'
            f'<span class="{badge_class}"></span></span>'
            f'<span class="name">{name}</span></button></form>')


def render_page(segments, items: dict, statuses: dict) -> str:
    """Render one folder level (segments == [] for the top level)."""
    crumbs = ['<a href="/">HOME</a>']
    for i, seg in enumerate(segments):
        crumbs.append(f'<a href="/folder/{encode_id(segments[:i + 1])}">'
                      f'{html.escape(seg)}</a>')
    breadcrumb = ' <span>&gt;</span> '.join(crumbs)

    tiles = [render_tile(item, segments + [name], statuses)
             for name, item in items.items()]
    grid = '\n'.join(tiles) if tiles else '<p class="empty">No shortcuts here.</p>'

    title = html.escape(get_app_name())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<header><h1>{title}</h1><nav>{breadcrumb}</nav><nav class="loglink"><a href="/log">LOG</a></nav></header>
<main>
{grid}
</main>
<footer>Magic Launcher Server v{VERSION} - read-only view, edit in the native app</footer>
<script>{PAGE_SCRIPT}</script>
</body>
</html>"""


def render_log_page(events) -> str:
    """Render the launch event log, newest first, auto-refreshing."""
    rows = []
    for ts, item_id, status in reversed(events):
        stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
        rows.append(f'<tr><td>{stamp}</td>'
                    f'<td>{html.escape(decode_id(item_id))}</td>'
                    f'<td class="st-{status}">{status.upper()}</td></tr>')
    if rows:
        table = ('<table class="log"><tr><th>Time</th><th>Shortcut</th>'
                 '<th>Status</th></tr>' + '\n'.join(rows) + '</table>')
    else:
        table = '<p class="empty">No launches yet.</p>'

    title = html.escape(get_app_name())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="5">
<title>{title} - Log</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<header><h1>{title}</h1><nav><a href="/">HOME</a> <span>&gt;</span> LOG</nav></header>
{table}
<footer>Magic Launcher Server v{VERSION} - last {len(events)} launch events, in memory only</footer>
</body>
</html>"""


class StreamDeckHandler(BaseHTTPRequestHandler):
    server_version = f"MagicLauncherServer/{VERSION}"

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

    def _send(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, code: int, text: str):
        self._send(code, 'text/html; charset=utf-8', text.encode('utf-8'))

    def _send_page(self, segments, items):
        # Re-check target validity per page load so the red-X state
        # tracks the filesystem, not the first request's cache.
        clear_validity_cache()
        self._send_html(200, render_page(segments, items, tracker.statuses()))

    def _not_found(self):
        self._send_html(404, '<h1>404</h1><p>Not found.</p>')

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/':
            self._send_page([], load_tree())
        elif path == '/status':
            payload = json.dumps(tracker.statuses()).encode('utf-8')
            self._send(200, 'application/json', payload)
        elif path == '/log':
            events = tracker.log()
            if 'application/json' in (self.headers.get('Accept') or ''):
                payload = json.dumps([
                    {'time': ts,
                     'iso': time.strftime('%Y-%m-%dT%H:%M:%S',
                                          time.localtime(ts)),
                     'id': item_id,
                     'shortcut': decode_id(item_id),
                     'status': status}
                    for ts, item_id, status in events]).encode('utf-8')
                self._send(200, 'application/json', payload)
            else:
                self._send_html(200, render_log_page(events))
        elif path.startswith('/folder/'):
            item_id = path[len('/folder/'):].rstrip('/')
            item = resolve(load_tree(), item_id)
            if isinstance(item, Folder):
                segments = [unquote(seg) for seg in item_id.split('/')]
                self._send_page(segments, item.items)
            else:
                self._not_found()
        elif path.startswith('/icon/'):
            self._serve_icon(path[len('/icon/'):])
        else:
            self._not_found()

    def _serve_icon(self, encoded_name: str):
        """Serve a BMP from the icons dir. Bare .bmp filenames only -
        anything with a path separator (or that isn't its own basename)
        is refused, so the request can't reach outside ICONS_DIR."""
        name = unquote(encoded_name)
        if ('/' in name or '\\' in name or name != Path(name).name
                or not name.endswith('.bmp')):
            self._not_found()
            return
        icon_path = ICONS_DIR / name
        if not icon_path.is_file():
            self._not_found()
            return
        self._send(200, 'image/bmp', icon_path.read_bytes())

    def do_POST(self):
        if urlparse(self.path).path != '/launch':
            self._not_found()
            return

        length = int(self.headers.get('Content-Length') or 0)
        if length > MAX_BODY_BYTES:
            self._send_html(413, '<h1>413</h1><p>Body too large.</p>')
            return
        body = self.rfile.read(length).decode('utf-8', errors='replace')
        item_id = parse_qs(body).get('id', [''])[0]

        # THE rule: resolve the id against the trusted config. Only an
        # entry that exists there as a Shortcut ever reaches launch().
        item = resolve(load_tree(), item_id)
        if not isinstance(item, Shortcut):
            logger.warning(f"Refused launch for unresolved id: {item_id!r}")
            self._respond_launch(False, refused=True)
            return

        # Canonical id (client encoding may differ) so the tracker key
        # always matches the data-id the tiles are rendered with.
        canonical_id = encode_id(unquote(seg) for seg in item_id.split('/'))
        proc = Launcher.launch_process(item.path, item.args)
        status = tracker.start(canonical_id, proc)
        self._respond_launch(proc is not None, status=status)

    def _respond_launch(self, ok: bool, refused: bool = False,
                        status: str = 'fail'):
        if 'application/json' in (self.headers.get('Accept') or ''):
            code = 404 if refused else 200
            payload = json.dumps({'ok': ok, 'status': status}).encode('utf-8')
            self._send(code, 'application/json', payload)
        else:
            # No-JS form fallback: bounce back to the page the tap came from
            self.send_response(303)
            self.send_header('Location', self.headers.get('Referer') or '/')
            self.send_header('Content-Length', '0')
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(
        description="Serve Magic Launcher's shortcuts as a tappable web grid.")
    parser.add_argument('--host', default=DEFAULT_HOST,
                        help=f"bind address (default {DEFAULT_HOST}; "
                             "use 0.0.0.0 to allow other devices on your LAN)")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help=f"port to listen on (default {DEFAULT_PORT})")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), StreamDeckHandler)
    print(f"Magic Launcher Server v{VERSION}")
    print(f"Serving {CONFIG_FILE}")
    print(f"Listening on http://{args.host}:{args.port}/")
    if args.host != '127.0.0.1':
        print("Reachable from other devices on your network - "
              "anything that can open this page can launch your shortcuts.")
    logger.info(f"Server started on {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
