#!/usr/bin/env python3
"""Build the profile's native SVG layouts around unchanged FNAF character art."""

from base64 import b64encode
from datetime import date
from html import escape
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
INK = "#e9eddb"
GREEN = "#c0dd83"
MUTED = "#8d9c7e"
DIM = "#525f48"
RED = "#d56a56"
SIZES = {"freddy": (474, 960), "bonnie": (591, 960), "chica": (569, 960), "foxy": (1020, 960), "band": (1011, 692), "springtrap": (1220, 655), "springtrap-face": (500, 500)}


def text(x, y, value, size=18, color=INK, weight="normal", spacing=0, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" letter-spacing="{spacing}" text-anchor="{anchor}">{escape(str(value))}</text>'


def lines(x, y, content, size=20, color=MUTED, step=30):
    return "".join(text(x, y + index * step, line, size, color) for index, line in enumerate(content))


def rect(x, y, w, h, fill="#10160e", stroke="#35432b", radius=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def image(name, x, y, w, h, crop=None, opacity=1):
    source = ASSETS / "characters" / f"{name}.webp"
    width, height = SIZES[name]
    view = crop or (0, 0, width, height)
    data = b64encode(source.read_bytes()).decode()
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{" ".join(map(str, view))}" preserveAspectRatio="xMidYMin slice" overflow="hidden" opacity="{opacity}"><image width="{width}" height="{height}" href="data:image/webp;base64,{data}"/></svg>'


def panel(w, h, title, desc, content, accent=GREEN):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs>
<radialGradient id="ambient" cx="80%" cy="25%" r="90%"><stop stop-color="#202c19"/><stop offset=".6" stop-color="#0b100b"/><stop offset="1" stop-color="#060906"/></radialGradient>
<linearGradient id="fade"><stop stop-color="#080c08"/><stop offset="1" stop-color="#080c08" stop-opacity="0"/></linearGradient>
<linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#080c08" stop-opacity="0"/><stop offset="1" stop-color="#080c08"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 .5H4" stroke="#000" stroke-opacity=".24"/></pattern>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#a2bb7c" stroke-opacity=".035"/></pattern>
<pattern id="checker" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M0 0h14v14H0zM14 14h14v14H14z" fill="#7f8a69"/></pattern>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<style>.rec{{animation:record 3s steps(1) infinite}}@keyframes record{{0%,65%{{opacity:1}}66%,100%{{opacity:.35}}}}@media(prefers-reduced-motion:reduce){{.rec{{animation:none}}}}</style>
</defs>
{rect(0, 0, w, h, '#070b08', 'none', 6)}
{rect(1, 1, w-2, h-2, 'url(#ambient)', '#39452f', 5)}
<rect width="{w}" height="{h}" fill="url(#grid)"/>
<path d="M0 1H{w}" stroke="{accent}" stroke-opacity=".6"/>
<g font-family="'Courier New',Courier,monospace">{content}</g>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="5" fill="url(#scan)" pointer-events="none"/>
</svg>'''


def save(name, w, h, title, desc, content, accent=GREEN):
    (ASSETS / f"{name}.svg").write_text(panel(w, h, title, desc, content, accent))


def stamp(x, y, label, color=GREEN):
    return rect(x, y, len(label) * 11 + 30, 38, "#10180d", "#455837") + text(x + 15, y + 25, label, 16, color, spacing=1)


def heading(number, title, sub, w, mobile):
    size = 30 if mobile else 34
    return text(32, 39, f"{number} / FAZBEAR ENTERTAINMENT", 13, MUTED, spacing=2) + text(32, 89, title, size, GREEN, "bold") + text(32, 120, sub, 15 if mobile else 17, MUTED) + f'<path d="M32 142H{w-32}" stroke="#34432a"/>'


def build_hero(mobile=False):
    w, h = (600, 790) if mobile else (1200, 550)
    if mobile:
        content = image("springtrap-face", 178, 310, 422, 460)
        content += rect(0, 310, 260, 460, "url(#fade)", "none")
        content += rect(0, 690, 600, 100, "url(#bottom)", "none")
        content += text(30, 38, "FAZBEAR ENTERTAINMENT", 14, MUTED, spacing=3)
        content += text(30, 64, "PERSONNEL ARCHIVE / NIGHT 03", 12, MUTED, spacing=1)
        content += text(26, 157, "MRTR4P", 97, INK, "bold", -5)
        content += text(30, 193, "OMAR ALBOSATY", 21, GREEN, spacing=4)
        content += lines(30, 241, ["SOFTWARE & DATA", "ENGINEER"], 27, INK, 33)
        content += stamp(30, 328, "NIGHT SHIFT")
        content += text(30, 695, "I ALWAYS", 39, GREEN, "bold") + text(30, 738, "COME BACK.", 39, GREEN, "bold")
        content += text(30, 768, "...usually to fix one more bug.", 15, MUTED)
    else:
        content = image("springtrap-face", 668, 0, 532, 550)
        content += rect(580, 0, 240, 550, "url(#fade)", "none")
        content += rect(0, 425, 1200, 125, "url(#bottom)", "none")
        content += text(38, 42, "FAZBEAR ENTERTAINMENT // PERSONNEL ARCHIVE", 14, MUTED, spacing=2)
        content += '<circle class="rec" cx="1053" cy="36" r="4" fill="#d56a56"/>' + text(1068, 42, "REC / 03", 14, INK)
        content += text(31, 191, "MRTR4P", 129, INK, "bold", -6)
        content += text(39, 237, "OMAR ALBOSATY", 25, GREEN, spacing=6)
        content += text(39, 286, "SOFTWARE & DATA ENGINEER", 23, INK, spacing=1)
        content += lines(39, 329, ["Building APIs. Moving data.", "Keeping the systems alive after midnight."], 19, MUTED, 30)
        content += stamp(39, 398, "NIGHT SHIFT")
        content += text(39, 503, '"I ALWAYS COME BACK."', 27, GREEN, "bold")
        content += text(1157, 508, "CAM 03 / SPRINGTRAP", 13, MUTED, anchor="end")
    save("hero-mobile" if mobile else "hero", w, h, "MrTr4p — the night shift", "Omar Albosaty. Software and data engineer. Springtrap watches from the shadows. I always come back, usually to fix one more bug.", content)


def build_personnel(mobile=False):
    w, h = (600, 600) if mobile else (1200, 370)
    content = heading("01", "THE PERSON BEHIND THE MONITOR", "PERSONNEL FILE / MRTR4P", w, mobile)
    if mobile:
        content += image("freddy", 378, 174, 214, 345, (0, 0, 474, 760), .65)
        content += lines(32, 192, ["I'm Omar, a software", "& data engineer.", "", "I build backend systems,", "APIs, data pipelines,", "and interactive interfaces.", "", "Off the clock: Linux", "customization, ML,", "and game-inspired projects."], 20, INK, 32)
        content += text(32, 565, ">>> Welcome to the night shift.", 19, GREEN)
    else:
        content += image("freddy", 898, 86, 288, 284, (0, 0, 474, 470))
        content += lines(32, 191, ["I'm Omar, a software & data engineer.", "I build backend systems, APIs, data pipelines, and", "interactive interfaces. Off the clock: Linux customization,", "machine learning, and game-inspired projects."], 22, INK, 34)
        content += text(32, 337, ">>> Welcome to the night shift.", 20, GREEN)
    save("personnel-mobile" if mobile else "personnel", w, h, "Personnel file — Omar Albosaty", "Software and data engineer building backend systems, APIs, data pipelines and interactive interfaces. Interested in Linux customization, machine learning and game-inspired projects.", content)


def build_systems(mobile=False):
    w, h = (600, 960) if mobile else (1200, 550)
    content = heading("02", "PARTS & SERVICE", "The tools that keep everything running.", w, mobile)
    systems = [
        ("freddy", "01 / BACKEND", ["C# / ASP.NET Core", "Node.js / NestJS / Redis"], "#cca878"),
        ("bonnie", "02 / INTERFACES", ["TypeScript / React", "QML / interactive UI"], "#b0a0e6"),
        ("chica", "03 / DATA SYSTEMS", ["Python / SQL / PostgreSQL", "Pandas / Airflow"], "#e2ce7b"),
        ("foxy", "04 / INFRASTRUCTURE", ["Linux / Docker / Git", "Shell scripting / theming"], "#dd8c79"),
    ]
    for index, (character, label, tools, color) in enumerate(systems):
        x = 22 if mobile else 22 + (index % 2) * 590
        y = 165 + index * 190 if mobile else 165 + (index // 2) * 184
        cw, ch = (556, 172) if mobile else (566, 168)
        content += rect(x, y, cw, ch, "#0a100b", "#33432c", 3)
        sw, sh = SIZES[character]
        crop = (0, 0, sw, sw * (1.15 if character != "freddy" else 1.1))
        content += image(character, x + 3, y + 4, 129, ch - 8, crop)
        content += text(x + 147, y + 42, label, 19, color, "bold")
        content += lines(x + 147, y + 84, tools, 18, INK, 31)
        content += f'<path d="M{x+147} {y+143}H{x+cw-20}" stroke="{color}" stroke-opacity=".35"/>'
    save("systems-mobile" if mobile else "systems", w, h, "Parts and service — development toolkit", "Backend: C#, ASP.NET Core, Node.js, NestJS, Redis. Interfaces: TypeScript, React, QML. Data: Python, SQL, PostgreSQL, Pandas, Airflow. Infrastructure: Linux, Docker, Git and shell scripting.", content)


PROJECTS = [
    ("01", "freddy", "THE SHOW STAGE", "ARCADE PORTFOLIO", ["An interactive developer portfolio", "built with React, TypeScript & Three.js."], ["React & TypeScript.", "An interactive portfolio", "with Three.js."], "omar-arcade-portfolio", "#cca878"),
    ("02", "bonnie", "BACKSTAGE", "DISTRIBUTED JOB EXECUTION", ["Distributed job execution in C#.", "The backend side of the workshop."], ["Distributed job execution", "in C#."], "distributed_job_execution", "#b0a0e6"),
    ("03", "chica", "THE KITCHEN", "ETL / DATA PIPELINES", ["Python, PostgreSQL & orchestration.", "Getting the data from source to service."], ["Python & PostgreSQL.", "ETL and orchestration."], "ETL-Project", "#e2ce7b"),
    ("04", "foxy", "PIRATE COVE", "RE:ZERO / LINUX THEMING", ["A custom Arch Linux GRUB theme.", "Installer, backups & BIOS/UEFI VM checks."], ["Arch Linux boot theme.", "Installer, backups,", "BIOS/UEFI VM checks."], "rezero-grub-theme", "#dd8c79"),
]


def build_projects(mobile=False):
    for number, character, room, title, description, short, repo, color in PROJECTS:
        w, h = (600, 460) if mobile else (1200, 330)
        sw, _ = SIZES[character]
        crop = (0, 0, sw, sw * 1.15)
        content = image(character, 370 if mobile else 905, 20, 230 if mobile else 295, h - 20, crop, .75 if mobile else 1)
        content += rect(310 if mobile else 790, 0, 160, h, "url(#fade)", "none")
        content += text(30, 40, f"CAM {number} / {room}", 15, color, spacing=2)
        if mobile:
            title_lines = {"01": ["ARCADE", "PORTFOLIO"], "02": ["DISTRIBUTED", "JOB EXECUTION"], "03": ["ETL /", "DATA PIPELINES"], "04": ["RE:ZERO /", "LINUX THEMING"]}[number]
            content += lines(30, 112, title_lines, 35, INK, 43)
            content += lines(30, 228, short, 20, MUTED, 32)
            content += stamp(30, 321, "OPEN REPOSITORY ->", color)
            content += text(30, 420, f"/ {repo}", 14, DIM)
        else:
            content += text(30, 104, title, 36, INK, "bold")
            content += lines(30, 158, description, 22, MUTED, 35)
            content += stamp(30, 242, "OPEN REPOSITORY ->", color)
            content += text(30, 307, f"github.com/MrTr4p/{repo}", 14, DIM)
        save(f"project-{number}" + ("-mobile" if mobile else ""), w, h, f"CAM {number} — {title}", f'{title}. {" ".join(description)} Open the {repo} GitHub repository.', content, color)


def build_activity(mobile=False):
    data = json.loads((ASSETS / "profile-data.json").read_text())["data"]["user"]
    calendar = data["contributionsCollection"]["contributionCalendar"]
    repos = data["repositories"]
    stars = sum(repository["stargazerCount"] for repository in repos["nodes"])
    latest = calendar["weeks"][-1]["contributionDays"][-1]["date"]
    w, h = (600, 560) if mobile else (1200, 435)
    content = heading("07", "SECURITY LOG", f"Actual GitHub activity / snapshot {latest}", w, mobile)
    for index, (value, label) in enumerate([(calendar["totalContributions"], "CONTRIBUTIONS / YEAR"), (repos["totalCount"], "PUBLIC REPOSITORIES"), (stars, "REPOSITORY STARS")]):
        x = 32 + index * (187 if mobile else 387)
        content += text(x, 218, value, 47 if mobile else 54, GREEN, "bold")
        content += text(x, 249, label, 10 if mobile else 15, MUTED)
    colors = {"NONE": "#192116", "FIRST_QUARTILE": "#3c4f27", "SECOND_QUARTILE": "#657d38", "THIRD_QUARTILE": "#93ae58", "FOURTH_QUARTILE": "#c0dd83"}
    cell, gap = (8, 2) if mobile else (14, 5)
    for week_index, week in enumerate(calendar["weeks"]):
        for day in week["contributionDays"]:
            # Sunday-first rows match GitHub's contribution calendar.
            day_index = (date.fromisoformat(day["date"]).weekday() + 1) % 7
            x = 32 + week_index * (cell + gap)
            y = (302 if mobile else 278) + day_index * (cell + gap)
            content += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="1" fill="{colors[day["contributionLevel"]]}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
    if mobile:
        content += lines(32, 442, ["A year in the workshop.", "One contribution at a time.", "Open GitHub for the latest activity."], 16, MUTED, 28)
    save("activity-mobile" if mobile else "activity", w, h, "Security log — GitHub activity", f'GitHub snapshot from {latest}. {calendar["totalContributions"]} contributions in the past year, {repos["totalCount"]} public repositories and {stars} repository stars. Contribution calendar follows.', content)


def build_footer(mobile=False):
    w, h = (600, 550) if mobile else (1200, 370)
    content = image("band", 145 if mobile else 570, 185 if mobile else 5, 455 if mobile else 630, 360, None)
    content += rect(0, h - 130, w, 130, "url(#bottom)", "none")
    content += text(32, 48, "06:00 AM / SHIFT COMPLETE", 14, MUTED, spacing=2)
    content += lines(32, 112, ["STILL HERE.", "STILL BUILDING."], 43 if mobile else 48, GREEN, 53)
    content += text(32, 249 if not mobile else 205, ">>> See you next night.", 22 if not mobile else 19, INK)
    content += f'<rect x="1" y="{h-16}" width="{w-2}" height="15" fill="url(#checker)" opacity=".5"/>'
    content += text(32, h - 38, "MRTR4P / END OF TRANSMISSION", 12, MUTED, spacing=2)
    save("footer-mobile" if mobile else "footer", w, h, "Shift complete — still here, still building", "Freddy, Bonnie, Chica, Foxy and Golden Freddy at the end of the night shift. See you next night.", content)


def build_buttons():
    for filename, label in [("portfolio", "PORTFOLIO >"), ("linkedin", "LINKEDIN >"), ("contact", "CONTACT >"), ("repositories", "ALL REPOSITORIES ->")]:
        width, size = (300, 19) if filename == "repositories" else (220, 22)
        content = text(22, 39, label, size, GREEN, "bold", 1)
        save(f"link-{filename}", width, 64, label, label, content)
    content = heading("03-06", "CHOOSE A CAMERA", "Four rooms. Four things I've built. Select a feed to open it.", 1200, False)
    save("project-heading", 1200, 155, "Choose a camera — selected projects", "Select a project camera feed to open its GitHub repository.", content)
    content = heading("03-06", "CHOOSE A CAMERA", "Select a feed to open its repository.", 600, True)
    save("project-heading-mobile", 600, 155, "Choose a camera — selected projects", "Select a project camera feed to open its GitHub repository.", content)


if "--refresh" in sys.argv:
    login = subprocess.check_output(["gh", "api", "user", "--jq", ".login"], text=True).strip()
    if login != "MrTr4p":
        raise SystemExit(f"Expected local GitHub account MrTr4p, found {login}. Stopping.")
    query = 'query { user(login:"MrTr4p") { repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100) { totalCount nodes { name stargazerCount } } contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }'
    data = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={query}"], text=True)
    json.loads(data)["data"]["user"]
    (ASSETS / "profile-data.json").write_text(data)

for mobile in (False, True):
    build_hero(mobile)
    build_personnel(mobile)
    build_systems(mobile)
    build_projects(mobile)
    build_activity(mobile)
    build_footer(mobile)
build_buttons()
print("Built responsive profile panels using local character renders.")
