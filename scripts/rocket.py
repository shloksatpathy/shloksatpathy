import math
import random

W, H = 800, 300
EARTH_CX, EARTH_CY, EARTH_R = 400, H + 1400, 1470  # large circle whose top edge is the curved horizon
PAD_X = 70
DT = 0.01
STEP = 0.05  # animation sample interval (s)
DUR = 14  # loop length (s)

G = 8  # px/s^2
IGNITION, MECO, STAGE2, SECO = 0.5, 5.5, 6.2, 11.0
PITCH_START = 2.5
FAIRING = 7.5
MAX_Q = 2.8

# time, label, label on the left of the marker
EVENTS = [
    (IGNITION, "LIFTOFF", True),
    (MAX_Q, "MAX-Q", False),
    (MECO, "MECO · STAGE SEP", False),
    (FAIRING, "FAIRING SEP", False),
    (SECO, "SECO · ORBIT", False),
]


def horizon_y(x):
    return EARTH_CY - math.sqrt(EARTH_R ** 2 - (x - EARTH_CX) ** 2)


def thrust(t):
    # Acceleration grows as each stage burns off propellant.
    if IGNITION <= t < MECO:
        return 13 / (1 - 0.5 * (t - IGNITION) / (MECO - IGNITION))
    if STAGE2 <= t < SECO:
        return 12 / (1 - 0.6 * (t - STAGE2) / (SECO - STAGE2))
    return 0


def simulate():
    x, y, v, pitch = PAD_X, horizon_y(PAD_X), 0.0, 0.0  # pitch: radians from vertical
    samples = []
    t = 0.0
    next_sample = 0.0
    while t <= DUR + 1e-9:
        if t >= next_sample - 1e-9:
            samples.append((t, x, y, pitch))
            next_sample += STEP
        if t < SECO:
            # Pitch program: hold vertical, then tip over smoothly to horizontal by SECO.
            u = min(max((t - PITCH_START) / (SECO - PITCH_START), 0), 1)
            pitch = math.radians(90) * u ** 0.7
        else:
            # Coast in orbit: turn with the horizon's curvature.
            pitch += v * DT / EARTH_R
        if t >= IGNITION:
            v += (thrust(t) - G * math.cos(pitch) * (t < SECO)) * DT
            x += v * math.sin(pitch) * DT
            y -= v * math.cos(pitch) * DT
        t += DT
    return samples


samples = simulate()
flight = [s for s in samples if s[0] >= IGNITION]
lengths = [0.0]
for a, b in zip(flight, flight[1:]):
    lengths.append(lengths[-1] + math.hypot(b[1] - a[1], b[2] - a[2]))
total = lengths[-1]


def key(t):
    return f"{t / DUR:.4f}"


def visible_between(start, end):
    # Opacity values for something shown from start to end (seconds) in each loop.
    return f'values="0;0;1;1;0;0" keyTimes="0;{key(start)};{key(start + 0.01)};{key(end)};{key(end + 0.01)};1"'


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<defs>"
    '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#0B1D3A"/><stop offset="0.75" stop-color="#14305C"/>'
    '<stop offset="1" stop-color="#2E6DB4"/></linearGradient>'
    '<radialGradient id="ground" cx="50%" cy="0%" r="100%">'
    '<stop offset="0" stop-color="#1C4A7A"/><stop offset="0.04" stop-color="#0F2A4A"/></radialGradient>'
    '<linearGradient id="flame" x1="1" y1="0" x2="0" y2="0">'
    '<stop offset="0" stop-color="#FFF4C2"/><stop offset="0.4" stop-color="#FFC94D"/>'
    '<stop offset="1" stop-color="#FF7A1F" stop-opacity="0"/></linearGradient>'
    "</defs>",
    f'<rect width="{W}" height="{H}" rx="8" fill="url(#sky)"/>',
]

random.seed(3)
for _ in range(60):
    x, y = random.uniform(0, W), random.uniform(0, H * 0.6)
    out.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.choice([0.6, 0.9])}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.2;0.8;0.2" dur="{random.uniform(2, 6):.1f}s" repeatCount="indefinite"/></circle>'
    )

# Earth and atmosphere glow along the horizon
out += [
    f'<circle cx="{EARTH_CX}" cy="{EARTH_CY}" r="{EARTH_R + 6}" fill="#4FA3E0" opacity="0.18"/>',
    f'<circle cx="{EARTH_CX}" cy="{EARTH_CY}" r="{EARTH_R}" fill="url(#ground)"/>',
]

# Launch tower
pad_y = horizon_y(PAD_X)
out += [
    f'<rect x="{PAD_X - 14}" y="{pad_y - 34:.1f}" width="4" height="34" fill="#5C6F8A"/>',
    f'<rect x="{PAD_X - 14}" y="{pad_y - 30:.1f}" width="10" height="2" fill="#5C6F8A"/>',
    f'<rect x="{PAD_X - 18}" y="{pad_y - 2:.1f}" width="36" height="3" fill="#5C6F8A"/>',
]

