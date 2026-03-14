import os
from flask import Flask, request, jsonify
from datetime import datetime
import pytz
import re

app = Flask(__name__)

TIMEZONE_MAP = {
    "lagos": "Africa/Lagos", "nigeria": "Africa/Lagos", "warri": "Africa/Lagos",
    "abuja": "Africa/Lagos", "port harcourt": "Africa/Lagos", "ibadan": "Africa/Lagos",
    "kano": "Africa/Lagos", "london": "Europe/London", "uk": "Europe/London",
    "england": "Europe/London", "manchester": "Europe/London", "birmingham": "Europe/London",
    "new york": "America/New_York", "nyc": "America/New_York", "chicago": "America/Chicago",
    "los angeles": "America/Los_Angeles", "la": "America/Los_Angeles",
    "houston": "America/Chicago", "dallas": "America/Chicago", "atlanta": "America/New_York",
    "miami": "America/New_York", "seattle": "America/Los_Angeles", "denver": "America/Denver",
    "toronto": "America/Toronto", "vancouver": "America/Vancouver", "montreal": "America/Toronto",
    "paris": "Europe/Paris", "berlin": "Europe/Berlin", "amsterdam": "Europe/Amsterdam",
    "madrid": "Europe/Madrid", "rome": "Europe/Rome", "moscow": "Europe/Moscow",
    "stockholm": "Europe/Stockholm", "warsaw": "Europe/Warsaw", "athens": "Europe/Athens",
    "lisbon": "Europe/Lisbon", "vienna": "Europe/Vienna", "prague": "Europe/Prague",
    "nairobi": "Africa/Nairobi", "kenya": "Africa/Nairobi", "accra": "Africa/Accra",
    "ghana": "Africa/Accra", "johannesburg": "Africa/Johannesburg", "south africa": "Africa/Johannesburg",
    "cairo": "Africa/Cairo", "egypt": "Africa/Cairo", "kampala": "Africa/Kampala",
    "uganda": "Africa/Kampala", "dakar": "Africa/Dakar", "senegal": "Africa/Dakar",
    "dubai": "Asia/Dubai", "uae": "Asia/Dubai", "india": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata", "delhi": "Asia/Kolkata", "bangalore": "Asia/Kolkata",
    "singapore": "Asia/Singapore", "tokyo": "Asia/Tokyo", "japan": "Asia/Tokyo",
    "shanghai": "Asia/Shanghai", "china": "Asia/Shanghai", "beijing": "Asia/Shanghai",
    "seoul": "Asia/Seoul", "korea": "Asia/Seoul", "karachi": "Asia/Karachi",
    "pakistan": "Asia/Karachi", "dhaka": "Asia/Dhaka", "bangladesh": "Asia/Dhaka",
    "bangkok": "Asia/Bangkok", "thailand": "Asia/Bangkok", "jakarta": "Asia/Jakarta",
    "indonesia": "Asia/Jakarta", "riyadh": "Asia/Riyadh", "saudi arabia": "Asia/Riyadh",
    "istanbul": "Europe/Istanbul", "turkey": "Europe/Istanbul",
    "sydney": "Australia/Sydney", "australia": "Australia/Sydney",
    "melbourne": "Australia/Melbourne", "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth", "auckland": "Pacific/Auckland", "new zealand": "Pacific/Auckland",
    "sao paulo": "America/Sao_Paulo", "brazil": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires", "argentina": "America/Argentina/Buenos_Aires",
    "mexico city": "America/Mexico_City", "mexico": "America/Mexico_City",
    "bogota": "America/Bogota", "colombia": "America/Bogota",
    "lima": "America/Lima", "peru": "America/Lima",
}

