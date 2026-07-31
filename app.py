##############################################
#  DIGITAL E-VOTING SYSTEM (DEPLOY-READY VERSION)
#  Realistic Multi-Page UI • Party Symbols (SVG) • Admin Dashboard
#  Timestamped Blockchain • Web-based Fingerprint Step
#
#  NOTE: This is an academic / demo project. It is NOT affiliated with,
#  endorsed by, or built using any material from the Election Commission
#  of India. Party symbols below are simplified original SVG illustrations
#  drawn for this demo, not copies of any official artwork or trademark.
##############################################

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import time
import hashlib
import os
import json

PORT = int(os.environ.get("PORT", 8080))

# ---------------- FINGERPRINT MODULE ----------------
# NOTE: the original version used input() to "scan" a fingerprint, which only
# works in a local terminal. On a real web server there's no terminal attached
# to a browser request, so it would hang forever. This version asks for the
# simulated fingerprint ID through a web form field instead.
FINGERPRINT_TEMPLATES = {
    "VOTER1001": "fp1", "VOTER1002": "fp2", "VOTER1003": "fp3", "VOTER1004": "fp4",
    "VOTER1005": "fp5", "VOTER1006": "fp6", "VOTER1007": "fp7", "VOTER1008": "fp8"
}

def verify_fingerprint(user_id, scanned_value):
    return FINGERPRINT_TEMPLATES.get(user_id) == scanned_value

##############################################
# USERS DATABASE
##############################################
users = {
    "VOTER1001": "ARYAN YADAV", "VOTER1002": "AVANISH YADAV", "VOTER1003": "CHARLIE",
    "VOTER1004": "SNEHA KUMARI", "VOTER1005": "RAHUL SHARMA",
    "VOTER1006": "PRIYA GUPTA", "VOTER1007": "VIKRAM SINGH", "VOTER1008": "ANITA RAI"
}

qr_tokens = {}
voted = {}
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def generate_token(voter_id):
    token = hashlib.sha256(f"{voter_id}{time.time()}".encode()).hexdigest()[:16]
    qr_tokens[voter_id] = token
    return token

def register_voter(full_name):
    """Registers a new voter: assigns the next VOTERxxxx ID and a matching
    simulated fingerprint ID (fpN), and adds them to the in-memory database."""
    existing_nums = []
    for vid in users:
        digits = "".join(ch for ch in vid if ch.isdigit())
        if digits:
            existing_nums.append(int(digits))
    next_num = max(existing_nums) + 1 if existing_nums else 1001
    voter_id = f"VOTER{next_num}"

    existing_fps = []
    for fp in FINGERPRINT_TEMPLATES.values():
        digits = "".join(ch for ch in fp if ch.isdigit())
        if digits:
            existing_fps.append(int(digits))
    next_fp_num = max(existing_fps) + 1 if existing_fps else 1
    fingerprint_id = f"fp{next_fp_num}"

    users[voter_id] = full_name.strip().upper()
    FINGERPRINT_TEMPLATES[voter_id] = fingerprint_id
    return voter_id, fingerprint_id

##############################################
# PARTY SYMBOLS — simple original SVG illustrations (not official artwork)
##############################################
def _icon_lotus(c):
    return f'''<svg viewBox="0 0 100 100"><g fill="{c}">
    <ellipse cx="50" cy="34" rx="12" ry="22"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(45 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(90 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(135 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(180 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(225 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(270 50 50)"/>
    <ellipse cx="50" cy="34" rx="12" ry="22" transform="rotate(315 50 50)"/>
    <circle cx="50" cy="50" r="9" fill="#fff5e0"/>
    </g></svg>'''

def _icon_cycle(c):
    return f'''<svg viewBox="0 0 100 100"><g fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round">
    <circle cx="27" cy="70" r="17"/>
    <circle cx="73" cy="70" r="17"/>
    <path d="M27 70 L47 35 L73 70 M47 35 L38 70 M47 35 L60 35 M60 35 L73 70"/>
    <path d="M60 35 L66 24 L74 24" stroke-width="4"/>
    </g></svg>'''