# Exhaust trail, drawn in behind the rocket
trail = "M" + " L".join(f"{s[1]:.1f},{s[2]:.1f}" for s in flight)
offsets = []
for s in samples:
    if s[0] < IGNITION:
        offsets.append(f"{total:.1f}")
    else:
        i = flight.index(s)
        offsets.append(f"{total - lengths[i]:.1f}")
out.append(
    f'<path d="{trail}" fill="none" stroke="#C9D6E8" stroke-opacity="0.35" stroke-width="1.5" '
    f'stroke-dasharray="{total:.1f} {total:.1f}"><animate attributeName="stroke-dashoffset" '
    f'values="{";".join(offsets)}" dur="{DUR}s" repeatCount="indefinite"/></path>'
)

# Event markers along the trajectory
for t, label, left in EVENTS:
    s = min(samples, key=lambda s: abs(s[0] - t))
    text_x, anchor = (s[1] - 6, "end") if left else (s[1] + 6, "start")
    out.append(
        f'<g opacity="0"><animate attributeName="opacity" {visible_between(t, DUR - 0.6)} '
        f'dur="{DUR}s" repeatCount="indefinite"/>'
        f'<circle cx="{s[1]:.1f}" cy="{s[2]:.1f}" r="2.5" fill="#FFD27F"/>'
        f'<text x="{text_x:.1f}" y="{s[2] - 8:.1f}" text-anchor="{anchor}" fill="#FFD27F" font-family="monospace" font-size="10">{label}</text></g>'
    )

# Rocket: drawn pointing along +x, moved along the trajectory and turned to its heading.
motion = ";".join(f"{s[1]:.2f},{s[2]:.2f}" for s in samples)
angles = ";".join(f"{math.degrees(s[3]) - 90:.2f}" for s in samples)


def flicker(start, end):
    return (
        f'<animate attributeName="opacity" {visible_between(start, end)} dur="{DUR}s" repeatCount="indefinite"/>'
        '<animateTransform attributeName="transform" type="scale" values="1 1;1.25 0.85;0.9 1.1;1 1" '
        'dur="0.15s" repeatCount="indefinite"/>'
    )


def drift(start, dx, dy, spin):
    # Moves a separated part away in the rocket's frame and fades it out.
    k0, k1 = key(start), key(min(start + 1.2, DUR - 0.1))
    return (
        f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{dx} {dy};{dx} {dy}" '
        f'keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite" additive="sum"/>'
        f'<animateTransform attributeName="transform" type="rotate" values="0;0;{spin};{spin}" '
        f'keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite" additive="sum"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite"/>'
    )


out += [
    "<g>",
    f'<animateMotion values="{motion}" calcMode="linear" dur="{DUR}s" repeatCount="indefinite"/>',
    "<g>",
    f'<animateTransform attributeName="transform" type="rotate" values="{angles}" dur="{DUR}s" repeatCount="indefinite"/>',
    '<g transform="translate(27 0)">',  # put the engine end on the trajectory point
    # first stage with its engine flame
    f"<g>{drift(MECO, -45, 12, -40)}",
    f'<g transform="translate(-27 0)"><g opacity="0">{flicker(IGNITION, MECO)}'
    '<path d="M0,-3 L-18,0 L0,3 Z" fill="url(#flame)"/></g></g>',
    '<rect x="-27" y="-3" width="19" height="6" rx="1" fill="#E6ECF5"/>',
    '<rect x="-27" y="-3" width="3" height="6" fill="#5C6F8A"/>',
    '<rect x="-12" y="-3.6" width="2" height="7.2" fill="#5C6F8A"/>',
    "</g>",
    # second stage with its engine flame
    f'<g transform="translate(-8 0)"><g opacity="0">{flicker(STAGE2, SECO)}'
    '<path d="M0,-2 L-12,0 L0,2 Z" fill="url(#flame)"/></g></g>',
    '<rect x="-8" y="-2.6" width="10" height="5.2" fill="#C9D6E8"/>',
    # fairing halves
    f'<g>{drift(FAIRING, -10, -14, -35)}<path d="M2,-2.6 L6,-2.6 Q10,-2.2 12,0 L2,0 Z" fill="#FFFFFF"/></g>',
    f'<g>{drift(FAIRING, -10, 14, 35)}<path d="M2,2.6 L6,2.6 Q10,2.2 12,0 L2,0 Z" fill="#E6ECF5"/></g>',
    # payload, exposed after fairing separation
    '<rect x="3" y="-1.6" width="5" height="3.2" fill="#FFD27F"/>',
    "</g></g></g>",
]

out += [
    f'<text x="{W - 20}" y="22" text-anchor="end" fill="#9BD4FF" font-family="monospace" font-size="11">'
    "two-stage ascent · gravity turn to orbit</text>",
    "</svg>",
]

print("\n".join(out))

