import math
import random

W, H = 800, 400
CX = 400
GROUND_Y = 360  # screen y of the pad at T-0
TRACK_RISE = 113  # how far the rocket climbs on screen before the camera locks onto it
DUR = 14
STEP = 0.05
DT = 0.005

IGNITION, FULL_THRUST, LIFTOFF = 1.0, 1.6, 3.0
MECO, SEPARATION, STAGE2, END = 9.0, 9.2, 9.9, DUR - 0.6
G = 10  # px/s^2
SCALE_HEIGHT = 100  # px, for air density
TIMES = [k * STEP for k in range(int(DUR / STEP) + 1)]


def thrust_accel(t):
    # Thrust over mass: grows as each stage burns off propellant.
    if LIFTOFF <= t < MECO:
        return 25 / (1 - 0.55 * (t - LIFTOFF) / (MECO - LIFTOFF))
    if STAGE2 <= t < END:
        return 30 / (1 - 0.5 * (t - STAGE2) / (END - STAGE2))
    return 0


def simulate():
    alt, v, t = 0.0, 0.0, 0.0
    states = {}
    k = 0
    while k < len(TIMES):
        if t >= TIMES[k] - 1e-9:
            states[k] = (alt, v)
            k += 1
        if t >= LIFTOFF:
            v += (thrust_accel(t) - G) * DT
            alt += v * DT
        t += DT
    return [states[k] for k in range(len(TIMES))]


STATES = simulate()
Q = [math.exp(-alt / SCALE_HEIGHT) * v * v for alt, v in STATES]
Q_MAX = max(Q)
MAX_Q_T = TIMES[Q.index(Q_MAX)]


def clamp(x):
    return min(max(x, 0.0), 1.0)


def ramp(t, start, end):
    return clamp((t - start) / (end - start))


def series(fn, fmt="{:.3f}"):
    return ";".join(fmt.format(fn(t, alt, v, q)) for t, (alt, v), q in zip(TIMES, STATES, Q))


def anim(attr, values, extra=""):
    return f'<animate attributeName="{attr}" values="{values}" dur="{DUR}s" repeatCount="indefinite"{extra}/>'


def anim_transform(kind, values, additive=False):
    add = ' additive="sum"' if additive else ""
    return (
        f'<animateTransform attributeName="transform" type="{kind}" values="{values}" '
        f'dur="{DUR}s" repeatCount="indefinite"{add}/>'
    )


def rise(alt):
    return min(alt, TRACK_RISE)


def stage1_on(t):
    if t < IGNITION or t >= MECO + 0.1:
        return 0.0
    if t >= MECO:
        return 1 - (t - MECO) / 0.1
    return ramp(t, IGNITION, IGNITION + 0.15)


def stage2_on(t):
    if t < STAGE2 or t >= END:
        return 0.0
    return ramp(t, STAGE2, STAGE2 + 0.25)


def engine_scale(t, alt):
    # Start-up from ignition to full thrust, then the plume widens as ambient pressure drops.
    start = 0.35 + 0.65 * ramp(t, IGNITION, FULL_THRUST)
    thin = 1 - math.exp(-alt / 400)
    return f"{start * (1 + 1.3 * thin):.3f} {start * (1 + 0.35 * thin):.3f}"


