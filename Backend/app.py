from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_conn, init_db
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

def parse_iso(s: str) -> datetime:
    # accept "Z" or "+00:00" and other offsets
    s = s.strip()
    if s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    return datetime.fromisoformat(s)

def iso_z(dt: datetime) -> str:
    # ensure we hand SQLite a consistent lexicographically sortable UTC format
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

# ---- initialize DB once at startup (Flask 3 removed before_first_request)
with app.app_context():
    init_db()
# ---------------------------------------------------------------

@app.get("/events")
def list_events():
    start = request.args.get("start")
    end   = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "start and end query params (ISO) are required"}), 400
    try:
        s = parse_iso(start); e = parse_iso(end)
        if s > e:
            return jsonify({"error": "start must be <= end"}), 400
        # normalize to UTC Z strings so TEXT comparison in SQLite is reliable
        start_z = iso_z(s); end_z = iso_z(e)
    except Exception:
        return jsonify({"error": "invalid ISO date"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM events
        WHERE start_dt <= ? AND end_dt >= ?
        ORDER BY start_dt ASC
    """, (end_z, start_z))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.post("/events")
def create_event():
    data = request.get_json(force=True)
    for k in ["title", "start_dt", "end_dt"]:
        if k not in data:
            return jsonify({"error": "title, start_dt, end_dt required"}), 400
    try:
        s = parse_iso(data["start_dt"]); e = parse_iso(data["end_dt"])
        if s >= e:
            return jsonify({"error": "start_dt < end_dt required"}), 400
        s_z = iso_z(s); e_z = iso_z(e)
    except Exception:
        return jsonify({"error": "invalid ISO datetimes"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (title, description, start_dt, end_dt, all_day, color, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("description"),
        s_z,
        e_z,
        1 if data.get("all_day") else 0,
        data.get("color", "#3b82f6"),
        data.get("location"),
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"id": new_id}), 201

@app.put("/events/<int:event_id>")
def update_event(event_id):
    data = request.get_json(force=True)
    fields = []
    params = []
    for k in ["title","description","start_dt","end_dt","all_day","color","location"]:
        if k in data:
            fields.append(f"{k}=?")
            # convert booleans to 0/1 if needed
            if k == "all_day":
                params.append(1 if data[k] else 0)
            else:
                params.append(data[k])
    if not fields:
        return jsonify({"error":"no fields to update"}), 400
    params.append(event_id)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE events SET {', '.join(fields)} WHERE id=?", params)
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if changed == 0:
        return jsonify({"error":"not found"}), 404
    return jsonify({"ok": True})

@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if changed == 0:
        return jsonify({"error":"not found"}), 404
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