ABBR_MAP = {
    "CST": "America/Chicago", "CDT": "America/Chicago", "EST": "America/New_York",
    "EDT": "America/New_York", "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "MST": "America/Denver", "MDT": "America/Denver", "GMT": "Europe/London",
    "UTC": "UTC", "WAT": "Africa/Lagos", "CAT": "Africa/Harare", "EAT": "Africa/Nairobi",
    "CET": "Europe/Paris", "EET": "Europe/Athens", "IST": "Asia/Kolkata",
    "GST": "Asia/Dubai", "SGT": "Asia/Singapore", "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul", "AEST": "Australia/Sydney", "AEDT": "Australia/Sydney",
    "AWST": "Australia/Perth", "NZST": "Pacific/Auckland", "NZDT": "Pacific/Auckland",
    "BRT": "America/Sao_Paulo", "PKT": "Asia/Karachi", "BST": "Europe/London",
}

def resolve_timezone(text):
    text = text.strip()
    if text.upper() in ABBR_MAP:
        return pytz.timezone(ABBR_MAP[text.upper()])
    lower = text.lower()
    if lower in TIMEZONE_MAP:
        return pytz.timezone(TIMEZONE_MAP[lower])
    for key in TIMEZONE_MAP:
        if lower in key or key in lower:
            return pytz.timezone(TIMEZONE_MAP[key])
    try:
        return pytz.timezone(text)
    except:
        pass
    return None

def parse_time(time_str):
    time_str = time_str.strip().upper()
    for fmt in ["%I:%M %p", "%I %p", "%H:%M", "%H%M"]:
        try:
            t = datetime.strptime(time_str, fmt)
            return t.hour, t.minute
        except:
            continue
    return None, None

def convert_time(time_str, from_tz, to_tz):
    hour, minute = parse_time(time_str)
    if hour is None:
        return None, None
    today = datetime.now().date()
    naive_dt = datetime(today.year, today.month, today.day, hour, minute)
    aware_dt = from_tz.localize(naive_dt)
    converted = aware_dt.astimezone(to_tz)
    return converted.strftime("%I:%M %p").lstrip("0"), f"{converted.strftime('%A')} — {converted.strftime('%Z')}"

@app.route("/meetingtime", methods=["POST"])
def meetingtime():
    text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"response_type": "ephemeral", "text": "*Zone It — Usage:*\n`/meetingtime [time] [timezone] [your city]`\n\n*Examples:*\n• `/meetingtime 11:30 AM CST Lagos`\n• `/meetingtime 3:00 PM GMT Nairobi`"})

    match = re.match(r'^(\d{1,2}(?::\d{2})?\s*(?:AM|PM)?)\s+([A-Z]{2,5})\s+(.+)$', text.strip(), re.IGNORECASE)
    if not match:
        return jsonify({"response_type": "ephemeral", "text": "Try: `/meetingtime 11:30 AM CST Lagos`"})

    time_str, source_str, dest_str = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
    from_tz = resolve_timezone(source_str)
    to_tz = resolve_timezone(dest_str)

    if not from_tz:
        return jsonify({"response_type": "ephemeral", "text": f"I don't recognize *{source_str}* as a timezone. Try CST, GMT, WAT, EST."})
    if not to_tz:
        return jsonify({"response_type": "ephemeral", "text": f"I don't recognize *{dest_str}*. Try a major city like Lagos, London, Nairobi."})

    converted_time, day_info = convert_time(time_str, from_tz, to_tz)
    if not converted_time:
        return jsonify({"response_type": "ephemeral", "text": f"Couldn't parse *{time_str}*. Try `11:30 AM` or `14:00`."})

    return jsonify({"response_type": "in_channel", "text": f"🌍 *Zone It — Time Conversion*\n🕐 *{time_str.upper()} {source_str.upper()}* → *{converted_time}* in *{dest_str.title()}* ({day_info})"})

@app.route("/", methods=["GET"])
def health():
    return "Zone It is running.", 200

@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    return """<html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f0f1a;color:#f0c060;"><h1>✦ Zone It</h1><p style="color:#fff;margin-top:20px;">Successfully installed to your Slack workspace.</p><p style="color:#aaa;margin-top:10px;">Type <strong style="color:#f0c060;">/meetingtime 11:30 AM CST Lagos</strong> in any channel to get started.</p></body></html>""", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