random.seed(11)
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<defs>",
    f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="8"/></clipPath>',
    '<linearGradient id="flame" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FFFFFF"/><stop offset="0.15" stop-color="#FFF1B8"/>'
    '<stop offset="0.45" stop-color="#FFB13B"/><stop offset="0.8" stop-color="#FF5E1A" stop-opacity="0.6"/>'
    '<stop offset="1" stop-color="#FF3D00" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="core" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FFFFFF"/><stop offset="0.7" stop-color="#FFF6D6"/>'
    '<stop offset="1" stop-color="#FFE08A" stop-opacity="0"/></linearGradient>',
    '<radialGradient id="glow"><stop offset="0" stop-color="#FFB347" stop-opacity="0.7"/>'
    '<stop offset="1" stop-color="#FF7A1F" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="vac" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.2" stop-color="#FFE7B0" stop-opacity="0.7"/>'
    '<stop offset="0.6" stop-color="#9BD4FF" stop-opacity="0.25"/><stop offset="1" stop-color="#9BD4FF" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="body" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#AEB9C9"/><stop offset="0.35" stop-color="#FFFFFF"/>'
    '<stop offset="1" stop-color="#8E9AAD"/></linearGradient>',
    '<linearGradient id="bell" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#3A3F4A"/><stop offset="0.4" stop-color="#8A8F99"/>'
    '<stop offset="1" stop-color="#2A2E36"/></linearGradient>',
    "</defs>",
    '<g clip-path="url(#frame)">',
    f'<rect width="{W}" height="{H}" fill="#0B1D3A"/>',
]

stars = ["<g>"]
for _ in range(70):
    stars.append(f'<circle cx="{random.uniform(0, W):.1f}" cy="{random.uniform(0, H):.1f}" r="{random.choice([0.6, 0.9, 1.2])}" fill="#FFFFFF"/>')
stars.append("</g>")
out += stars

# World: ground, pad and tower. It scrolls down once the camera tracks the rocket.
world_shift = series(lambda t, a, v, q: a - rise(a), "0,{:.2f}")
out += [f"<g>{anim_transform('translate', world_shift)}"]

out += [
    f'<rect x="0" y="{GROUND_Y}" width="{W}" height="200" fill="#2B3A4A"/>',
    f'<rect x="0" y="{GROUND_Y}" width="{W}" height="4" fill="#3E5266"/>',
    f'<rect x="{CX - 50}" y="{GROUND_Y - 4}" width="100" height="6" fill="#5C6F8A"/>',
]
# Launch tower (truss) beside the rocket
tx = CX - 46
out.append('<g stroke="#6B7C93" stroke-width="1.5" fill="none">')
out.append(f'<rect x="{tx - 14}" y="{GROUND_Y - 230}" width="14" height="230"/>')
for k in range(0, 230, 14):
    y = GROUND_Y - k
    out.append(f'<path d="M{tx - 14},{y} L{tx},{y - 14} M{tx},{y} L{tx - 14},{y - 14}"/>')
out.append(f'<path d="M{tx},{GROUND_Y - 190} L{CX - 13},{GROUND_Y - 190}"/>')
out.append("</g>")

# Flame glow on the ground
out.append(
    f'<ellipse cx="{CX}" cy="{GROUND_Y}" rx="160" ry="30" fill="url(#glow)" opacity="0">'
    f'{anim("opacity", series(lambda t, a, v, q: stage1_on(t)))}</ellipse>'
)
out.append("</g>")

# Air rushing past: streak strength follows dynamic pressure q = rho * v^2.
streaks = [f'<g stroke="#FFFFFF" stroke-width="1" opacity="0">{anim("opacity", series(lambda t, a, v, q: 0.4 * q / Q_MAX))}']
for _ in range(16):
    x = random.choice([random.uniform(60, CX - 60), random.uniform(CX + 60, W - 60)])
    length = random.uniform(30, 70)
    d = random.uniform(0.25, 0.45)
    streaks.append(
        f'<line x1="{x:.0f}" x2="{x:.0f}" y1="-80" y2="{-80 + length:.0f}">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {H + 160}" '
        f'dur="{d:.2f}s" begin="-{random.uniform(0, d):.2f}s" repeatCount="indefinite"/></line>'
    )
streaks.append("</g>")
out += streaks


