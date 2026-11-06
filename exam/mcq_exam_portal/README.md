# MCQ Exam Portal (Python / Flask)

A secure MCQ exam web app that runs on your PC and is reachable by other students on the same Wi‑Fi / LAN via your IP address.

Student results are stored **on the server** in `data/exam_records.json` — not in each browser — so the database is shared and dynamic for every client.

## Features

- Upload CSV question banks
- Fullscreen + tab-switch proctoring (auto-submit after 2 violations)
- Question palette, mark-for-review, progress bar
- Server-side student database (visible from any PC on the network)
- Export results to CSV
- Works across multiple machines without installing anything on student PCs

## Requirements

- Python 3.8+
- Flask

```bash
pip install -r requirements.txt
```

## How to run

1. Open a terminal in this folder:

```bash
cd mcq_exam_portal
python app.py
```

2. The console prints something like:

```
  Local:    http://127.0.0.1:5000
  Network:  http://192.168.1.42:5000
  Database: http://192.168.1.42:5000/database
```

3. **On your PC** open the Local URL.  
   **On student PCs** open the **Network** URL (same Wi‑Fi / LAN).

4. Students upload a questions CSV, fill in name/ID, and take the exam.  
   Results appear automatically on `/database` for everyone.

### Windows firewall

If other PCs cannot connect, allow port 5000:

```
netsh advfirewall firewall add rule name="MCQ Exam Portal" dir=in action=allow protocol=TCP localport=5000
```

### Linux

```bash
# optional if firewall is active
sudo ufw allow 5000/tcp
```

## CSV question format

One question per line, 6 columns:

```
"Question text","Option A","Option B","Option C","Option D","CorrectLetter"
```

Correct letter must be `A`, `B`, `C`, or `D`.  
A sample file is included: `sample_questions.csv`.

## Data storage

| File | Purpose |
|------|---------|
| `data/exam_records.json` | All exam attempts (shared, server-side) |

Deleting this file or using **Clear All** on the database page wipes all records.

## API (for reference)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/records` | List all records |
| POST | `/api/records` | Add a new exam result |
| DELETE | `/api/records` | Clear all records |
| GET | `/api/health` | Health check + IP |

## Stopping the server

Press `Ctrl+C` in the terminal where `app.py` is running.
