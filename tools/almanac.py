"""Prototype of the weather tile's sky math, using only what OWL has (sin cos atan2 sqrt rad deg %).

Prints the sun's and moon's rise and set and the moon's phase for a place and day, to check against any almanac:
  python3 tools/almanac.py LAT LON [YYYY-MM-DD [UTC_OFFSET_HOURS]]
"""
import calendar
import sys
import time
from math import sin, cos, atan2, sqrt, radians as rad, degrees as deg


def asin(x):
    return atan2(x, sqrt(max(0.0, 1 - x * x)))


def sky(t, lat, lon):
    """Alt/az (degrees, az from north clockwise) of sun and moon, and the moon's elongation."""
    d = t / 86400 - 10957.5  # days since J2000.0
    eps = rad(23.439)
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    # The sun: mean anomaly and ecliptic longitude.
    g = rad(357.529 + 0.98560028 * d)
    sun_lon = 280.459 + 0.98564736 * d + 1.915 * sin(g) + 0.020 * sin(2 * g)
    # The moon: mean longitude, anomaly, elongation and argument of latitude, plus the big terms.
    L = 218.316 + 13.176396 * d
    M = rad(134.963 + 13.064993 * d)
    D = rad(297.850 + 12.190749 * d)
    F = rad(93.272 + 13.229350 * d)
    moon_lon = L + 6.289 * sin(M) + 1.274 * sin(2 * D - M) + 0.658 * sin(2 * D) - 0.186 * sin(g) - 0.059 * sin(2 * D - 2 * M) - 0.057 * sin(2 * D - M - g)
    moon_lat = 5.128 * sin(F)
    out = {}
    for name, lam, beta in (("sun", sun_lon, 0.0), ("moon", moon_lon, moon_lat)):
        lr, br = rad(lam), rad(beta)
        ra = deg(atan2(sin(lr) * cos(eps) - (sin(br) / cos(br)) * sin(eps), cos(lr)))
        dec = asin(sin(br) * cos(eps) + cos(br) * sin(eps) * sin(lr))
        h = rad(gmst + lon - ra)
        phi = rad(lat)
        alt = deg(asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(h)))
        az = (deg(atan2(-cos(dec) * sin(h), sin(dec) * cos(phi) - cos(dec) * cos(h) * sin(phi))) + 360) % 360
        out[name] = (alt, az)
    elong = ((moon_lon - sun_lon) % 360 + 360) % 360
    out["elong"] = elong
    out["illum"] = (1 - cos(rad(elong))) / 2
    return out


def crossings(day_utc0, lat, lon, body, h0, tz=0):
    """Local times (UTC+tz) when body's altitude crosses h0, minute by minute over the local day."""
    res = []
    prev = None
    for m in range(0, 1441):
        t = day_utc0 - tz * 3600 + m * 60
        alt = sky(t, lat, lon)[body][0]
        if prev is not None and (prev < h0) != (alt < h0):
            res.append(("rise" if alt > prev else "set", "%02d:%02d" % divmod(m, 60)))
        prev = alt
    return res


if __name__ == "__main__":
    lat, lon = float(sys.argv[1]), float(sys.argv[2])
    day = sys.argv[3] if len(sys.argv) > 3 else time.strftime("%Y-%m-%d", time.gmtime())
    tz = float(sys.argv[4]) if len(sys.argv) > 4 else 0
    day0 = calendar.timegm(tuple(map(int, day.split("-"))) + (0, 0, 0))
    print("%s, UTC%+g" % (day, tz))
    print("sun: ", crossings(day0, lat, lon, "sun", -0.833, tz))
    # The moon's parallax (~0.95 deg) lifts the apparent horizon test to about +0.125 deg.
    print("moon:", crossings(day0, lat, lon, "moon", 0.125, tz))
    s = sky(day0 + 12 * 3600, lat, lon)
    print("noon UTC: sun alt %.1f az %.1f | moon alt %.1f az %.1f | elongation %.0f, %.0f%% lit" % (
        *s["sun"], *s["moon"], s["elong"], s["illum"] * 100))
