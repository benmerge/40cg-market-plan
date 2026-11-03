"""Regenerate the calendar files from events.json.

Run:  python3 build.py
Writes events.ics (the subscribable feed with every event) and
events/<id>.ics (one file per event, for "Add to Calendar" buttons).
"""
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TZ = [
    "BEGIN:VTIMEZONE", "TZID:America/Chicago",
    "BEGIN:STANDARD", "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
    "TZOFFSETFROM:-0500", "TZOFFSETTO:-0600", "TZNAME:CST", "END:STANDARD",
    "BEGIN:DAYLIGHT", "DTSTART:19700308T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
    "TZOFFSETFROM:-0600", "TZOFFSETTO:-0500", "TZNAME:CDT", "END:DAYLIGHT",
    "END:VTIMEZONE",
]


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode()
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b" " + b[cut:]
    out.append(b.decode())
    return "\r\n".join(out)


def vevent(e, stamp):
    ds = e["date"].replace("-", "")
    lines = ["BEGIN:VEVENT", f"UID:{e['id']}@40cg-market-plan", f"DTSTAMP:{stamp}",
             "SUMMARY:" + esc("40CG: " + e["title"])]
    if e.get("start"):
        end = (e.get("end") or e["start"]).replace(":", "")
        lines += [f"DTSTART;TZID=America/Chicago:{ds}T{e['start'].replace(':', '')}00",
                  f"DTEND;TZID=America/Chicago:{ds}T{end}00"]
    else:
        nd = (dt.date.fromisoformat(e["date"]) + dt.timedelta(days=1)).strftime("%Y%m%d")
        lines += [f"DTSTART;VALUE=DATE:{ds}", f"DTEND;VALUE=DATE:{nd}"]
    if e.get("location"):
        lines.append("LOCATION:" + esc(e["location"]))
    desc = (e.get("notes") or "").strip()
    if e.get("cost"):
        desc = (desc + " Cost: $" + e["cost"]).strip()
    if desc:
        lines.append("DESCRIPTION:" + esc(desc))
    if e.get("type") == "market":
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Booth tomorrow", "TRIGGER:-P1D", "END:VALARM",
                  "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Booth in 2 hours", "TRIGGER:-PT2H", "END:VALARM"]
    lines.append("END:VEVENT")
    return lines


def calendar(events, stamp, name):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//40 Century Grain//Market Plan//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{name}",
             "X-WR-TIMEZONE:America/Chicago", "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
             "X-PUBLISHED-TTL:PT6H"] + TZ
    for e in events:
        lines += vevent(e, stamp)
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(x) for x in lines) + "\r\n"


def main():
    with open(os.path.join(HERE, "events.json")) as f:
        events = json.load(f)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    with open(os.path.join(HERE, "events.ics"), "w", newline="") as f:
        f.write(calendar(events, stamp, "40 Century Grain"))
    os.makedirs(os.path.join(HERE, "events"), exist_ok=True)
    for e in events:
        with open(os.path.join(HERE, "events", e["id"] + ".ics"), "w", newline="") as f:
            f.write(calendar([e], stamp, "40 Century Grain"))
    print(f"Wrote events.ics and {len(events)} event files")


if __name__ == "__main__":
    main()
