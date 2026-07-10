##############################################
#  BLOCKCHAIN E-VOTING SYSTEM (DEPLOY-READY VERSION)
#  Clean UI • Admin Login • Timestamped Blockchain
#  Web-based Fingerprint Step (fixed for hosting)
##############################################

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import time
import hashlib
import os

# ---------------- FINGERPRINT MODULE ----------------
# NOTE: original code used input() to "scan" a fingerprint. That works only
# in a local terminal. On a real web server there's no terminal attached to
# a browser request, so it would hang forever. This version asks for the
# simulated fingerprint ID through a web form field instead.
FINGERPRINT_TEMPLATES = {
    "VOTER1001": "fp1", "VOTER1002": "fp2", "VOTER1003": "fp3", "VOTER1004": "fp4",
    "VOTER1005": "fp5", "VOTER1006": "fp6", "VOTER1007": "fp7", "VOTER1008": "fp8"
}

def verify_fingerprint(user_id, scanned_value):
    return FINGERPRINT_TEMPLATES.get(user_id) == scanned_value

PORT = int(os.environ.get("PORT", 8080))

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
ADMIN_PASSWORD = "admin123"

def generate_ascii_qr(voter_id):
    token = hashlib.sha256(f"{voter_id}{time.time()}".encode()).hexdigest()[:16]
    qr_tokens[voter_id] = token
    qr = f"#####################\n#  QR LOGIN TOKEN   #\n#   {token[:10]}   #\n#####################"
    return qr, token

##############################################
# SMART CONTRACT
##############################################
class SmartContract:
    def __init__(self):
        self.parties = {"BJP": "...", "SP": "...", "CONGRESS": "...", "BSP": "...", "AAP": "..."}
        self.vote_count = {p: 0 for p in self.parties}

    def vote(self, voter, choice):
        if voter in voted:
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
        self.chain = [Block(0, time.strftime("%d-%m-%Y %H:%M:%S"), "GENESIS", "0")]

    def add_block(self, data):
        last = self.chain[-1]
        self.chain.append(Block(len(self.chain), time.strftime("%d-%m-%Y %H:%M:%S"), data, last.hash))

chain = Blockchain()

def broadcast_vote(data):
    chain.add_block(data)

##############################################
# HTML TEMPLATE
##############################################
def html_page(title, body):
    css = """
    <style>
    body { font-family: Arial; background: #f4f4f4; margin: 0; }
    h1 { background: #111; color: #fff; padding: 15px; text-align:center; }
    .container { background: #fff; padding: 25px; width: 55%; margin: auto; border-radius: 10px; }
    input, button { padding: 10px; font-size: 16px; margin: 6px; }
    .primary-btn { background: #1e73ff; color: white; border: none; }
    .vote-btn { background: green; color: white; border: none; }
    </style>
    """
    return f"<html><head><title>{title}</title>{css}</head><body><h1>{title}</h1><div class='container'>{body}</div></body></html>"

##############################################
# MAIN WEB HANDLER
##############################################
class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = """
            <h2>Welcome to Our E-Voting System Project</h2>
            <p>Secure • Transparent • Blockchain Based</p>
            <a href="/loading"><button class="primary-btn">Enter System</button></a>
            """
            return self.respond(html_page("Welcome", body))

        if path == "/loading":
            return self.respond("""
            <html><head>
            <meta http-equiv="refresh" content="2;URL='/home'" />
            <style>
            body{display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;}
            </style></head>
            <body><h2>Loading E-Voting System...</h2></body></html>
            """)

        if path == "/home":
            body = """
            <h2>QR Login</h2>
            <form action="/qr" method="get">
                <input name="id" placeholder="Enter Voter ID">
                <button class="primary-btn">Enter</button>
            </form>
            <p><a href="/admin_login">Admin Login</a></p>
            """
            return self.respond(html_page("E-Voting Home", body))

        if path == "/admin_login":
            return self.respond(html_page("Admin Login", """
                <form action="/admin" method="get">
                    <input type="password" name="pass" placeholder="Admin password">
                    <button class="primary-btn">Login</button>
                </form>
            """))

        if path == "/admin":
            params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            pw = params.get("pass", [""])[0]
            if pw != ADMIN_PASSWORD:
                return self.respond(html_page("Error", "Wrong password"))
            rows = "".join(f"<tr><td>{p}</td><td>{c}</td></tr>" for p, c in contract.vote_count.items())
            blocks = "".join(
                f"<li>Block {b.index} [{b.timestamp}] {b.data} (hash: {b.hash[:12]}...)</li>"
                for b in chain.chain
            )
            body = f"""
            <h2>Live Results</h2>
            <table border="1" cellpadding="6"><tr><th>Party</th><th>Votes</th></tr>{rows}</table>
            <h2>Blockchain Ledger</h2>
            <ul>{blocks}</ul>
            """
            return self.respond(html_page("Admin Dashboard", body))

        if path == "/qr":
            params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            voter = params.get("id", [""])[0]
            if voter not in users:
                return self.respond(html_page("Error", "Invalid Voter ID"))
            qr, token = generate_ascii_qr(voter)
            body = f"""
            <pre>{qr}</pre>
            <p>{token}</p>
            <form action="/vote" method="get">
                <input type="hidden" name="id" value="{voter}">
                <input name="tkn" placeholder="Paste token above">
                <button>Login</button>
            </form>
            """
            return self.respond(html_page("QR Login", body))

        if path == "/vote":
            params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            voter = params.get("id", [""])[0]
            token = params.get("tkn", [""])[0]
            if qr_tokens.get(voter) != token:
                return self.respond(html_page("Error", "Invalid Token"))
            # Web-based fingerprint step (replaces blocking input())
            body = f"""
            <h2>Fingerprint Verification</h2>
            <p>Simulated sensor — enter the fingerprint ID on file for this voter.</p>
            <form action="/verify_fp" method="get">
                <input type="hidden" name="id" value="{voter}">
                <input type="hidden" name="tkn" value="{token}">
                <input name="fp" placeholder="Fingerprint ID (e.g. fp1)">
                <button class="primary-btn">Scan</button>
            </form>
            """
            return self.respond(html_page("Fingerprint Check", body))

        if path == "/verify_fp":
            params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            voter = params.get("id", [""])[0]
            token = params.get("tkn", [""])[0]
            fp = params.get("fp", [""])[0]
            if qr_tokens.get(voter) != token:
                return self.respond(html_page("Error", "Invalid Token"))
            if not verify_fingerprint(voter, fp):
                return self.respond(html_page("Error", "Fingerprint Failed"))
            cards = ""
            for p in contract.parties:
                cards += f"""
                <form action="/cast" method="get">
                    <h3>{p}</h3>
                    <input type="hidden" name="id" value="{voter}">
                    <input type="hidden" name="c" value="{p}">
                    <button class="vote-btn">Vote</button>
                </form>
                """
            return self.respond(html_page("Vote", cards))

        if path == "/cast":
            params = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            voter = params.get("id", [""])[0]
            choice = params.get("c", [""])[0]
            if contract.vote(voter, choice):
                broadcast_vote(f"{voter} voted {choice}")
                msg = "Vote Recorded"
            else:
                msg = "Already Voted"
            return self.respond(html_page("Status", msg))

        return self.respond(html_page("404", "Not Found"))

    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def log_message(self, format, *args):
        pass  # quiet logs


if __name__ == "__main__":
    print(f"Server running on 0.0.0.0:{PORT}")
    HTTPServer(("0.0.0.0", PORT), WebHandler).serve_forever()
