# omalauncher-widgets

Two home-screen widgets for [omalauncher](https://github.com/SimonSchubert/omalauncher), the Omarchy-themed Android
launcher, written in its OWL language, with the tools used to make them. Both began as the launcher's bundled
`10-today.owl` and `20-fetch.owl` and were redrawn as dot-matrix displays.

| Widget | |
|---|---|
| `widgets/10-today.owl` | The date and the weather. The tile has a split-flap date and a live sky, with the sun and moon where they really are. Its full screen has a place search (forgiving of typos), the conditions, hourly charts, five days, sun and moon times, and Pierrot on the moon, whose scene follows the moon's phase |
| `widgets/20-fetch.owl` | The phone's vitals (CPU, memory, storage, temperature) with Pix, a pixel mascot whose mood follows them and who puts on headphones while audio plays. Its full screen lists the phone, hardware, battery, launcher and Linux, fastfetch style |

## Install

1. Copy the files in `widgets/` to `~/.config/omalauncher/widgets/` in the launcher's Linux. They replace the bundled
   widgets of the same name.
2. Pix knows when audio is playing only once the launcher has notification access (Android settings, Notification
   access).

The weather follows you by your IP address, which can be a town or two off, or shows a place you pick on its full
screen. Widgets can't read the phone's GPS yet; omalauncher
[issue #31](https://github.com/SimonSchubert/omalauncher/issues/31) asks for that.

## Data

- Weather: [wttr.in](https://wttr.in), and [Open-Meteo](https://open-meteo.com) (CC BY 4.0) for the hourly forecast
  and days four and five.
- Place names and the place search: © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors (ODbL),
  through Nominatim and komoot's [Photon](https://photon.komoot.io).
- Rough location from your IP address: [ipinfo.io](https://ipinfo.io).

These are free public services, so go easy on them. OWL can't refresh a single source, so a place search refreshes
all of the weather's sources each time typing pauses.

## Tools

| | |
|---|---|
| `tools/wxfont.py` | The widgets' 3x5 pixel font as an OWL map. A character missing from it draws as a checker, so add new glyphs here |
| `tools/almanac.py` | The sky math the weather uses, in Python: `python3 tools/almanac.py LAT LON [YYYY-MM-DD [UTC_OFFSET]]` prints the sun's and moon's rise and set and the moon's phase, to check against any almanac |
| `previews/pierrot/` | Renders Pierrot's moon scenes frame by frame: `python3 poses.py [pose] [times...]`, `python3 fish.py` |
| `previews/pix/preview.py` | Renders Pix with headphone variants: `python3 previews/pix/preview.py out/pix.png` |
| `tools/push.sh` | Installs a widget on a phone from a computer (below) |

The previews mirror the widgets' drawing code; the widgets are the source of truth, so keep the two in step when
changing an animation. They need Pillow and ImageMagick.

## Installing from a computer

`tools/push.sh` sends a widget to the phone over a network both are on (Tailscale works well) and installs it through
the launcher's terminal, without adb:

1. Copy `local.env.example` to `local.env` and fill in the two addresses.
2. Run `tools/push.sh widgets/10-today.owl`.
3. In the launcher's terminal on the phone, type the line it prints (`bash < /dev/tcp/<computer>/8769`).

The phone replaces its copy only if that's still the last committed version (or a checksum given as a second
argument), rolls back if `owl-check` says the new one doesn't compile, and reports back with the screen preview in
`out/`. `tools/check-public.sh`, as a pre-commit hook, keeps the addresses and any `PRIVATE_WORDS` in `local.env` out
of commits.

## License

MIT, see [LICENSE](LICENSE). The widgets build on the launcher's bundled widgets, © Simon Schubert and contributors.
