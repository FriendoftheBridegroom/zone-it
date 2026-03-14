from flask import Flask, request, jsonify
from datetime import datetime
import pytz
import re

app = Flask(__name__)

# City to timezone mapping
TIMEZONE_MAP = {
    # Nigeria
    "lagos": "Africa/Lagos",
    "nigeria": "Africa/Lagos",
    "warri": "Africa/Lagos",
    "abuja": "Africa/Lagos",
    "port harcourt": "Africa/Lagos",
    "ibadan": "Africa/Lagos",
    "kano": "Africa/Lagos",

    # UK
    "london": "Europe/London",
    "uk": "Europe/London",
    "england": "Europe/London",
    "manchester": "Europe/London",
    "birmingham": "Europe/London",

    # USA
    "new york": "America/New_York",
    "nyc": "America/New_York",
    "chicago": "America/Chicago",
    "cst": "America/Chicago",
    "est": "America/New_York",
    "pst": "America/Los_Angeles",
    "mst": "America/Denver",
    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "houston": "America/Chicago",
    "dallas": "America/Chicago",
    "atlanta": "America/New_York",
    "miami": "America/New_York",
    "seattle": "America/Los_Angeles",
    "denver": "America/Denver",

    # Canada
    "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",
    "montreal": "America/Toronto",

    # Europe
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "amsterdam": "Europe/Amsterdam",
    "madrid": "Europe/Madrid",
    "rome": "Europe/Rome",
    "moscow": "Europe/Moscow",
    "stockholm": "Europe/Stockholm",
    "warsaw": "Europe/Warsaw",
    "athens": "Europe/Athens",
    "lisbon": "Europe/Lisbon",
    "vienna": "Europe/Vienna",
    "prague": "Europe/Prague",

    # Africa
    "nairobi": "Africa/Nairobi",
    "kenya": "Africa/Nairobi",
    "accra": "Africa/Accra",
    "ghana": "Africa/Accra",
    "johannesburg": "Africa/Johannesburg",
    "south africa": "Africa/Johannesburg",
    "cairo": "Africa/Cairo",
    "egypt": "Africa/Cairo",
    "addis ababa": "Africa/Addis_Ababa",
    "ethiopia": "Africa/Addis_Ababa",
    "dar es salaam": "Africa/Dar_es_Salaam",
    "tanzania": "Africa/Dar_es_Salaam",
    "kampala": "Africa/Kampala",
    "uganda": "Africa/Kampala",
    "dakar": "Africa/Dakar",
    "senegal": "Africa/Dakar",

    # Asia & Middle East
    "dubai": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "india": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "ist": "Asia/Kolkata",
    "singapore": "Asia/Singapore",
    "tokyo": "Asia/Tokyo",
    "japan": "Asia/Tokyo",
    "shanghai": "Asia/Shanghai",
    "china": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "seoul": "Asia/Seoul",
    "korea": "Asia/Seoul",
    "karachi": "Asia/Karachi",
    "pakistan": "Asia/Karachi",
    "dhaka": "Asia/Dhaka",
    "bangladesh": "Asia/Dhaka",
    "bangkok": "Asia/Bangkok",
    "thailand": "Asia/Bangkok",
    "jakarta": "Asia/Jakarta",
    "indonesia": "Asia/Jakarta",
    "riyadh": "Asia/Riyadh",
    "saudi arabia": "Asia/Riyadh",
    "jerusalem": "Asia/Jerusalem",
    "israel": "Asia/Jerusalem",
    "tehran": "Asia/Tehran",
    "iran": "Asia/Tehran",
    "istanbul": "Europe/Istanbul",
    "turkey": "Europe/Istanbul",

    # Oceania
    "sydney": "Australia/Sydney",
    "australia": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth",
    "auckland": "Pacific/Auckland",
    "new zealand": "Pacific/Auckland",

    # Latin America
    "sao paulo": "America/Sao_Paulo",
    "brazil": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "argentina": "America/Argentina/Buenos_Aires",
    "mexico city": "America/Mexico_City",
    "mexico": "America/Mexico_City",
    "bogota": "America/Bogota",
    "colombia": "America/Bogota",
    "lima": "America/Lima",
    "peru": "America/Lima",
}

