import math
import random

W, H = 800, 440
CX, CY = 400, 220
SAMPLES = 180
BASE_A, BASE_T = 50, 3  # period of the smallest satellite orbit; others follow T^2 ∝ a^3

# Satellite scene: name, semi-major axis, eccentricity, rotation (deg), color, label position
ORBITS = [
    ("LEO", 50, 0.0, 0, "#9BD4FF", (36, -40)),
    ("MEO", 110, 0.15, 60, "#4FA3E0", (60, -110)),
    ("Molniya e=0.7", 150, 0.7, -20, "#FFD27F", (-300, -60)),
    ("GEO", 190, 0.0, 0, "#C9D6E8", (140, 150)),
]

# Solar system intro: name, orbit radius, planet radius, color, start angle (deg)
PLANETS = [
    ("Mercury", 45, 2, "#B8B0A8", 200),
    ("Venus", 70, 3.2, "#E8C78A", 80),
    ("Earth", 100, 4, None, 300),
    ("Mars", 135, 2.6, "#D9714E", 20),
    ("Jupiter", 175, 9, "#D8B48A", 140),
    ("Saturn", 210, 7.5, "#E6D29C", 250),
]
EARTH_A, EARTH_R, EARTH_T, EARTH_START = 100, 4, 8, 300
HOLD, ZOOM_END, FADE = 4, 7, 1  # seconds: solar view, end of zoom, crossfade length
ZOOM = 32 / EARTH_R  # makes the intro Earth match the satellite scene Earth
STEP = 0.05


def kepler_positions(a, e):
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


def earth_at(t):
    angle = math.radians(EARTH_START + 360 * t / EARTH_T)
    return EARTH_A * math.cos(angle), EARTH_A * math.sin(angle)


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs>'
    '<radialGradient id="earth" cx="40%" cy="35%" r="70%">'
    '<stop offset="0" stop-color="#6FC3FF"/><stop offset="0.6" stop-color="#2E6DB4"/>'
    '<stop offset="1" stop-color="#0F3566"/></radialGradient>'
    '<radialGradient id="sun"><stop offset="0" stop-color="#FFF4C2"/><stop offset="0.5" stop-color="#FFC94D"/>'
    '<stop offset="1" stop-color="#FF9A1F" stop-opacity="0"/></radialGradient>'
    '</defs>',
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

# Solar system intro. The camera tracks Earth and zooms in on it.
scales, centers = [], []
for k in range(int(ZOOM_END / STEP) + 1):
    t = k * STEP
    u = min(max((t - HOLD) / (ZOOM_END - HOLD), 0), 1)
    u = u * u * (3 - 2 * u)
    ex, ey = earth_at(t)
    scales.append(f"{ZOOM ** u:.4f}")
    centers.append(f"{-ex * u:.3f},{-ey * u:.3f}")

out += [
    f'<g><animate attributeName="opacity" from="1" to="0" begin="{ZOOM_END}s" dur="{FADE}s" fill="freeze"/>',
    f'<g transform="translate({CX} {CY})"><g>',
    f'<animateTransform attributeName="transform" type="scale" values="{";".join(scales)}" dur="{ZOOM_END}s" fill="freeze"/>',
    "<g>",
    f'<animateTransform attributeName="transform" type="translate" values="{";".join(centers)}" dur="{ZOOM_END}s" fill="freeze"/>',
    '<circle r="34" fill="url(#sun)"/>',
    '<circle r="16" fill="#FFE08A"/>',
]
for name, a, r, color, start in PLANETS:
    period = EARTH_T * (a / EARTH_A) ** 1.5
    out.append(f'<circle r="{a}" fill="none" stroke="#2E6DB4" stroke-opacity="0.35" vector-effect="non-scaling-stroke"/>')
    out.append(
        f'<g transform="rotate({start})"><animateTransform attributeName="transform" type="rotate" '
        f'from="{start}" to="{start + 360 * ZOOM_END / period:.3f}" dur="{ZOOM_END}s" fill="freeze"/>'
    )
    if name == "Earth":
        out.append(f'<circle cx="{a}" r="{r * 36 / 32:.2f}" fill="#4FA3E0" opacity="0.15"/>')
        out.append(f'<circle cx="{a}" r="{r}" fill="url(#earth)"/>')
    else:
        out.append(f'<circle cx="{a}" r="{r}" fill="{color}"/>')
    if name == "Saturn":
        out.append(f'<ellipse cx="{a}" rx="{r * 1.9}" ry="{r * 0.5}" fill="none" stroke="{color}" stroke-width="1.2"/>')
    out.append("</g>")
out += ["</g></g></g></g>"]

# Satellite scene, faded in once the camera reaches Earth.
out += [
    f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{ZOOM_END}s" dur="{FADE}s" fill="freeze"/>',
    f'<circle cx="{CX}" cy="{CY}" r="36" fill="#4FA3E0" opacity="0.15"/>',
    f'<circle cx="{CX}" cy="{CY}" r="32" fill="url(#earth)"/>',
]
for name, a, e, rot, color, (lx, ly) in ORBITS:
    b = a * math.sqrt(1 - e * e)
    period = BASE_T * (a / BASE_A) ** 1.5
    values = ";".join(f"{x:.2f},{y:.2f}" for x, y in kepler_positions(a, e))
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
    "</g>",
    "</svg>",
]

print("\n".join(out))