def _icon_hand(c):
    return f'''<svg viewBox="0 0 100 100"><g fill="{c}">
    <rect x="34" y="45" width="32" height="38" rx="10"/>
    <rect x="27" y="30" width="10" height="30" rx="5"/>
    <rect x="40" y="18" width="10" height="42" rx="5"/>
    <rect x="53" y="20" width="10" height="40" rx="5"/>
    <rect x="65" y="28" width="10" height="32" rx="5"/>
    <rect x="20" y="50" width="12" height="24" rx="6" transform="rotate(-25 26 62)"/>
    </g></svg>'''

def _icon_elephant(c):
    return f'''<svg viewBox="0 0 100 100"><g fill="{c}">
    <ellipse cx="48" cy="52" rx="28" ry="20"/>
    <path d="M72 45 Q86 45 86 58 Q86 68 76 66 Q82 60 76 52 Z"/>
    <path d="M28 55 Q14 55 12 70 Q11 80 20 82 Q17 70 24 62 Q20 62 22 56 Z"/>
    <rect x="30" y="66" width="8" height="18" rx="3"/>
    <rect x="44" y="68" width="8" height="20" rx="3"/>
    <rect x="58" y="68" width="8" height="20" rx="3"/>
    <rect x="70" y="64" width="8" height="18" rx="3"/>
    <circle cx="66" cy="46" r="3" fill="#fff"/>
    </g></svg>'''

def _icon_broom(c):
    return f'''<svg viewBox="0 0 100 100"><g fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round">
    <line x1="66" y1="14" x2="38" y2="58"/>
    <g stroke-width="3.5">
    <line x1="38" y1="58" x2="16" y2="86"/>
    <line x1="42" y1="63" x2="24" y2="90"/>
    <line x1="46" y1="68" x2="32" y2="92"/>
    <line x1="50" y1="72" x2="42" y2="94"/>
    <line x1="53" y1="76" x2="52" y2="95"/>
    </g>
    <path d="M36 55 L52 71" stroke-width="6"/>
    </g></svg>'''

PARTIES = {
    "BJP":      {"full": "Bharatiya Janata Party",    "color": "#FF9933", "icon": _icon_lotus},
    "SP":       {"full": "Samajwadi Party",            "color": "#DC2626", "icon": _icon_cycle},
    "CONGRESS": {"full": "Indian National Congress",   "color": "#16A34A", "icon": _icon_hand},
    "BSP":      {"full": "Bahujan Samaj Party",         "color": "#2563EB", "icon": _icon_elephant},
    "AAP":      {"full": "Aam Aadmi Party",             "color": "#0EA5E9", "icon": _icon_broom},
}

##############################################
# SMART CONTRACT
##############################################
class SmartContract:
    def __init__(self):
        self.parties = list(PARTIES.keys())
        self.vote_count = {p: 0 for p in self.parties}

    def vote(self, voter, choice):
        if voter in voted or choice not in self.parties:
            return False
        self.vote_count[choice] += 1
        voted[voter] = True
        return True

contract = SmartContract()

