import math
import random

W, H = 800, 440
CX, CY = 400, 220
SAMPLES = 180
EARTH_R = 32
VIEW = math.radians(20)  # camera elevation above Earth's equator
FOCAL = 700  # perspective distance for the satellite scene
SPIN = 16  # seconds per Earth rotation
SPIN_FRAMES = 24  # frames per 45° of rotation (the meridian grid repeats every 45°)
BASE_A, BASE_T = 55, 3  # period of the smallest satellite orbit; others follow T^2 ∝ a^3

# Satellite scene: name, a, e, inclination, RAAN, argument of perigee (deg), color
ORBITS = [
    ("LEO", 55, 0.0, 51.6, 0, 0, "#9BD4FF"),
    ("MEO", 110, 0.15, 55, 120, 40, "#4FA3E0"),
    ("Molniya", 120, 0.7, 63.4, 200, 270, "#FFD27F"),
    ("GEO", 190, 0.0, 0, 0, 0, "#C9D6E8"),
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
SOLAR_VIEW = math.radians(25)
EARTH_T = 8
HOLD, ZOOM_END, FADE = 3, 8, 1.5  # seconds: solar view, end of zoom, satellite scene fade-in
# Everything but Earth fades out over the second half of the zoom, so only Earth is left when it arrives.
FADE_OUT = (
    f'<animate attributeName="opacity" from="1" to="0" begin="{(HOLD + ZOOM_END) / 2}s" '
    f'dur="{(ZOOM_END - HOLD) / 2}s" fill="freeze"/>'
)
FADE_IN = f'<animate attributeName="opacity" from="0" to="1" begin="{ZOOM_END}s" dur="{FADE}s" fill="freeze"/>'
ZOOM = EARTH_R / 4  # makes the intro Earth match the satellite scene Earth
STEP = 0.05


def rot_x(p, deg):
    x, y, z = p
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return x, y * c - z * s, y * s + z * c


def rot_z(p, deg):
    x, y, z = p
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return x * c - y * s, x * s + y * c, z


def project(p, elev, focal):
    # x right, y away from the camera, z up. Returns screen x, screen y, depth, perspective scale.
    x, y, z = p
    depth = y * math.cos(elev) - z * math.sin(elev)
    up = y * math.sin(elev) + z * math.cos(elev)
    k = focal / (focal + depth)
    return x * k, -up * k, depth, k


def kepler_positions(a, e):
    b = a * math.sqrt(1 - e * e)
    points = []
    for i in range(SAMPLES):
        m = 2 * math.pi * i / SAMPLES
        E = m
        for _ in range(20):
            E -= (E - e * math.sin(E) - m) / (1 - e * math.cos(E))
        points.append((a * (math.cos(E) - e), b * math.sin(E), 0))
    return points


def runs(points, closed):
    # Splits projected points into polylines that are behind (depth > 0) or in front of the centre.
    result = []
    n = len(points) if closed else len(points) - 1
    for i in range(n):
        p, q = points[i], points[(i + 1) % len(points)]
        back = p[2] + q[2] > 0
        if result and result[-1][0] == back and result[-1][1][-1] is p:
            result[-1][1].append(q)
        else:
            result.append((back, [p, q]))
    return result


def path(points):
    return "M" + " L".join(f"{CX + p[0]:.1f},{CY + p[1]:.1f}" for p in points)


def discrete(flags):
    return ";".join("1" if f else "0" for f in flags)


def satellite(color):
    return (
        f'<rect x="-9" y="-2" width="6" height="4" fill="{color}"/>'
        f'<rect x="3" y="-2" width="6" height="4" fill="{color}"/>'
        '<rect x="-3" y="-3" width="6" height="6" rx="1" fill="#FFFFFF"/>'
    )


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

# ---------- Solar system intro: tilted view, camera tracks and zooms into Earth ----------

times = [k * STEP for k in range(int(ZOOM_END / STEP) + 1)]


def planet_track(a, start):
    period = EARTH_T * (a / 100) ** 1.5
    track = []
    for t in times:
        angle = math.radians(start + 360 * t / period)
        track.append(project((a * math.cos(angle), a * math.sin(angle), 0), SOLAR_VIEW, 1e9))
    return track


earth_track = planet_track(100, 300)
scales, centers = [], []
for t, (ex, ey, _, _) in zip(times, earth_track):
    u = min(max((t - HOLD) / (ZOOM_END - HOLD), 0), 1)
    u = u * u * (3 - 2 * u)
    scales.append(f"{ZOOM ** u:.4f}")
    centers.append(f"{-ex * u:.3f},{-ey * u:.3f}")

out += [
    f'<g transform="translate({CX} {CY})"><g>',
    f'<animateTransform attributeName="transform" type="scale" values="{";".join(scales)}" dur="{ZOOM_END}s" fill="freeze"/>',
    "<g>",
    f'<animateTransform attributeName="transform" type="translate" values="{";".join(centers)}" dur="{ZOOM_END}s" fill="freeze"/>',
    f"<g>{FADE_OUT}",
]
for _, a, _, _, _ in PLANETS:
    out.append(
        f'<ellipse rx="{a}" ry="{a * math.sin(SOLAR_VIEW):.2f}" fill="none" stroke="#2E6DB4" '
        'stroke-opacity="0.35" vector-effect="non-scaling-stroke"/>'
    )
out.append("</g>")


def planet_body(name, r, color):
    if name == "Earth":
        return f'<circle r="{r * 36 / 32:.2f}" fill="#4FA3E0" opacity="0.15"/><circle r="{r}" fill="url(#earth)"/>'
    body = f'<circle r="{r}" fill="{color}"/>'
    if name == "Saturn":
        body += (
            f'<ellipse rx="{r * 2.1}" ry="{r * 2.1 * math.sin(SOLAR_VIEW):.2f}" fill="none" '
            f'stroke="{color}" stroke-width="1.2"/>'
        )
    return f"<g>{FADE_OUT}{body}</g>"


planet_layers = {True: [], False: []}
for name, a, r, color, start in PLANETS:
    track = earth_track if name == "Earth" else planet_track(a, start)
    motion = ";".join(f"{p[0]:.2f},{p[1]:.2f}" for p in track)
    for back in (True, False):
        flags = [(p[2] > 0) == back for p in track]
        planet_layers[back].append(
            f'<g><animateMotion values="{motion}" dur="{ZOOM_END}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="{discrete(flags)}" calcMode="discrete" dur="{ZOOM_END}s" fill="freeze"/>'
            f"{planet_body(name, r, color)}</g>"
        )

out += planet_layers[True]
out += [f'<g>{FADE_OUT}<circle r="34" fill="url(#sun)"/><circle r="16" fill="#FFE08A"/></g>']
out += planet_layers[False]
out += ["</g></g></g>"]

# ---------- Satellite scene: 3D orbits around a spinning Earth ----------
# Its Earth matches the zoomed-in intro Earth exactly, so it appears at once; everything else fades in.

back_layer, front_layer, legend = [], [], []
for idx, (name, a, e, inc, raan, argp, color) in enumerate(ORBITS):
    period = BASE_T * (a / BASE_A) ** 1.5
    points = [rot_z(rot_x(rot_z(p, argp), inc), raan) for p in kepler_positions(a, e)]
    proj = [project(p, VIEW, FOCAL) for p in points]

    for back, line in runs(proj, closed=True):
        (back_layer if back else front_layer).append(
            f'<path d="{path(line)}" fill="none" stroke="{color}" stroke-opacity="{0.2 if back else 0.6}" stroke-dasharray="3 4"/>'
        )

    loop = proj + [proj[0]]
    motion = ";".join(f"{CX + p[0]:.2f},{CY + p[1]:.2f}" for p in loop)
    scale = ";".join(f"{p[3]:.3f}" for p in loop)
    for back in (True, False):
        flags = [(p[2] > 0) == back for p in proj]
        (back_layer if back else front_layer).append(
            f'<g><animateMotion values="{motion}" dur="{period:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{discrete(flags)}" calcMode="discrete" dur="{period:.2f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="{scale}" dur="{period:.2f}s" repeatCount="indefinite"/>'
            f"{satellite(color)}</g></g>"
        )

    y = 26 + idx * 18
    legend.append(
        f'<rect x="20" y="{y - 8}" width="10" height="4" fill="{color}"/>'
        f'<text x="38" y="{y}" fill="{color}" font-family="monospace" font-size="11">'
        f"{name:<8} i={inc:g}° e={e:g} T={period:.1f}s</text>"
    )

# Earth: parallels are fixed, meridians turn with the spin.
grid = []
for lat in (-60, -30, 0, 30, 60):
    ring = []
    for k in range(73):
        lon = math.radians(k * 5)
        la = math.radians(lat)
        ring.append(project(
            (EARTH_R * math.cos(la) * math.cos(lon), EARTH_R * math.cos(la) * math.sin(lon), EARTH_R * math.sin(la)),
            VIEW, FOCAL,
        ))
    grid += [path(line) for back, line in runs(ring, closed=False) if not back]

frames = []
for f in range(SPIN_FRAMES):
    pieces = []
    for m in range(8):
        lon = math.radians(m * 45 + 45 * f / SPIN_FRAMES)
        meridian = []
        for k in range(13):
            la = math.radians(-90 + k * 15)
            meridian.append(project(
                (EARTH_R * math.cos(la) * math.cos(lon), EARTH_R * math.cos(la) * math.sin(lon), EARTH_R * math.sin(la)),
                VIEW, FOCAL,
            ))
        pieces += [path(line) for back, line in runs(meridian, closed=False) if not back]
    frames.append(" ".join(pieces))

out += [f'<g opacity="0">{FADE_IN}']
out += back_layer
out += [
    "</g>",
    f'<g opacity="0"><set attributeName="opacity" to="1" begin="{ZOOM_END}s"/>',
    f'<circle cx="{CX}" cy="{CY}" r="{EARTH_R + 4}" fill="#4FA3E0" opacity="0.15"/>',
    f'<circle cx="{CX}" cy="{CY}" r="{EARTH_R}" fill="url(#earth)"/>',
    "</g>",
    f'<g opacity="0">{FADE_IN}',
    f'<g fill="none" stroke="#9BD4FF" stroke-opacity="0.3" stroke-width="0.8">',
    f'<path d="{" ".join(grid)}"/>',
    f'<path d="{frames[0]}"><animate attributeName="d" values="{";".join(frames)}" calcMode="discrete" '
    f'dur="{SPIN / 8}s" repeatCount="indefinite"/></path>',
    "</g>",
]
out += front_layer
out += legend
out += [
    f'<text x="20" y="{H - 16}" fill="#9BD4FF" font-family="monospace" font-size="11">'
    "Kepler's laws: Earth at one focus · faster near perigee · T² ∝ a³</text>",
    "</g>",
    "</svg>",
]

print("\n".join(out))