def stage1_plume():
    parts = [
        f'<g opacity="0">{anim("opacity", series(lambda t, a, v, q: stage1_on(t)))}',
        f"<g>{anim_transform('scale', series(lambda t, a, v, q: engine_scale(t, a), '{}'))}",
        '<ellipse cx="0" cy="95" rx="64" ry="130" fill="url(#glow)">'
        '<animate attributeName="opacity" values="0.8;1;0.75;0.95;0.8" dur="0.2s" repeatCount="indefinite"/></ellipse>',
        # turbulent outer layer, swaying slightly
        "<g opacity=\"0.6\">"
        '<animateTransform attributeName="transform" type="rotate" values="0;2;-1.5;1;0" dur="0.35s" repeatCount="indefinite"/>'
        '<path d="M-26,0 C-38,60 -22,170 0,250 C22,170 38,60 26,0 Z" fill="url(#flame)"/></g>',
        "<g>"
        '<animateTransform attributeName="transform" type="scale" values="1 1;1.07 0.9;0.94 1.1;1.04 0.96;1 1" dur="0.12s" repeatCount="indefinite"/>'
        '<path d="M-21,0 C-29,50 -15,150 0,215 C15,150 29,50 21,0 Z" fill="url(#flame)"/></g>',
        "<g>"
        '<animateTransform attributeName="transform" type="scale" values="1 1;0.92 1.08;1.06 0.94;1 1" dur="0.09s" repeatCount="indefinite"/>'
        '<path d="M-11,0 C-13,35 -6,85 0,125 C6,85 13,35 11,0 Z" fill="url(#core)"/></g>',
    ]
    # Shock diamonds, strongest in thick air near the ground
    parts.append(f'<g fill="#FFFFFF">{anim("opacity", series(lambda t, a, v, q: 0.9 * (1 - clamp(a / 600))))}')
    for i, y in enumerate([20, 44, 66, 86]):
        s = 6 - i
        parts.append(
            f'<polygon points="0,{y - s * 1.6} {s},{y} 0,{y + s * 1.6} {-s},{y}">'
            f'<animate attributeName="opacity" values="1;0.5;0.9;0.6;1" dur="{0.1 + 0.02 * i:.2f}s" repeatCount="indefinite"/></polygon>'
        )
    parts.append("</g>")
    # Sparks streaming out of the nozzles
    for _ in range(14):
        d = random.uniform(0.35, 0.6)
        dx = random.uniform(-26, 26)
        parts.append(
            f'<circle r="{random.uniform(0.8, 1.6):.1f}" fill="#FFE08A">'
            f'<animate attributeName="cx" values="{random.uniform(-6, 6):.1f};{dx:.1f}" dur="{d:.2f}s" begin="-{random.uniform(0, d):.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="4;{random.uniform(160, 240):.0f}" dur="{d:.2f}s" begin="-{random.uniform(0, d):.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;0" dur="{d:.2f}s" begin="-{random.uniform(0, d):.2f}s" repeatCount="indefinite"/></circle>'
        )
    parts.append("</g></g>")
    return "".join(parts)


def stage2_plume():
    return (
        f'<g transform="translate(0 -100)"><g opacity="0">{anim("opacity", series(lambda t, a, v, q: stage2_on(t)))}'
        "<g>"
        '<animateTransform attributeName="transform" type="scale" values="1 1;1.05 0.95;0.96 1.05;1 1" dur="0.14s" repeatCount="indefinite"/>'
        '<path d="M-7,0 C-30,30 -62,95 -70,190 L70,190 C62,95 30,30 7,0 Z" fill="url(#vac)"/>'
        '<path d="M-4,0 C-6,20 -3,45 0,70 C3,45 6,20 4,0 Z" fill="url(#core)"/></g></g></g>'
    )


# Rocket, origin at the first-stage nozzle exits, nose pointing up.
rocket_y = series(lambda t, a, v, q: f"{CX},{GROUND_Y - rise(a):.2f}", "{}")
shake = "0 0;0.7 -0.4;-0.6 0.5;0.5 0.3;-0.7 -0.3;0 0"


def separation_offset(t):
    s = max(t - SEPARATION, 0)
    return f"0,{60 * s * s:.2f}"


