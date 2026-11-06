import math
import random

W, H = 800, 440
CX, CY = 400, 220
SAMPLES = 180
BASE_A, BASE_T = 50, 3  # period of the smallest orbit; others follow T^2 ∝ a^3

# name, semi-major axis, eccentricity, rotation (deg), color, label position
ORBITS = [
    ("LEO", 50, 0.0, 0, "#9BD4FF", (36, -40)),
    ("MEO", 110, 0.15, 60, "#4FA3E0", (60, -110)),
    ("Molniya e=0.7", 150, 0.7, -20, "#FFD27F", (-300, -60)),
    ("GEO", 190, 0.0, 0, "#C9D6E8", (140, 150)),
]


def positions(a, e):
    b = a * math.sqrt(1 - e * e)
    points = []
    for i in range(SAMPLES):
        m = 2 * math.pi * i / SAMPLES
        E = m
        for _ in range(20):
            E -= (E - e * math.sin(E) - m) / (1 - e * math.cos(E))
        points.append((a * (math.cos(E) - e), b * math.sin(E)))
    points.append(points[0])
    return points


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><radialGradient id="earth" cx="40%" cy="35%" r="70%">'
    '<stop offset="0" stop-color="#6FC3FF"/><stop offset="0.6" stop-color="#2E6DB4"/>'
    '<stop offset="1" stop-color="#0F3566"/></radialGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="8" fill="#0B1D3A"/>',
]

random.seed(7)
for _ in range(90):
    x, y = random.uniform(0, W), random.uniform(0, H)
    r = random.choice([0.6, 0.8, 1.1])
    dur = random.uniform(2, 6)
    out.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="{dur:.1f}s" repeatCount="indefinite"/></circle>'
    )

out += [
    f'<circle cx="{CX}" cy="{CY}" r="36" fill="#4FA3E0" opacity="0.15"/>',
    f'<circle cx="{CX}" cy="{CY}" r="32" fill="url(#earth)"/>',
]

for name, a, e, rot, color, (lx, ly) in ORBITS:
    b = a * math.sqrt(1 - e * e)
    period = BASE_T * (a / BASE_A) ** 1.5
    values = ";".join(f"{x:.2f},{y:.2f}" for x, y in positions(a, e))
    out += [
        f'<g transform="translate({CX} {CY}) rotate({rot})">',
        f'<ellipse cx="{-a * e:.2f}" cy="0" rx="{a}" ry="{b:.2f}" fill="none" stroke="{color}" stroke-opacity="0.35" stroke-dasharray="3 4"/>',
        "<g>",
        f'<animateMotion values="{values}" dur="{period:.2f}s" repeatCount="indefinite"/>',
        f'<rect x="-9" y="-2" width="6" height="4" fill="{color}"/>',
        f'<rect x="3" y="-2" width="6" height="4" fill="{color}"/>',
        '<rect x="-3" y="-3" width="6" height="6" rx="1" fill="#FFFFFF"/>',
        "</g>",
        "</g>",
        f'<text x="{CX + lx}" y="{CY + ly}" fill="{color}" font-family="monospace" font-size="11">{name} · T={period:.1f}s</text>',
    ]

out += [
    f'<text x="20" y="{H - 16}" fill="#9BD4FF" font-family="monospace" font-size="11">'
    "Kepler's laws: Earth at one focus · faster near perigee · T² ∝ a³</text>",
    "</svg>",
]

print("\n".join(out))
