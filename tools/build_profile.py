#!/usr/bin/env python3
"""Build original animated vector panels for the GitHub night-shift profile."""

from collections import defaultdict
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "terminal"
OUT.mkdir(parents=True, exist_ok=True)
SANS = "Arial,Helvetica,sans-serif"
MONO = "'Courier New',Courier,monospace"
THEMES = {
    "dark": {"bg":"#0b110e", "panel":"#111b15", "ink":"#ecf3e7", "muted":"#a1b19e", "line":"#34473a", "accent":"#c1f186", "amber":"#e7be71", "dim":"#1d3023", "red":"#ed8a76"},
    "light": {"bg":"#f3f5e9", "panel":"#e8eddd", "ink":"#162d20", "muted":"#506751", "line":"#bccab1", "accent":"#345d2b", "amber":"#8b5d14", "dim":"#d9e3cc", "red":"#a63a2b"},
}


def txt(x, y, value, size=18, fill=None, weight=400, mono=False, anchor="start", spacing=0, cls=""):
    family = MONO if mono else SANS
    return f'<text x="{x}" y="{y}" fill="{fill or T["ink"]}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}" class="{cls}">{escape(str(value))}</text>'


def line(x1, y1, x2, y2, stroke=None, width=1, extra=""):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{stroke or T["line"]}" stroke-width="{width}" {extra}/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{stroke or T["line"]}" stroke-width="{width}" {extra}/>'


def box(x, y, w, h, fill=None, stroke=None, radius=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill or T["panel"]}" stroke="{stroke or T["line"]}" {extra}/>'


def label(x, y, value, color=None):
    return txt(x, y, value, 13, color or T["muted"], 600, True, spacing=1.2)


def paragraph(x, y, content, size=20, step=30, color=None):
    return "".join(txt(x, y + step*i, text, size, color or T["muted"]) for i, text in enumerate(content))


def arrow(x, y, size=14, color=None):
    return f'<path d="M{x} {y+size}L{x+size} {y}M{x} {y}H{x+size}V{y+size}" fill="none" stroke="{color or T["accent"]}" stroke-width="2.5" stroke-linecap="square"/>'


def tag(x, y, text, amber=False):
    w = len(text)*8 + 24
    return box(x, y, w, 29, T["dim"], T["line"], 3) + txt(x+12, y+20, text, 12, T["amber"] if amber else T["accent"], 700, True)


def panel(name, width, height, title, description, body, theme, mobile=False, extra_defs=""):
    css = '''
      .enter{animation:enter .7s ease-out backwards}.late{animation-delay:.18s}
      .fill{transform-box:fill-box;transform-origin:left center;animation:fill .9s cubic-bezier(.2,.8,.2,1) backwards}
      .rise{transform-box:fill-box;transform-origin:center bottom;animation:rise .85s cubic-bezier(.2,.8,.2,1) backwards}
      .pulse{animation:pulse 3s ease-in-out infinite}.cursor{animation:cursor 1.4s steps(1) infinite}
      .sweep{transform-box:fill-box;transform-origin:100% 36%;animation:sweep 9s ease-in-out infinite alternate}
      .sweep-line{animation:scan 7s linear infinite}.route-dot{animation:route 8s linear infinite}
      .camera{animation:camera 16s steps(1) infinite}.camera-2{animation-delay:-12s}.camera-3{animation-delay:-8s}.camera-4{animation-delay:-4s}
      .flow{stroke-dasharray:7 14;animation:flow 3s linear infinite}.day{animation:enter .55s ease-out backwards}
      @keyframes enter{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}
      @keyframes fill{from{transform:scaleX(.02)}}@keyframes rise{from{transform:scaleY(.02)}}
      @keyframes pulse{0%,100%{opacity:1}50%{opacity:.42}}@keyframes cursor{0%,60%{opacity:1}61%,100%{opacity:0}}
      @keyframes sweep{from{transform:rotate(-16deg)}to{transform:rotate(17deg)}}
      @keyframes scan{from{transform:translateY(0)}to{transform:translateY(182px)}}
      @keyframes route{0%{transform:translate(0,0)}25%{transform:translate(110px,0)}50%{transform:translate(110px,65px)}75%{transform:translate(225px,65px)}100%{transform:translate(0,0)}}
      @keyframes camera{0%,24.9%{opacity:1}25%,100%{opacity:0}}@keyframes flow{to{stroke-dashoffset:-42}}
      @media(prefers-reduced-motion:reduce){*{animation:none!important}.camera{opacity:0}.camera-1{opacity:1}}
    '''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs><style>{css}</style>