# Timezone abbreviation to pytz timezone
ABBR_MAP = {
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "GMT": "Europe/London",
    "UTC": "UTC",
    "WAT": "Africa/Lagos",
    "CAT": "Africa/Harare",
    "EAT": "Africa/Nairobi",
    "CET": "Europe/Paris",
    "EET": "Europe/Athens",
    "IST": "Asia/Kolkata",
    "GST": "Asia/Dubai",
    "SGT": "Asia/Singapore",
    "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul",
    "AEST": "Australia/Sydney",
    "AEDT": "Australia/Sydney",
    "AWST": "Australia/Perth",
    "NZST": "Pacific/Auckland",
    "NZDT": "Pacific/Auckland",
    "BRT": "America/Sao_Paulo",
    "PKT": "Asia/Karachi",
    "BST": "Europe/London",
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
    formats = ["%I:%M %p", "%I %p", "%H:%M", "%H%M"]
    for fmt in formats:
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
    time_out = converted.strftime("%I:%M %p").lstrip("0")
    day_out = converted.strftime("%A")
    tz_abbr = converted.strftime("%Z")
    return time_out, f"{day_out} — {tz_abbr}"

@app.route("/meetingtime", methods=["POST"])
def meetingtime():
    data = request.form
    text = data.get("text", "").strip()

    if not text:
        return jsonify({
            "response_type": "ephemeral",
            "text": (
                "*Zone It — Usage:*\n"
                "`/meetingtime [time] [timezone] [your city]`\n\n"
                "*Examples:*\n"
                "• `/meetingtime 11:30 AM CST Lagos`\n"
                "• `/meetingtime 3:00 PM GMT Nairobi`\n"
                "• `/meetingtime 9:00 AM EST Sydney`"
            )
        })

    pattern = r'^(\d{1,2}(?::\d{2})?\s*(?:AM|PM)?)\s+([A-Z]{2,5})\s+(.+)$'
    match = re.match(pattern, text.strip(), re.IGNORECASE)

    if not match:
        return jsonify({
            "response_type": "ephemeral",
            "text": (
                "I couldn't understand that format. Try:\n"
                "`/meetingtime 11:30 AM CST Lagos`\n"
                "`/meetingtime 3:00 PM GMT Nairobi`"
            )
        })

    time_str = match.group(1).strip()
    source_str = match.group(2).strip()
    dest_str = match.group(3).strip()

    from_tz = resolve_timezone(source_str)
    to_tz = resolve_timezone(dest_str)

    if not from_tz:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"I don't recognize *{source_str}* as a timezone. Try abbreviations like CST, GMT, WAT, EST."
        })

    if not to_tz:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"I don't recognize *{dest_str}* as a city or country. Try a major city name like Lagos, London, Nairobi, Sydney."
        })

    converted_time, day_info = convert_time(time_str, from_tz, to_tz)

    if not converted_time:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"I couldn't parse the time *{time_str}*. Try formats like `11:30 AM` or `14:00`."
        })

    return jsonify({
        "response_type": "in_channel",
        "text": (
            f"🌍 *Zone It — Time Conversion*\n"
            f"🕐 *{time_str.upper()} {source_str.upper()}* → "
            f"*{converted_time}* in *{dest_str.title()}* ({day_info})"
        )
    })

@app.route("/", methods=["GET"])
def health():
    return "Zone It is running.", 200

@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    code = request.args.get("code")
    if not code:
        return "Installation failed. No code provided.", 400
    return """
    <html>
    <body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f0f1a;color:#f0c060;">
    <h1 style="font-size:2rem;">✦ Zone It</h1>
    <p style="font-size:1.2rem;color:#fff;margin-top:20px;">Successfully installed to your Slack workspace.</p>
    <p style="color:#aaa;margin-top:10px;">Type <strong style="color:#f0c060;">/meetingtime 11:30 AM CST Lagos</strong> in any channel to get started.</p>
    </body>
    </html>
    """, 200

if __name__ == "__main__":
    app.run(debug=True)
