"""
MCQ Exam Portal - Flask backend
Runs on all network interfaces so other PCs can access via your IP address.
Student exam records are stored server-side in data/exam_records.json
"""

import os
import json
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RECORDS_FILE = os.path.join(DATA_DIR, "exam_records.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_records():
    """Load all exam records from the JSON file."""
    if not os.path.exists(RECORDS_FILE):
        return []
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_records(records):
    """Persist records to the JSON file (atomic write)."""
    tmp = RECORDS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    os.replace(tmp, RECORDS_FILE)


def get_local_ip():
    """Best-effort local LAN IP for display."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("exam.html")


@app.route("/database")
def database_page():
    return render_template("database.html")


# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/records", methods=["GET"])
def get_records():
    """Return all stored exam records (used by database page)."""
    records = load_records()
    # Newest first
    records_sorted = sorted(
        records,
        key=lambda r: r.get("submittedAt", ""),
        reverse=True,
    )
    return jsonify({"ok": True, "records": records_sorted, "count": len(records_sorted)})


@app.route("/api/records", methods=["POST"])
def add_record():
    """Accept a new exam result from any client and store it."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": False, "error": "No JSON body"}), 400

    required = ["studentId", "name", "subject", "date", "total", "correct", "wrong", "percentage"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    record = {
        "studentId": str(data["studentId"]).strip(),
        "name": str(data["name"]).strip(),
        "subject": str(data["subject"]).strip(),
        "date": str(data["date"]).strip(),
        "total": int(data["total"]),
        "correct": int(data["correct"]),
        "wrong": int(data["wrong"]),
        "percentage": float(data["percentage"]),
        "timeTaken": str(data.get("timeTaken", "")),
        "violationCount": int(data.get("violationCount", 0)),
        "integrity": str(data.get("integrity", "Clean")),
        "terminated": bool(data.get("terminated", False)),
        "submittedAt": data.get("submittedAt") or datetime.utcnow().isoformat() + "Z",
        "clientIp": request.remote_addr or "",
    }

    records = load_records()
    records.append(record)
    save_records(records)

    return jsonify({"ok": True, "message": "Record saved", "totalRecords": len(records)})


@app.route("/api/records", methods=["DELETE"])
def clear_records():
    """Clear all records (admin action from database page)."""
    save_records([])
    return jsonify({"ok": True, "message": "All records cleared"})


@app.route("/api/health")
def health():
    return jsonify({
        "ok": True,
        "ip": get_local_ip(),
        "recordsFile": RECORDS_FILE,
        "recordCount": len(load_records()),
    })


if __name__ == "__main__":
    host = "0.0.0.0"   # listen on all interfaces → reachable via your LAN IP
    port = 50201
    local_ip = get_local_ip()
    print("=" * 60)
    print("  MCQ Exam Portal")
    print("=" * 60)
    print(f"  Local:    http://127.0.0.1:{port}")
    print(f"  Network:  http://{local_ip}:{port}")
    print(f"  Database: http://{local_ip}:{port}/database")
    print(f"  Records:  {RECORDS_FILE}")
    print("=" * 60)
    print("  Share the Network URL with students on the same Wi-Fi/LAN.")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    app.run(host=host, port=port, debug=False, threaded=True)
