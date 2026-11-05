"""
make_cards.py: draws the three GitHub stats cards for the profile README.

It reads the numbers straight from GitHub (no third-party card services, which
block GitHub's servers) and writes three SVG pictures:
    stats.svg       stars, contributions, PRs, issues, repos
    top-langs.svg   most used languages across my repositories
    streak.svg      total contributions, current streak, longest streak

Run by .github/workflows/snake.yml every day. To try it on your own computer:
    python .github/scripts/make_cards.py out
Only uses Python's standard library, so there's nothing to install.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from html import escape

USER = os.environ.get("CARD_USER", "ryuma33")
NAME = "Althaf Nezam Rawther"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else "dist"

# "radical"-style colours, matching the profile's pink/purple theme
BG, BORDER, TITLE, TEXT, ICON, DIM, RING = "#141321", "#2a2140", "#fe428e", "#a9fef7", "#f8d847", "#8b8aa8", "#fe428e"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"
LANG_COLORS = {"Python": "#3572A5", "HTML": "#e34c26", "JavaScript": "#f1e05a", "C++": "#f34b7d", "CSS": "#663399",
               "C": "#555555", "Java": "#b07219", "TypeScript": "#3178c6", "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051"}


# ---------------------------------------------------------------- fetching data
def get(url, data=None):
    headers = {"User-Agent": "profile-cards", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8")
    return json.loads(body) if "api.github.com" in url else body


def contribution_days():
    """Daily contribution counts for the last year: {date: count}."""
    if TOKEN:  # official API (used inside GitHub Actions)
        q = {"query": "query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
             "variables": {"l": USER}}
        try:
            j = get("https://api.github.com/graphql", json.dumps(q).encode())
            weeks = j["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            return {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}
        except Exception as e:  # fall back to the public calendar page
            print("GraphQL failed, using public calendar:", e)
    html = get(f"https://github.com/users/{USER}/contributions")
    dates = dict(re.findall(r'data-date="([\d-]+)"\s+id="([^"]+)"', html))
    dates = {v: k for k, v in dates.items()}  # id -> date
    days = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        if cid in dates:
            m = re.match(r"(\d+) contribution", text)
            days[dates[cid]] = int(m.group(1)) if m else 0
    return days


def repo_stats():
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = {}
    for r in own:
        if r["name"].lower() == USER.lower():
            continue  # skip the profile repo itself (just a README + GIF script)
        for lang, size in get(r["languages_url"]).items():
            langs[lang] = langs.get(lang, 0) + size
    return stars, len(own), langs


def search_count(q):
    try:
        return get(f"https://api.github.com/search/issues?q={q}&per_page=1")["total_count"]
    except Exception:
        return 0


# ---------------------------------------------------------------- drawing
def card(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title>'
            f'<style>text{{font-family:{FONT}}} .t{{font-size:18px;font-weight:600;fill:{TITLE}}} .l{{font-size:14px;font-weight:600;fill:{TEXT}}}'
            f' .v{{font-size:14px;font-weight:700;fill:{TEXT}}} .s{{font-size:12px;fill:{DIM}}} .big{{font-size:28px;font-weight:700;fill:{TEXT}}}'
            f' .fade{{opacity:0;animation:f .6s ease forwards}} @keyframes f{{to{{opacity:1}}}}</style>'
            f'<rect x="0.5" y="0.5" rx="6" width="{w-1}" height="{h-1}" fill="{BG}" stroke="{BORDER}"/>{body}</svg>')


ICONS = {  # 16px icons
    "star": '<path d="M8 .8l2.2 4.6 5 .7-3.6 3.5.9 5L8 12.2l-4.5 2.4.9-5L.8 6.1l5-.7z"/>',
    "commit": '<circle cx="8" cy="8" r="3" fill="none" stroke-width="1.6"/><path d="M0 8h5M11 8h5" stroke-width="1.6"/>',
    "pr": '<circle cx="4" cy="3" r="2" fill="none" stroke-width="1.5"/><circle cx="4" cy="13" r="2" fill="none" stroke-width="1.5"/><circle cx="12" cy="13" r="2" fill="none" stroke-width="1.5"/><path d="M4 5v6M12 11V6a2 2 0 0 0-2-2H7" fill="none" stroke-width="1.5"/>',
    "issue": '<circle cx="8" cy="8" r="6.5" fill="none" stroke-width="1.5"/><circle cx="8" cy="8" r="1.5"/>',
    "repo": '<path d="M3 1.5h10v11H4.5A1.5 1.5 0 0 0 3 14zM3 14a1.5 1.5 0 0 0 1.5 1.5H13v-3" fill="none" stroke-width="1.5"/>',
}


def icon(name, x, y):
    return f'<g transform="translate({x},{y})" fill="{ICON}" stroke="{ICON}">{ICONS[name]}</g>'


def stats_card(stars, contribs, prs, issues, repos):
    rows = [("star", "Total Stars Earned:", stars), ("commit", "Contributions (last year):", contribs),
            ("pr", "Total PRs:", prs), ("issue", "Total Issues:", issues), ("repo", "Public Repositories:", repos)]
    body = f'<text x="25" y="35" class="t">{escape(NAME)}\'s GitHub Stats</text>'
    for i, (ic, label, val) in enumerate(rows):
        y = 70 + i * 25
        body += f'<g class="fade" style="animation-delay:{150 + i * 150}ms">{icon(ic, 25, y - 12)}<text x="50" y="{y}" class="l">{label}</text><text x="230" y="{y}" class="v">{val}</text></g>'
    # ring with total contributions
    body += (f'<circle cx="390" cy="105" r="40" fill="none" stroke="{RING}" stroke-opacity=".2" stroke-width="6"/>'
             f'<circle cx="390" cy="105" r="40" fill="none" stroke="{RING}" stroke-width="6" stroke-linecap="round" stroke-dasharray="251" stroke-dashoffset="{251 - min(251, 251 * contribs / 365):.0f}" transform="rotate(-90 390 105)"/>'
             f'<text x="390" y="112" text-anchor="middle" class="big">{contribs}</text><text x="390" y="165" text-anchor="middle" class="s">contributions</text>')
    return card(467, 195, "GitHub stats", body)


def langs_card(langs):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    body = '<text x="25" y="35" class="t">Most Used Languages</text><mask id="m"><rect x="25" y="55" width="300" height="8" rx="4" fill="#fff"/></mask>'
    x = 25.0
    for lang, size in top:
        w = 300 * size / total
        body += f'<rect mask="url(#m)" x="{x:.1f}" y="55" width="{w + 0.5:.1f}" height="8" fill="{LANG_COLORS.get(lang, "#858585")}"/>'
        x += w
    for i, (lang, size) in enumerate(top):
        cx, cy = 25 + (i % 2) * 150, 90 + (i // 2) * 25
        body += (f'<g class="fade" style="animation-delay:{150 + i * 120}ms"><circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(lang, "#858585")}"/>'
                 f'<text x="{cx + 16}" y="{cy}" class="s" style="fill:{TEXT}">{escape(lang)} {100 * size / total:.2f}%</text></g>')
    return card(350, 165, "Most used languages", body)


def streaks(days):
    ds = sorted(days)
    longest = run = 0
    longest_rng, start = ("", ""), None
    for d in ds:
        if days[d] > 0:
            run += 1
            start = start or d
            if run > longest:
                longest, longest_rng = run, (start, d)
        else:
            run, start = 0, None
    # current streak: count back from today (today may still be 0 without breaking it)
    cur, end, i = 0, None, len(ds) - 1
    if i >= 0 and days[ds[i]] == 0:
        i -= 1
    while i >= 0 and days[ds[i]] > 0:
        cur += 1
        end = end or ds[i]
        i -= 1
    cur_rng = (ds[i + 1], end) if cur else ("", "")
    return cur, cur_rng, longest, longest_rng


def fmt(d):
    return dt.date.fromisoformat(d).strftime("%b %-d" if os.name != "nt" else "%b %#d") if d else ""


def streak_card(days):
    total = sum(days.values())
    cur, cur_rng, longest, lr = streaks(days)
    ds = sorted(days)
    first = f"{fmt(ds[0])}, {ds[0][:4]}" if ds else ""
    rng = lambda r: f"{fmt(r[0])} - {fmt(r[1])}" if r[0] else "No streak yet"
    body = (f'<line x1="166" y1="28" x2="166" y2="170" stroke="{BORDER}"/><line x1="329" y1="28" x2="329" y2="170" stroke="{BORDER}"/>'
            f'<g class="fade" style="animation-delay:100ms"><text x="83" y="90" text-anchor="middle" class="big" style="fill:{TITLE}">{total}</text>'
            f'<text x="83" y="125" text-anchor="middle" class="l">Total Contributions</text><text x="83" y="148" text-anchor="middle" class="s">{first} - Present</text></g>'
            f'<g class="fade" style="animation-delay:300ms"><circle cx="247.5" cy="71" r="40" fill="none" stroke="{RING}" stroke-width="5"/>'
            f'<path transform="translate(237 18)" d="M10 0c2 6 10 8 10 17a10 10 0 0 1-20 0c0-5 3-7 4-10 1 3 2 4 4 4-1-4 0-8 2-11z" fill="{ICON}" stroke="{BG}" stroke-width="3"/>'
            f'<text x="247.5" y="82" text-anchor="middle" class="big">{cur}</text>'
            f'<text x="247.5" y="140" text-anchor="middle" class="l" style="fill:{ICON}">Current Streak</text><text x="247.5" y="160" text-anchor="middle" class="s">{rng(cur_rng)}</text></g>'
            f'<g class="fade" style="animation-delay:500ms"><text x="411" y="90" text-anchor="middle" class="big" style="fill:{TITLE}">{longest}</text>'
            f'<text x="411" y="125" text-anchor="middle" class="l">Longest Streak</text><text x="411" y="148" text-anchor="middle" class="s">{rng(lr)}</text></g>')
    return card(495, 195, "GitHub streak", body)


def main():
    os.makedirs(OUT, exist_ok=True)
    days = contribution_days()
    stars, nrepos, langs = repo_stats()
    prs = search_count(f"author:{USER}+type:pr")
    issues = search_count(f"author:{USER}+type:issue")
    files = {"stats.svg": stats_card(stars, sum(days.values()), prs, issues, nrepos),
             "top-langs.svg": langs_card(langs), "streak.svg": streak_card(days)}
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("saved", name)


if __name__ == "__main__":
    main()