<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{T['line']}" stroke-width=".7" opacity=".3"/></pattern>
<pattern id="check" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 0h10v10H0zM10 10h10v10H10z" fill="{T['accent']}"/><path d="M10 0h10v10H10zM0 10h10v10H0z" fill="{T['bg']}"/></pattern>
<linearGradient id="beam" x1="0" y1="1" x2="1" y2="0"><stop stop-color="{T['accent']}" stop-opacity=".22"/><stop offset="1" stop-color="{T['accent']}" stop-opacity="0"/></linearGradient>
<linearGradient id="shine"><stop stop-color="{T['accent']}" stop-opacity="0"/><stop offset=".5" stop-color="{T['accent']}" stop-opacity=".32"/><stop offset="1" stop-color="{T['accent']}" stop-opacity="0"/></linearGradient>
{extra_defs}</defs>
<rect x=".75" y=".75" width="{width-1.5}" height="{height-1.5}" rx="8" fill="{T['bg']}" stroke="{T['line']}" stroke-width="1.5"/>
{body}
</svg>'''
    (OUT / f"{name}{'-mobile' if mobile else ''}-{theme}.svg").write_text(svg)


def map_scene(x, y, w, h):
    s = w/390
    rooms = [(24,39,112,65,"01"), (166,39,112,65,"02"), (24,135,112,65,"03"), (166,135,112,65,"04")]
    body = box(0,0,390,282,T["panel"],T["line"],5)
    body += '<rect x="1" y="1" width="388" height="280" rx="5" fill="url(#grid)"/>'
    body += label(18,23,"CAMERA SYSTEM") + txt(374,23,"REC",12,T["red"],700,True,"end")
    body += '<circle cx="333" cy="19" r="3.5" fill="'+T["red"]+'" class="pulse"/>'
    body += f'<path d="M136 71H166M80 104V135M222 104V135M136 167H166M278 167H332V235H151V200" fill="none" stroke="{T["muted"]}" stroke-width="2"/>'
    for index,(rx,ry,rw,rh,number) in enumerate(rooms,1):
        body += box(rx,ry,rw,rh,T["bg"],T["line"],2)
        body += txt(rx+10,ry+24,"CAM "+number,14,T["muted"],700,True)
        active = box(rx,ry,rw,rh,T["dim"],T["accent"],2)+txt(rx+10,ry+24,"CAM "+number,14,T["accent"],700,True)
        active += f'<path d="M{rx+10} {ry+44}h{rw-20}" stroke="{T["accent"]}" stroke-width="2"/>'
        body += f'<g class="camera camera-{index}">{active}</g>'
    body += f'<path d="M316 67L284 43V91Z" fill="{T["accent"]}" opacity=".85"/>'
    body += '<polygon class="sweep" points="316,67 201,0 172,188" fill="url(#beam)"/>'
    body += box(300,49,45,36,T["bg"],T["accent"],3)
    body += f'<path d="M310 58h20v16h-20zM320 85V99M309 99h22" fill="none" stroke="{T["accent"]}" stroke-width="2"/>'
    body += '<circle cx="80" cy="71" r="3" fill="'+T["amber"]+'" class="route-dot"/>'
    body += label(20,256,"PROJECT SURVEILLANCE") + txt(370,256,"4 FEEDS",12,T["accent"],700,True,"end")
    return f'<g transform="translate({x} {y}) scale({s})">{body}</g>'


def banner(theme, mobile):
    w,h=(420,570) if mobile else (1020,408)
    b = '<g class="enter">'+label(28 if mobile else 36,35,"NIGHT SHIFT / DEVELOPER TERMINAL")
    b += txt(25 if mobile else 31,109 if mobile else 141,"MRTR4P",64 if mobile else 98,T["ink"],900,spacing=-3)
    b += txt(29 if mobile else 37,141 if mobile else 181,"OMAR ALBOSATY",17 if mobile else 19,T["accent"],600,True,spacing=2)
    b += paragraph(29 if mobile else 37,181 if mobile else 230,["Software & data engineer.","Keeping the systems alive."],20 if mobile else 25,29 if mobile else 35,T["ink"])
    b += '</g>'
    if mobile:
        b += map_scene(29,239,362,262)
        b += label(29,529,">>> SELECT A SYSTEM BELOW")
    else:
        b += map_scene(584,55,396,287)
        b += tag(37,303,"C# / TYPESCRIPT / PYTHON")
        b += label(37,370,">>> PORTFOLIO ACCESS GRANTED")
        b += txt(979,370,"SYSTEM RESTART",13,T["muted"],600,True,"end")
    b += '<rect x="1" y="'+str(h-11)+'" width="'+str(w-2)+'" height="10" fill="url(#check)" opacity=".55"/>'
    panel("banner",w,h,"MrTr4p — night shift developer terminal","Omar Albosaty, software and data engineer. An animated CCTV map cycles through four project cameras. Use the links and expandable sections below.",b,theme,mobile)


def nav(theme):
    for name,number,title in [("projects","01","CAMERAS"),("maintenance","02","SYSTEMS"),("activity","03","LOGBOOK"),("contact","04","CONTACT")]:
        b=label(17,25,number)+txt(17,53,title,19,T["accent"],800,True)+arrow(157,40,13)
        panel("nav-"+name,188,76,title,"Open "+title.lower(),b,theme)
        b=label(10,22,number)+txt(10,53,title,19,T["accent"],800,True)
        panel("nav-"+name,110,72,title,"Open "+title.lower(),b,theme,True)


def project_icon(kind,x,y):
    c=T["accent"]; m=T["line"]
    if kind==0:
        b=box(0,0,104,67,T["panel"],c,4)+line(15,86,89,86,c,3)+line(52,67,52,86,c,3)
        b+=f'<path d="M37 21L25 33L37 45M67 21L79 33L67 45M57 19L47 48" fill="none" stroke="{c}" stroke-width="2.5"/>'
        b+=f'<circle cx="88" cy="12" r="3" fill="{T["amber"]}" class="pulse"/>'
    elif kind==1:
        b=f'<path class="flow" d="M20 18H86V74H20Z" fill="none" stroke="{c}" stroke-width="2"/>'
        b+="".join(box(rx,ry,28,22,T["panel"],c,3) for rx,ry in [(4,7),(74,7),(4,65),(74,65)])
        b+=box(40,35,28,22,T["dim"],c,3)
    elif kind==2:
        b=f'<path d="M18 18H86M18 45H86M18 72H86" stroke="{m}" stroke-width="2"/>'
        b+=f'<path class="flow" d="M18 18H86V45H18V72H86" fill="none" stroke="{c}" stroke-width="2"/>'
        for rx,ry in [(8,8),(77,8),(8,35),(77,35),(8,62),(77,62)]:b+=box(rx,ry,20,20,T["panel"],c,3)
    else:
        b=box(0,0,104,86,T["panel"],c,4)+line(0,19,104,19,c)
        b+=txt(13,42,">_",20,c,700,True)+line(13,57,82,57,m,3)+line(13,70,57,70,m,3)
        b+=f'<path class="fill" d="M13 70H57" stroke="{c}" stroke-width="3"/>'
    return f'<g transform="translate({x} {y})">{b}</g>'


PROJECTS=[
    ("01","omar-arcade-portfolio",["Arcade","portfolio"],"React / TypeScript / Three.js",["An interactive home","for the things I build."],"PORTFOLIO"),
    ("02","distributed_job_execution",["Distributed","jobs"],"C#",["Distributed job execution","from the backend workshop."],"BACKEND"),
    ("03","ETL-Project",["Data","pipelines"],"Python / PostgreSQL",["Data extraction, transformation,","and orchestration."],"DATA"),
    ("04","rezero-grub-theme",["Linux","boot theme"],"Python / GRUB / Arch",["A custom boot experience","with installer and VM checks."],"LINUX"),
]


def projects(theme,mobile,data):
    for i,(number,repo,title,stack,description,category) in enumerate(PROJECTS):
        w,h=(230,350) if mobile else (500,282)
        b=label(22,32,"CAM "+number+" / "+category)+arrow(w-36,20,13)
        if mobile:
            b+=txt(21,85,title[0],29,T["ink"],800)+txt(21,122,title[1],29,T["ink"],800)
            short={0:description,1:["Distributed execution","in C#."],2:["Data transformation","and orchestration."],3:["Custom GRUB theme.","Installer & VM checks."]}[i]
            b+=paragraph(22,158,short,16,23)
            b+=project_icon(i,23,214)
            stack_mobile=["React / TS", "C#", "Python / SQL", "Arch / GRUB"][i]
            b+=txt(22,327,stack_mobile,13,T["accent"],700,True)
        else:
            b+=txt(22,94," ".join(title),34,T["ink"],800)
            b+=paragraph(22,137,description,18,27)
            b+=project_icon(i,365,149)
            b+=txt(22,248,stack,13,T["accent"],700,True)
        b+=f'<circle cx="{w-26}" cy="{h-27}" r="3" fill="{T["accent"]}" class="pulse"/>'
        panel("project-"+number,w,h,"CAM "+number+" — "+" ".join(title)," ".join(description)+" Built with "+stack+". Open the "+repo+" repository.",b,theme,mobile)


def maintenance(theme,mobile):
    w,h=(420,302) if mobile else (1020,214)
    b=label(28,35,"MAINTENANCE CONSOLE")+txt(28,80,"Keep every system running.",25 if mobile else 32,T["ink"],800)
    systems=[("BACKEND", "C# / Node.js"),("DATA", "Python / SQL"),("INTERFACES", "React / Linux")]
    for i,(name,tools) in enumerate(systems):
        x=28 if mobile else 28+i*328; y=108+i*60 if mobile else 113
        b+=label(x,y,name)+txt(x+(180 if mobile else 0),y if mobile else y+30,tools,14,T["muted"],400,True)
        bw=360 if mobile else 292
        b+=box(x,y+13 if mobile else y+45,bw,5,T["dim"],"none",2)
        b+=f'<rect x="{x}" y="{y+13 if mobile else y+45}" width="{bw}" height="5" rx="2" fill="{T["accent"]}" class="fill" style="animation-delay:{i*.2}s"/>'
    panel("maintenance",w,h,"Maintenance console — development systems","Backend, data and interface systems animate into place. Expand the corresponding maintenance sections for tools and project links.",b,theme,mobile)


def numbers(theme,mobile,data):
    days=[day for week in data["contributionsCollection"]["contributionCalendar"]["weeks"] for day in week["contributionDays"]]
    active=sum(day["contributionCount"]>0 for day in days)
    longest=current=0
    for day in days:
        current=current+1 if day["contributionCount"] else 0
        longest=max(longest,current)
    values=[(sum(d["contributionCount"] for d in days),"PUBLIC CONTRIBUTIONS"),(active,"ACTIVE DAYS"),(longest,"LONGEST STREAK / DAYS"),(data["repositories"]["totalCount"],"PUBLIC REPOSITORIES")]
    w,h=(420,254) if mobile else (1020,150)
    b=""
    for i,(value,title) in enumerate(values):
        x=25+(i%2)*204 if mobile else 30+i*250
        y=63+(i//2)*122 if mobile else 76
        b+=txt(x,y,value,44 if mobile else 51,T["accent"],800,mono=True,cls="enter")
        b+=txt(x,y+29,title,15 if mobile else 13,T["muted"],600,True)
    panel("numbers",w,h,"Public GitHub activity at a glance",", ".join(str(v)+" "+label.lower() for v,label in values)+". Calendar period only; not lifetime statistics.",b,theme,mobile)


def activity(theme,mobile,data):
    cal=data["contributionsCollection"]["contributionCalendar"]
    days=[day for week in cal["weeks"] for day in week["contributionDays"]]
    w,h=(420,508) if mobile else (1020,392)
    latest=days[-1]["date"]
    b=label(27,34,"SECURITY LOG / PUBLIC GITHUB ACTIVITY")
    b+=txt(27,79,"Every night leaves a trace.",25 if mobile else 32,T["ink"],800)
    b+=txt(27,109,"LAST 12 MONTHS / "+latest,12,T["muted"],400,True)
    cell,gap=(5.1,1.7) if mobile else (12.5,5)
    ramp=[T["dim"],"#354f34","#547b42","#8abb5d",T["accent"]] if theme=="dark" else [T["dim"],"#b7cc99","#88ac6d","#5e8547",T["accent"]]
    for wi,week in enumerate(cal["weeks"]):
        for day in week["contributionDays"]:
            weekday=(date.fromisoformat(day["date"]).weekday()+1)%7
            level=["NONE","FIRST_QUARTILE","SECOND_QUARTILE","THIRD_QUARTILE","FOURTH_QUARTILE"].index(day["contributionLevel"])
            b+=f'<rect x="{27+wi*(cell+gap):.1f}" y="{140+weekday*(cell+gap):.1f}" width="{cell}" height="{cell}" rx="1" fill="{ramp[level]}" class="day" style="animation-delay:{wi*.012:.3f}s"><title>{day["date"]}: {day["contributionCount"]} public contributions</title></rect>'
    monthly=defaultdict(int)
    for day in days:monthly[day["date"][:7]]+=day["contributionCount"]
    month_list=list(monthly.items()); maximum=max((v for _,v in month_list),default=1) or 1
    bx,by,bw,bh=(27,261,364,140) if mobile else (27,295,750,60)
    step=bw/len(month_list)
    b+=label(bx,by-15,"CONTRIBUTIONS BY MONTH")
    for i,(month,value) in enumerate(month_list):
        bar_h=max(2,value/maximum*bh)
        b+=f'<rect x="{bx+i*step:.1f}" y="{by+bh-bar_h:.1f}" width="{step-7:.1f}" height="{bar_h:.1f}" rx="2" fill="{T["accent"]}" class="rise" style="animation-delay:{i*.055}s"><title>{month}: {value} public contributions</title></rect>'
        b+=txt(bx+i*step+(step-7)/2,by+bh+21,month[5:],15,T["muted"],400,True,"middle")
    if mobile:b+=paragraph(27,459,["Open the log below for dates", "and a text version of the activity."],16,23)
    else:b+=label(812,310,"READ THE LOG")+txt(812,340,">>>",29,T["accent"],700,True,cls="cursor")
    panel("activity",w,h,"Animated contribution calendar and monthly activity","Public GitHub contribution calendar and monthly totals. Dated snapshot ending "+latest+". Expand the native log for exact dates and values.",b,theme,mobile)


def footer(theme,mobile):
    w,h=(420,193) if mobile else (1020,170)
    b=label(28,34,"06:00 AM / SHIFT COMPLETE")
    b+=txt(28,86,"Still here.",32 if mobile else 40,T["ink"],800)
    b+=txt(28,127 if mobile else 86,"Still building.",32 if mobile else 40,T["accent"],800) if mobile else txt(234,86,"Still building.",40,T["accent"],800)
    b+=label(28,163 if mobile else 132,">>> BACK TO THE CONTROL ROOM")
    if not mobile:b+=f'<circle cx="942" cy="75" r="27" fill="none" stroke="{T["line"]}" stroke-width="2"/><path d="M942 54V75M929 60a20 20 0 1 0 26 0" fill="none" stroke="{T["accent"]}" stroke-width="3" class="pulse"/>'
    b+=f'<rect x="1" y="{h-9}" width="{w-2}" height="8" fill="url(#check)" opacity=".5"/>'
    panel("footer",w,h,"Shift complete — back to the control room","Still here, still building. Click to return to the top of the profile.",b,theme,mobile)


class PublicCalendarParser(HTMLParser):
    def __init__(self):
        super().__init__();self.cells={};self.labels={};self.current=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if "data-date" in attrs:self.cells[attrs["id"]]=(attrs["data-date"],int(attrs["data-level"]))
        if tag=="tool-tip" and attrs.get("for") in self.cells:self.current=attrs["for"];self.labels[self.current]=""
    def handle_data(self,value):
        if self.current:self.labels[self.current]+=value
    def handle_endtag(self,tag):
        if tag=="tool-tip":self.current=None
    def calendar(self):
        weeks=defaultdict(list)
        levels=["NONE","FIRST_QUARTILE","SECOND_QUARTILE","THIRD_QUARTILE","FOURTH_QUARTILE"]
        for identifier,(iso,level) in sorted(self.cells.items(),key=lambda item:item[1][0]):
            label=self.labels[identifier];match=re.match(r"([\d,]+) contributions?",label)
            count=int(match[1].replace(",","")) if match else 0
            day=date.fromisoformat(iso);sunday=day-timedelta(days=(day.weekday()+1)%7)
            weeks[str(sunday)].append({"date":iso,"contributionCount":count,"contributionLevel":levels[level]})
        assert self.cells and len(self.cells)==len(self.labels),"Incomplete public calendar"
        return {"totalContributions":sum(d["contributionCount"] for week in weeks.values() for d in week),"weeks":[{"contributionDays":week} for week in weeks.values()]}


def refresh():
    account=subprocess.check_output(["gh","api","user","--jq",".login"],text=True).strip()
    if account!="MrTr4p":raise SystemExit(f"Expected local GitHub account MrTr4p, found {account}. Stopping.")
    query='{user(login:"MrTr4p"){name login url repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC){totalCount nodes{name url description stargazerCount forkCount primaryLanguage{name color}}}}}'
    data=json.loads(subprocess.check_output(["gh","api","graphql","-f",f"query={query}"],text=True))
    public_html=subprocess.check_output(["gh","api","https://github.com/users/MrTr4p/contributions"],text=True)
    parser=PublicCalendarParser();parser.feed(public_html)
    data["data"]["user"]["contributionsCollection"]={"contributionCalendar":parser.calendar()}
    data["source"]={"calendar":"https://github.com/users/MrTr4p/contributions","visibility":"public"}
    (ASSETS/"profile-data.json").write_text(json.dumps(data,indent=2)+"\n")


def picture(name, alt, width="100%", link=None):
    canonical="https://raw.githubusercontent.com/MrTr4p/MrTr4p/main/assets/terminal/"
    sources="".join(f'<source media="{media}" srcset="{canonical}{name}{suffix}.svg">' for media,suffix in [
        ("(max-width: 640px) and (prefers-color-scheme: dark)","-mobile-dark"),
        ("(max-width: 640px) and (prefers-color-scheme: light)","-mobile-light"),
        ("(prefers-color-scheme: dark)","-dark"),
        ("(prefers-color-scheme: light)","-light"),
    ])
    body=f'<picture>{sources}<img src="assets/terminal/{name}-dark.svg" alt="{escape(alt,quote=True)}" width="{width}"></picture>'
    return f'<a href="{escape(link,quote=True)}">{body}</a>' if link else body


def readme(data):
    cal=data["contributionsCollection"]["contributionCalendar"]
    days=[day for week in cal["weeks"] for day in week["contributionDays"]]
    active=[d for d in days if d["contributionCount"]]
    monthly=defaultdict(int)
    for day in days:monthly[day["date"][:7]]+=day["contributionCount"]
    pieces=[picture("banner","MrTr4p — Omar Albosaty. Software and data engineer. Animated CCTV map and night-shift developer terminal.")]
    pieces.append("".join(picture("nav-"+name,title,"24.9%",target) for name,title,target in [
        ("projects","Open camera feeds / projects","#camera-feeds"),
        ("maintenance","Open maintenance / tools","#maintenance"),
        ("activity","Open security log / activity","#security-log"),
        ("contact","Open contact links","#contact"),
    ]))
    pieces.append('''<details>
