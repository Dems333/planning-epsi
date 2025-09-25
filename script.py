import requests
import datetime
import uuid
import os

API_URL = "https://api-hepedt2.tartrau.fr/api/courses/week"
STUDENT = "d.moricelegouet"

def get_events_for_date(date_str):
    params = {"student": STUDENT, "date": date_str}
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()
    return resp.json()

def format_datetime(date, time):
    dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y%m%dT%H%M%SZ")

def build_ics(events):
    now = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    ics = [
        "BEGIN:VCALENDAR",
        "METHOD:REQUEST",
        "PRODID:-//ADE/version 6.0",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
    ]

    for ev in events:
        uid = ev["id"] or str(uuid.uuid4())
        dtstart = format_datetime(ev["date"], ev["start_time"])
        dtend = format_datetime(ev["date"], ev["end_time"])
        summary = ev["subject"]
        location = ev["room"] if ev["room"] else "NS"
        teacher = ev["teacher"] if ev["teacher"] else ""
        description = f"\\n\\n{teacher}\\n(Exported :{now})\\n"

        ics.extend([
            "BEGIN:VEVENT",
            f"DTSTAMP:{now}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"LOCATION:{location}",
            f"DESCRIPTION:{description}",
            f"UID:{uid}",
            "CREATED:19700101T000000Z",
            f"LAST-MODIFIED:{now}",
            f"SEQUENCE:{int(datetime.datetime.utcnow().timestamp())}",
            "END:VEVENT"
        ])

    ics.append("END:VCALENDAR")
    return "\n".join(ics)

def main():
    start = datetime.date.today()
    end = datetime.date(2026, 9, 30)
    all_events = []
    current = start

    while current <= end:
        monday = current - datetime.timedelta(days=current.weekday())
        date_str = monday.strftime("%Y-%m-%d")
        try:
            week_events = get_events_for_date(date_str)
            all_events.extend(week_events)
        except Exception as e:
            print("Erreur API :", e)
        current += datetime.timedelta(weeks=1)

    # Création du dossier docs/ si inexistant
    os.makedirs("docs", exist_ok=True)

    # Sauvegarde dans docs/planning.ics → publié par GitHub Pages
    ics_content = build_ics(all_events)
    with open("docs/planning.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print("✅ planning.ics généré avec", len(all_events), "événements.")

if __name__ == "__main__":
    main()