##############################################
# BLOCKCHAIN
##############################################
class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = hashlib.sha256(f"{self.index}{self.timestamp}{self.data}{self.prev_hash}".encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [Block(0, time.strftime("%d-%m-%Y %H:%M:%S"), "GENESIS BLOCK", "0" * 12)]

    def add_block(self, data):
        last = self.chain[-1]
        self.chain.append(Block(len(self.chain), time.strftime("%d-%m-%Y %H:%M:%S"), data, last.hash))

chain = Blockchain()

def broadcast_vote(data):
    chain.add_block(data)

##############################################
# SHARED CSS / HTML SHELL
##############################################
BASE_CSS = """
<style>
  :root{
    --navy:#0b1f3a; --navy-light:#132c52; --saffron:#FF9933; --green:#138808;
    --cream:#FBF8F2; --card:#ffffff; --ink:#1a1a2e; --muted:#6b7280; --gold:#c89b3c;
    --danger:#c0392b;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; font-family:'Segoe UI',Arial,sans-serif; background:var(--cream); color:var(--ink);
  }
  .tricolor{height:6px; background:linear-gradient(90deg,var(--saffron) 0 33.3%,#fff 33.3% 66.6%,var(--green) 66.6% 100%);}
  header.topbar{
    background:linear-gradient(180deg,var(--navy) 0%,var(--navy-light) 100%);
    color:#fff; padding:16px 28px; display:flex; align-items:center; gap:14px;
  }
  header.topbar .seal{width:44px; height:44px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 3px var(--gold);}
  header.topbar .seal svg{width:28px; height:28px;}
  header.topbar .titles{flex:1;}
  header.topbar h1{margin:0; font-size:19px; letter-spacing:.3px;}
  header.topbar .sub{margin:0; font-size:12px; color:#c9d4e8;}
  header.topbar .tag{font-size:11px; background:rgba(255,255,255,.12); padding:4px 10px; border-radius:20px;}
  main{max-width:760px; margin:0 auto; padding:30px 20px 60px;}
  .card{background:var(--card); border-radius:14px; padding:28px 30px; box-shadow:0 4px 18px rgba(11,31,58,.08); border:1px solid #eee;}
  h2.page-title{margin:0 0 6px; font-size:22px; color:var(--navy);}
  p.page-sub{margin:0 0 22px; color:var(--muted); font-size:14px;}
  label{display:block; font-size:12px; font-weight:600; color:var(--navy); margin:14px 0 6px; letter-spacing:.3px; text-transform:uppercase;}
  input[type=text], input[type=password]{
    width:100%; padding:12px 14px; font-size:15px; border:1.5px solid #dbe0e8; border-radius:9px; outline:none; transition:.15s;
  }
  input:focus{border-color:var(--saffron); box-shadow:0 0 0 3px rgba(255,153,51,.15);}
  .btn{
    display:inline-block; margin-top:20px; padding:13px 26px; font-size:15px; font-weight:600;
    border:none; border-radius:9px; cursor:pointer; text-decoration:none; text-align:center;
  }
  .btn-primary{background:var(--navy); color:#fff; width:100%;}
  .btn-primary:hover{background:var(--navy-light);}
  .btn-outline{background:transparent; color:var(--navy); border:1.5px solid var(--navy);}
  .link-row{text-align:center; margin-top:18px; font-size:13px;}
  .link-row a{color:var(--navy); text-decoration:none; font-weight:600;}
  .footer-note{max-width:760px; margin:0 auto; padding:0 20px 40px; text-align:center; color:#9aa2b1; font-size:11.5px; line-height:1.6;}
  .badge-id{display:inline-block; background:#eef2f7; color:var(--navy); font-family:monospace; padding:3px 10px; border-radius:6px; font-size:13px;}
  .party-grid{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:10px;}
  .party-card{
    background:#fff; border:2px solid #eee; border-radius:14px; padding:18px 16px; text-align:center;
    transition:.15s;
  }
  .party-card .icon-wrap{width:64px; height:64px; border-radius:50%; margin:0 auto 12px; display:flex; align-items:center; justify-content:center;}
  .party-card .icon-wrap svg{width:38px; height:38px;}
  .party-card h4{margin:0 0 2px; font-size:15px; color:var(--navy);}
  .party-card .full-name{font-size:11px; color:var(--muted); margin-bottom:12px; min-height:28px;}
  .vote-btn{width:100%; padding:10px; border:none; border-radius:8px; color:#fff; font-weight:700; cursor:pointer; font-size:13px; letter-spacing:.3px;}
  .strip{display:flex; justify-content:center; gap:10px; margin-top:26px; flex-wrap:wrap;}
  .strip .chip{width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center;}
  .strip .chip svg{width:22px; height:22px;}
  .strip-label{text-align:center; font-size:11px; color:var(--muted); margin-top:10px; text-transform:uppercase; letter-spacing:.5px;}
  .token-box{background:var(--navy); color:#fff; font-family:monospace; font-size:18px; letter-spacing:2px; padding:18px; border-radius:10px; text-align:center; margin:14px 0 6px;}
  .result-row{margin-bottom:16px;}
  .result-row .meta{display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;}
  .result-row .meta b{color:var(--navy);}
  .bar-bg{background:#eef1f5; border-radius:6px; height:14px; overflow:hidden;}
  .bar-fill{height:100%; border-radius:6px;}
  .block-item{border-left:3px solid var(--gold); padding:10px 16px; margin-bottom:10px; background:#fafbfd; border-radius:0 8px 8px 0;}
  .block-item .idx{font-weight:700; color:var(--navy); font-size:13px;}
  .block-item .meta{font-size:11.5px; color:var(--muted); font-family:monospace;}
  .status-icon{width:64px; height:64px; border-radius:50%; margin:0 auto 16px; display:flex; align-items:center; justify-content:center; font-size:32px; color:#fff;}
  .center{text-align:center;}
  .spinner{width:46px; height:46px; border:4px solid #dbe4f2; border-top-color:var(--navy); border-radius:50%; margin:0 auto 18px; animation:spin 0.9s linear infinite;}
  @keyframes spin{to{transform:rotate(360deg);}}
  table.results-table{width:100%; border-collapse:collapse; margin-top:8px;}
  table.results-table th{background:var(--navy); color:#fff; text-align:left; padding:9px 12px; font-size:12px; text-transform:uppercase;}
  table.results-table td{padding:9px 12px; border-bottom:1px solid #eee; font-size:14px;}
  .disclaimer{background:#fff7e6; border:1px solid #f0d58c; color:#7a5c00; font-size:11.5px; padding:10px 14px; border-radius:8px; margin-top:22px;}
  .fp-wrap{width:110px; height:110px; border-radius:50%; background:#eef2f7; margin:0 auto 20px; display:flex; align-items:center; justify-content:center; animation:pulse 1.6s ease-in-out infinite;}
  @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(11,31,58,.12);}50%{box-shadow:0 0 0 14px rgba(11,31,58,0);}}
</style>
"""

SEAL_SVG = """<svg viewBox="0 0 100 100">
<circle cx="50" cy="50" r="46" fill="#ffffff"/>
<circle cx="50" cy="50" r="46" fill="none" stroke="#c89b3c" stroke-width="2"/>
<circle cx="50" cy="50" r="39" fill="none" stroke="#0b1f3a" stroke-opacity="0.12" stroke-width="1" stroke-dasharray="2 4"/>
<path d="M30 52 L45 66 L73 33" fill="none" stroke="#0b1f3a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

def shell(title, body, subtitle="Digital Voting Portal &bull; Demonstration System"):
    return f"""<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} | E-Voting Portal</title>{BASE_CSS}</head>
    <body>
    <div class="tricolor"></div>
    <header class="topbar">
        <div class="seal">{SEAL_SVG}</div>
        <div class="titles">
            <h1>Digital Voting Portal</h1>
            <p class="sub">{subtitle}</p>
        </div>
        <div class="tag">DEMO BUILD</div>
    </header>
    <main>{body}</main>
    <div class="footer-note">
        This is an academic / demonstration project and is <b>not affiliated with, endorsed by, or connected to</b>
        the Election Commission of India or any government body. Party names and symbols above are simplified,
        original illustrations created for this demo, not official artwork.
    </div>
    </body></html>"""

def party_icon_html(code, size=64):
    p = PARTIES[code]
    return f'<div class="icon-wrap" style="background:{p["color"]}22;">{p["icon"](p["color"])}</div>'

##############################################
# MAIN WEB HANDLER
##############################################
class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}

        if path == "/":
            strip = "".join(
                f'<div class="chip" style="background:{p["color"]}22;">{p["icon"](p["color"])}</div>'
                for p in PARTIES.values()
            )
            body = f"""
            <div class="card center">
                <h2 class="page-title">Welcome to the Digital Voting Portal</h2>
                <p class="page-sub">Secure &bull; Transparent &bull; Blockchain-Verified</p>
                <a href="/loading" class="btn btn-primary" style="width:auto; padding:14px 40px;">Proceed to Voting Portal &rarr;</a>
                <div class="strip">{strip}</div>
                <div class="strip-label">Contesting Parties in this Demo Election</div>
                <div class="disclaimer">Demo / educational project &mdash; not a real or official election system.</div>
            </div>
            """
            return self.respond(shell("Welcome", body))

        if path == "/loading":
            return self.respond(f"""<html><head><meta charset="utf-8">
            <meta http-equiv="refresh" content="1.6;URL='/home'" />{BASE_CSS}</head>
            <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
            <div class="center">
                <div class="spinner"></div>
                <p style="color:var(--navy); font-weight:600;">Initializing secure connection&hellip;</p>
                <p style="color:var(--muted); font-size:12px;">Verifying blockchain integrity</p>
            </div>
            </body></html>""")

        if path == "/home":
            body = """
            <div class="card">
                <h2 class="page-title">Voter Login</h2>
                <p class="page-sub">Enter your registered Voter ID to receive a secure access token.</p>
                <form action="/qr" method="get">
                    <label>Voter ID</label>
                    <input type="text" name="id" placeholder="e.g. VOTER1001" required>
                    <button class="btn btn-primary">Generate Access Token &rarr;</button>
                </form>
                <div class="link-row"><a href="/register">New voter? Register here</a></div>
                <div class="link-row"><a href="/admin_login">Election Officer / Admin Login</a></div>
            </div>
            """
            return self.respond(shell("Voter Login", body))

        if path == "/register":
            body = """
            <div class="card">
                <h2 class="page-title">Voter Registration</h2>
                <p class="page-sub">Naye voter yahan register karke apna Voter ID aur Fingerprint ID paa sakte hain.</p>
                <form action="/register_submit" method="get">
                    <label>Full Name</label>
                    <input type="text" name="name" placeholder="e.g. RAVI KUMAR" required>
                    <button class="btn btn-primary">Register &amp; Get Voter ID &rarr;</button>
                </form>
                <div class="link-row"><a href="/home">&larr; Already registered? Login</a></div>
            </div>
            """
            return self.respond(shell("Voter Registration", body))

        if path == "/register_submit":
            name = params.get("name", [""])[0].strip()
            if not name:
                return self.respond(self._error_page("Please enter your full name to register.", "/register"))
            voter_id, fingerprint_id = register_voter(name)
            body = f"""
            <div class="card center">
                <div class="status-icon" style="background:var(--green);">&#10003;</div>
                <h2 class="page-title">Registration Successful</h2>
                <p class="page-sub">Welcome, {users[voter_id]}. Save these details &mdash; you'll need them to vote.</p>
                <label style="text-align:left;">Your Voter ID</label>
                <div class="token-box">{voter_id}</div>
                <label style="text-align:left;">Your Fingerprint ID (for biometric verification)</label>
                <div class="token-box">{fingerprint_id}</div>
                <a href="/qr?id={voter_id}" class="btn btn-primary" style="margin-top:20px;">Proceed to Login &amp; Vote &rarr;</a>
                <div class="link-row"><a href="/home">&larr; Back to Home</a></div>
            </div>
            """
            return self.respond(shell("Registration Successful", body))

        if path == "/admin_login":
            body = """
            <div class="card">
                <h2 class="page-title">Election Officer Login</h2>
                <p class="page-sub">Restricted access &mdash; authorized personnel only.</p>
                <form action="/admin" method="get">
                    <label>Admin Password</label>
                    <input type="password" name="pass" placeholder="Enter password" required>
                    <button class="btn btn-primary">Login to Dashboard</button>
                </form>
                <div class="link-row"><a href="/home">&larr; Back to Voter Login</a></div>
            </div>
            """
            return self.respond(shell("Officer Login", body))

        if path == "/admin":
            pw = params.get("pass", [""])[0]
            if pw != ADMIN_PASSWORD:
                return self.respond(self._error_page("Incorrect admin password.", "/admin_login"))

            total_votes = sum(contract.vote_count.values()) or 1
            leader_code = max(contract.vote_count, key=contract.vote_count.get)
            rows = ""
            for code, cnt in contract.vote_count.items():
                p = PARTIES[code]
                pct = round((cnt / total_votes) * 100, 1) if total_votes else 0
                rows += f"""
                <div class="result-row" id="row-{code}">
                    <div class="meta"><b>{code} &mdash; {p['full']}</b><span><span id="count-{code}">{cnt}</span> votes (<span id="pct-{code}">{pct}</span>%)</span></div>
                    <div class="bar-bg"><div class="bar-fill" id="bar-{code}" style="width:{pct}%; background:{p['color']};"></div></div>
                </div>
                """

            blocks = "".join(
                f"""<div class="block-item">
                    <div class="idx">Block #{b.index}</div>
                    <div class="meta">{b.timestamp} &bull; {b.data}</div>
                    <div class="meta">hash: {b.hash[:24]}&hellip;</div>
                </div>"""
                for b in reversed(chain.chain)
            )

            codes = list(PARTIES.keys())
            colors = [PARTIES[c]["color"] for c in codes]
            counts = [contract.vote_count[c] for c in codes]

            body = f"""
            <div class="card">
                <h2 class="page-title">Election Command Center</h2>
                <p class="page-sub">Live results, updated automatically as votes are cast.</p>
                <div id="leaderBox" style="background:#f0f4fa; border-radius:10px; padding:12px 16px; margin-bottom:18px; font-weight:700; color:var(--navy);">
                    Leading: {leader_code} &mdash; {PARTIES[leader_code]['full']} ({contract.vote_count[leader_code]} votes)
                </div>
                {rows}
            </div>
            <div class="card" style="margin-top:20px;">
                <h2 class="page-title" style="font-size:18px;">Live Vote Chart</h2>
                <p class="page-sub">Refreshes every 2 seconds &mdash; no page reload needed.</p>
                <canvas id="voteChart" height="180"></canvas>
            </div>
            <div class="card" style="margin-top:20px;">
                <h2 class="page-title" style="font-size:18px;">Blockchain Ledger</h2>
                <p class="page-sub">Every vote is recorded as an immutable, timestamped block.</p>
                <div id="ledgerBox">{blocks}</div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
            const partyCodes = {json.dumps(codes)};
            const partyColors = {json.dumps(colors)};
            const partyNames = {json.dumps({c: PARTIES[c]['full'] for c in codes})};
            const ctx = document.getElementById('voteChart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: partyCodes,
                    datasets: [{{ data: {json.dumps(counts)}, backgroundColor: partyColors, borderRadius: 6 }}]
                }},
                options: {{
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }} }}
                }}
            }});
            function refresh() {{
                fetch('/votes_live').then(r => r.json()).then(data => {{
                    let total = data.votes.reduce((a,b) => a+b, 0) || 1;
                    let maxV = Math.max(...data.votes);
                    let leaderIdx = data.votes.indexOf(maxV);
                    let leaderCode = data.labels[leaderIdx];
                    document.getElementById('leaderBox').innerText =
                        'Leading: ' + leaderCode + ' \u2014 ' + partyNames[leaderCode] + ' (' + maxV + ' votes)';
                    data.labels.forEach((code, i) => {{
                        let cnt = data.votes[i];
                        let pct = Math.round((cnt/total)*1000)/10;
                        document.getElementById('count-'+code).innerText = cnt;
                        document.getElementById('pct-'+code).innerText = pct;
                        document.getElementById('bar-'+code).style.width = pct + '%';
                    }});
                    chart.data.datasets[0].data = data.votes;
                    chart.update();
                }});
            }}
            setInterval(refresh, 2000);
            </script>
            """
            return self.respond(shell("Admin Dashboard", body))

        if path == "/votes_live":
            data = {
                "labels": list(contract.vote_count.keys()),
                "votes": list(contract.vote_count.values())
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        if path == "/qr":
            voter = params.get("id", [""])[0].strip().upper()
            if voter not in users:
                return self.respond(self._error_page(f"'{voter}' is not a registered Voter ID.", "/home"))
            token = generate_token(voter)
            body = f"""
            <div class="card center">
                <h2 class="page-title">Access Token Generated</h2>
                <p class="page-sub">Welcome, {users[voter]} &nbsp;<span class="badge-id">{voter}</span></p>
                <div class="token-box">{token}</div>
                <p style="font-size:12px; color:var(--muted);">This one-time token confirms your identity for this session.</p>
                <form action="/vote" method="get" style="text-align:left; margin-top:10px;">
                    <input type="hidden" name="id" value="{voter}">
                    <label>Confirm Token</label>
                    <input type="text" name="tkn" placeholder="Paste the token shown above" required>
                    <button class="btn btn-primary">Continue &rarr;</button>
                </form>
            </div>
            """
            return self.respond(shell("Access Token", body))

        if path == "/vote":
            voter = params.get("id", [""])[0]
            token = params.get("tkn", [""])[0]
            if qr_tokens.get(voter) != token:
                return self.respond(self._error_page("Invalid or expired access token.", "/home"))
            body = f"""
            <div class="card center">
                <div class="fp-wrap">
                    <svg viewBox="0 0 100 100" width="52" height="52">
                        <g fill="none" stroke="#0b1f3a" stroke-width="4" stroke-linecap="round">
                            <path d="M50 20 a30 30 0 0 1 30 30 v10"/>
                            <path d="M50 20 a30 30 0 0 0 -30 30 v14 a8 8 0 0 0 8 8"/>
                            <path d="M50 30 a20 20 0 0 1 20 20 v12"/>
                            <path d="M50 30 a20 20 0 0 0 -20 20 v8"/>
                            <path d="M50 40 a10 10 0 0 1 10 10 v18"/>
                        </g>
                    </svg>
                </div>
                <h2 class="page-title">Biometric Verification</h2>
                <p class="page-sub">Simulated fingerprint sensor &mdash; enter the fingerprint ID on file for this voter.</p>
                <form action="/verify_fp" method="get" style="text-align:left;">
                    <input type="hidden" name="id" value="{voter}">
                    <input type="hidden" name="tkn" value="{token}">
                    <label>Fingerprint ID</label>
                    <input type="text" name="fp" placeholder="e.g. fp1" required>
                    <button class="btn btn-primary">Scan &amp; Verify</button>
                </form>
            </div>
            """
            return self.respond(shell("Fingerprint Check", body))

        if path == "/verify_fp":
            voter = params.get("id", [""])[0]
            token = params.get("tkn", [""])[0]
            fp = params.get("fp", [""])[0]
            if qr_tokens.get(voter) != token:
                return self.respond(self._error_page("Invalid or expired access token.", "/home"))
            if not verify_fingerprint(voter, fp):
                return self.respond(self._error_page("Fingerprint verification failed.", "/vote?id=" + voter + "&tkn=" + token))
            if voter in voted:
                return self.respond(self._error_page("This Voter ID has already cast a vote.", "/home"))

            cards = ""
            for code, p in PARTIES.items():
                cards += f"""
                <div class="party-card">
                    {party_icon_html(code)}
                    <h4>{code}</h4>
                    <div class="full-name">{p['full']}</div>
                    <form action="/cast" method="get">
                        <input type="hidden" name="id" value="{voter}">
                        <input type="hidden" name="c" value="{code}">
                        <button class="vote-btn" style="background:{p['color']};">Cast Vote</button>
                    </form>
                </div>
                """
            body = f"""
            <div class="card">
                <h2 class="page-title">Select Your Candidate</h2>
                <p class="page-sub">Identity verified for {users.get(voter,'')} &nbsp;<span class="badge-id">{voter}</span>. Choose one party below.</p>
                <div class="party-grid">{cards}</div>
            </div>
            """
            return self.respond(shell("Cast Your Vote", body))

        if path == "/cast":
            voter = params.get("id", [""])[0]
            choice = params.get("c", [""])[0]
            p = PARTIES.get(choice)
            if contract.vote(voter, choice):
                broadcast_vote(f"{voter} voted {choice}")
                block = chain.chain[-1]
                body = f"""
                <div class="card center">
                    <div class="status-icon" style="background:var(--green);">&#10003;</div>
                    <h2 class="page-title">Vote Recorded Successfully</h2>
                    <p class="page-sub">Your vote has been sealed into the blockchain and cannot be altered.</p>
                    {party_icon_html(choice, 56) if p else ''}
                    <p style="margin-top:14px;"><b>{choice}</b> &mdash; {p['full'] if p else ''}</p>
                    <div class="block-item" style="text-align:left; margin-top:18px;">
                        <div class="idx">Block #{block.index}</div>
                        <div class="meta">{block.timestamp}</div>
                        <div class="meta">hash: {block.hash[:28]}&hellip;</div>
                    </div>
                    <a href="/" class="btn btn-outline" style="margin-top:20px;">Return to Home</a>
                </div>
                """
            else:
                body = f"""
                <div class="card center">
                    <div class="status-icon" style="background:var(--danger);">&#33;</div>
                    <h2 class="page-title">Vote Not Recorded</h2>
                    <p class="page-sub">Voter ID <span class="badge-id">{voter}</span> has already cast a vote in this election.</p>
                    <a href="/" class="btn btn-outline">Return to Home</a>
                </div>
                """
            return self.respond(shell("Vote Status", body))

        return self.respond(self._error_page("The page you're looking for doesn't exist.", "/"))

    def _error_page(self, message, back_url):
        body = f"""
        <div class="card center">
            <div class="status-icon" style="background:var(--danger);">&#33;</div>
            <h2 class="page-title">Something Went Wrong</h2>
            <p class="page-sub">{message}</p>
            <a href="{back_url}" class="btn btn-outline">Go Back</a>
        </div>
        """
        return shell("Error", body)

    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode())

    def log_message(self, format, *args):
        pass  # quiet logs


if __name__ == "__main__":
    print(f"Server running on 0.0.0.0:{PORT}")
    HTTPServer(("0.0.0.0", PORT), WebHandler).serve_forever()
