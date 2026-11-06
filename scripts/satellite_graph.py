import json
import os
import sys
import urllib.request

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { weekday contributionLevel } }
      }
    }
  }
}
"""

COLORS = {
    "NONE": "#16305A",
    "FIRST_QUARTILE": "#2E6DB4",
    "SECOND_QUARTILE": "#4FA3E0",
    "THIRD_QUARTILE": "#9BD4FF",
    "FOURTH_QUARTILE": "#FFFFFF",
}

CELL = 11
STEP = 14
LEFT = 20
TOP = 56
SAT_Y = 30
DUR = 10

user = sys.argv[1]
request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
)
calendar = json.load(urllib.request.urlopen(request))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"]

width = LEFT * 2 + len(weeks) * STEP - (STEP - CELL)
grid_bottom = TOP + 7 * STEP - (STEP - CELL)
height = grid_bottom + 34

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    f'<rect width="{width}" height="{height}" rx="8" fill="#0B1D3A"/>',
]

for i, week in enumerate(weeks):
    x = LEFT + i * STEP
    t = (x + CELL / 2 + 40) / (width + 80)
    lit = []
    for day in week["contributionDays"]:
        y = TOP + day["weekday"] * STEP
        level = day["contributionLevel"]
        rect = f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLORS[level]}"/>'
        if level == "NONE":
            out.append(rect)
        else:
            lit.append(rect)
    if lit:
        out.append(
            f'<g opacity="0.25"><animate attributeName="opacity" values="0.25;0.25;1;1" '
            f'keyTimes="0;{t:.4f};{t + 0.01:.4f};1" dur="{DUR}s" repeatCount="indefinite"/>'
        )
        out.extend(lit)
        out.append("</g>")

beam = grid_bottom - SAT_Y
out += [
    "<g>",
    f'<animateTransform attributeName="transform" type="translate" values="-40 {SAT_Y};{width + 40} {SAT_Y}" dur="{DUR}s" repeatCount="indefinite"/>',
    f'<polygon points="-4,6 4,6 14,{beam} -14,{beam}" fill="#9BD4FF" opacity="0.15"/>',
    '<rect x="-22" y="-3" width="14" height="6" fill="#4FA3E0"/>',
    '<rect x="8" y="-3" width="14" height="6" fill="#4FA3E0"/>',
    '<rect x="-6" y="-5" width="12" height="10" rx="1" fill="#C9D6E8"/>',
    '<line x1="0" y1="-5" x2="0" y2="-11" stroke="#C9D6E8" stroke-width="1.5"/>',
    "</g>",
    f'<text x="{LEFT}" y="{height - 12}" fill="#9BD4FF" font-family="monospace" font-size="11">'
    f'{calendar["totalContributions"]} contributions in the last year</text>',
    "</svg>",
]

print("\n".join(out))