out += [
    f"<g>{anim_transform('translate', rocket_y)}",
    f'<g><animateTransform attributeName="transform" type="translate" values="{shake}" dur="0.08s" repeatCount="indefinite"/>',
    # Second stage: its engine bell sits inside the interstage until separation.
    stage2_plume(),
    '<path d="M-4,-118 L4,-118 L9,-100 L-9,-100 Z" fill="url(#bell)"/>',
    '<rect x="-12" y="-160" width="24" height="42" fill="url(#body)"/>',
    '<path d="M-12,-160 L-12,-178 Q-12,-198 0,-207 Q12,-198 12,-178 L12,-160 Z" fill="url(#body)"/>',
    '<rect x="-12" y="-163" width="24" height="3" fill="#2B3A4A"/>',
    # First stage, which falls away at separation
    f"<g>{anim_transform('translate', series(lambda t, a, v, q: separation_offset(t), '{}'))}",
    f'<g>{anim("opacity", series(lambda t, a, v, q: 1 - ramp(t, 10.6, 11.6)))}',
    stage1_plume(),
    '<path d="M-11,-8 L-5,-8 L-4,0 L-12,0 Z" fill="url(#bell)"/>',
    '<path d="M-3,-8 L3,-8 L4,0 L-4,0 Z" fill="url(#bell)"/>',
    '<path d="M5,-8 L11,-8 L12,0 L4,0 Z" fill="url(#bell)"/>',
    '<rect x="-12" y="-118" width="24" height="110" fill="url(#body)"/>',
    '<rect x="-12" y="-118" width="24" height="12" fill="#1E2630"/>',
    '<rect x="-12" y="-40" width="24" height="3" fill="#2B3A4A"/>',
    '<rect x="-16" y="-104" width="4" height="7" fill="#5C6F8A"/>',
    '<rect x="12" y="-104" width="4" height="7" fill="#5C6F8A"/>',
    '<path d="M-12,-30 L-20,-8 L-12,-8 Z" fill="#8E9AAD"/>',
    '<path d="M12,-30 L20,-8 L12,-8 Z" fill="#8E9AAD"/>',
    "</g></g>",
    "</g></g>",
]

# HUD: mission clock and event readout
hud = ['<g font-family="monospace" font-size="12">']
for k in range(DUR):
    rel = k - int(LIFTOFF)
    clock = f"T{'-' if rel < 0 else '+'}00:{abs(rel):02d}"
    hud.append(
        f'<text x="20" y="28" fill="#FFFFFF" opacity="0">{clock}'
        f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{k / DUR:.4f};{(k + 1) / DUR:.4f}" '
        f'calcMode="discrete" dur="{DUR}s" repeatCount="indefinite"/></text>'
    )
events = [
    (0, "TERMINAL COUNT"),
    (IGNITION, "ENGINE IGNITION"),
    (LIFTOFF, "LIFTOFF"),
    (MAX_Q_T - 0.6, "MAX-Q"),
    (MAX_Q_T + 0.8, "PLUME EXPANDING"),
    (MECO, "MECO"),
    (SEPARATION, "STAGE SEPARATION"),
    (STAGE2, "STAGE 2 IGNITION"),
    (END, ""),
]
for (start, label), (end, _) in zip(events, events[1:]):
    hud.append(
        f'<text x="20" y="46" fill="#FFD27F" opacity="0">{label}'
        f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{start / DUR:.4f};{end / DUR:.4f}" '
        f'calcMode="discrete" dur="{DUR}s" repeatCount="indefinite"/></text>'
    )
hud.append("</g>")
out += hud

# Fade between loops
out += [
    f'<rect width="{W}" height="{H}" fill="#0B1D3A">'
    f'<animate attributeName="opacity" values="1;0;0;1" keyTimes="0;{0.4 / DUR:.4f};{(DUR - 0.5) / DUR:.4f};1" '
    f'dur="{DUR}s" repeatCount="indefinite"/></rect>',
    "</g>",
    "</svg>",
]

print("\n".join(out))