<summary><strong><code>&gt;&gt;&gt; PERSONNEL FILE / OPEN</code></strong></summary>

I'm **Omar Albosaty**, a **software & data engineer**. I build APIs, distributed systems, data pipelines, and interactive interfaces. I also make game-inspired Linux themes and experiment with machine learning.

[Portfolio](https://albosaty.dev) · [LinkedIn](https://www.linkedin.com/in/omar-riyad-7b032137b/) · [Email](mailto:omaralbosaty49@gmail.com)

</details>''')
    pieces.append("## Camera feeds\n\nSelect a feed to open its repository.")
    for start in (0,2):
        pieces.append("".join(picture("project-"+n,"CAM "+n+" — "+" ".join(title)+". "+" ".join(desc)+" Built with "+stack+". Open repository.","49.9%","https://github.com/MrTr4p/"+repo) for n,repo,title,stack,desc,_ in PROJECTS[start:start+2]))
    pieces.append('''<details>
<summary><strong><code>&gt;&gt;&gt; OPEN ADDITIONAL FEEDS</code></strong></summary>

- [Re:Zero Hyprlock](https://github.com/MrTr4p/rezero-hyprlock) — a custom Hyprland lock screen.
- [Royal Capital SDDM](https://github.com/MrTr4p/rezero-royal-capital-sddm) — an animated login theme in QML.
- [Elden Ring GRUB](https://github.com/MrTr4p/elden-erdtree-grub) — an Erdtree scene for the boot menu.
- [Machine learning notebooks](https://github.com/MrTr4p/machine-learning-college) — experiments and coursework.

[All repositories →](https://github.com/MrTr4p?tab=repositories)

</details>''')
    pieces.append("## Maintenance\n\n"+picture("maintenance","Maintenance console. Animated system checks for backend, data and interfaces. Expand a system below for its tools."))
    pieces.append('''<details>
<summary><strong><code>&gt;&gt;&gt; BACKEND SYSTEMS / EXPAND</code></strong></summary>

**C# · ASP.NET Core · Node.js · NestJS · Redis**

APIs, distributed execution, and backend services.

[Inspect distributed job execution →](https://github.com/MrTr4p/distributed_job_execution)

</details>

<details>
<summary><strong><code>&gt;&gt;&gt; DATA SYSTEMS / EXPAND</code></strong></summary>

**Python · SQL · PostgreSQL · Pandas · Airflow**

Data pipelines, transformation, orchestration, and machine learning experiments.

[Inspect ETL pipelines →](https://github.com/MrTr4p/ETL-Project) · [Open ML notebooks →](https://github.com/MrTr4p/machine-learning-college)

</details>

<details>
<summary><strong><code>&gt;&gt;&gt; INTERFACES &amp; LINUX / EXPAND</code></strong></summary>

**TypeScript · React · QML · Linux · Docker · Git**

Interactive interfaces and custom desktop, login, lock-screen, and boot experiences.

[Inspect the arcade portfolio →](https://github.com/MrTr4p/omar-arcade-portfolio) · [Open Linux themes →](https://github.com/MrTr4p/rezero-grub-theme)

</details>''')
    pieces.append("## Security log\n\n"+picture("numbers","Public GitHub activity for the calendar period: contributions, active days, longest streak and public repositories."))
    pieces.append(picture("activity","Animated public contribution calendar and monthly totals. Snapshot ending "+days[-1]["date"]+". Expand the activity log below for exact values."))
    log='''<details>
<summary><strong><code>&gt;&gt;&gt; OPEN THE ACTIVITY LOG</code></strong></summary>

Public GitHub activity from **'''+days[0]["date"]+"** to **"+days[-1]["date"]+'''**.

| Month | Contributions |
| :--- | ---: |
'''
    log+="\n".join(f'| {month} | {count} |' for month,count in monthly.items())
    log+='\n\n**Recent active days**\n\n| Date | Contributions |\n| :--- | ---: |\n'
    log+="\n".join(f'| {day["date"]} | {day["contributionCount"]} |' for day in reversed(active[-12:]))
    log+='\n\n[Open the current GitHub activity →](https://github.com/MrTr4p?tab=overview)\n\n</details>'
    pieces.append(log)
    pieces.append('''## Contact

[**PORTFOLIO ↗**](https://albosaty.dev) &nbsp; / &nbsp; [**LINKEDIN ↗**](https://www.linkedin.com/in/omar-riyad-7b032137b/) &nbsp; / &nbsp; [**EMAIL ↗**](mailto:omaralbosaty49@gmail.com)''')
    pieces.append(picture("footer","06:00 AM. Shift complete. Still here, still building. Return to the top of the profile.",link="#"))
    pieces.append('<sub>FNAF-inspired terminal theme · Original vector graphics · Motion respects your reduced-motion setting.</sub>')
    (ROOT/"README.md").write_text("\n\n".join(pieces)+"\n")


if "--refresh" in sys.argv:refresh()
data=json.loads((ASSETS/"profile-data.json").read_text())["data"]["user"]
for theme,T in THEMES.items():
    nav(theme)
    for mobile in (False,True):
        banner(theme,mobile);projects(theme,mobile,data);maintenance(theme,mobile);numbers(theme,mobile,data);activity(theme,mobile,data);footer(theme,mobile)
readme(data)
print("Built original vector terminal panels in dark, light, desktop and mobile variants.")
