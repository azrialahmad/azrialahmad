"""Generate the GitHub headers from the portfolio's design tokens.

Run: uv run --with fonttools python scripts/generate-banners.py
Fonts are downloaded into a temporary directory, then converted to SVG paths
so GitHub doesn't need to load fonts, stylesheets, or third-party images.
"""

from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
FONTS = {
    "display": "https://fonts.gstatic.com/s/cormorantgaramond/v21/co3smX5slCNuHLi8bLeY9MK7whWMhyjYrGFEsdtdc62E6zd5rDDOjw.ttf",
    "body": "https://fonts.gstatic.com/s/dmsans/v17/rP2tp2ywxg089UriI5-g4vlH9VoD8CmcqZG40F9JadbnoEwAopxhTg.ttf",
}


def oklch(lightness, chroma, hue):
    """Convert the portfolio's OKLCH tokens to universally supported sRGB."""
    from math import cos, radians, sin

    a, b = chroma * cos(radians(hue)), chroma * sin(radians(hue))
    l = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    linear = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

    def channel(value):
        value = 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055
        return round(max(0, min(1, value)) * 255)

    return "#" + "".join(f"{channel(value):02x}" for value in linear)


PALETTES = {
    "light": {
        "bg": oklch(0.97, 0.01, 90),
        "ink": oklch(0.22, 0.04, 265),
        "muted": oklch(0.48, 0.05, 265),
        "accent": oklch(0.52, 0.22, 265),
        "border": oklch(0.87, 0.03, 265),
    },
    "dark": {
        "bg": oklch(0.16, 0.04, 265),
        "ink": oklch(0.92, 0.02, 90),
        "muted": oklch(0.65, 0.05, 265),
        "accent": oklch(0.66, 0.18, 265),
        "border": oklch(0.28, 0.06, 265),
    },
}


def lettering(font, text, x, y, size, color, tracking=0):
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    cursor = 0
    paths = []
    for char in text:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        commands = pen.getCommands()
        if commands:
            paths.append(f'<path transform="translate({cursor:.2f} 0)" d="{commands}"/>')
        cursor += glyphs[name].width + tracking / scale
    return (
        f'<g aria-label="{escape(text, quote=True)}" fill="{color}" '
        f'transform="translate({x} {y}) scale({scale:.6f} {-scale:.6f})">'
        + "".join(paths)
        + "</g>"
    )


def banner(fonts, colors):
    bg, ink, muted, accent, border = (colors[key] for key in ("bg", "ink", "muted", "accent", "border"))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440" role="img" aria-labelledby="title description">',
        '<title id="title">Azrial Ahmad Haidar — Software, AI and Data</title>',
        '<desc id="description">An editorial header in the portfolio’s cream and cobalt palette. Curious by nature, precise by practice. Based in Yogyakarta, Indonesia.</desc>',
        f'<rect width="1200" height="440" fill="{bg}"/>',
        f'<path d="M64 52H96" stroke="{accent}" stroke-width="1.5"/>',
        lettering(fonts["body"], "ENGINEERING & EXPERIMENTS", 110, 57, 15, accent, 2.3),
        lettering(fonts["display"], "Azrial", 58, 180, 132, ink),
        lettering(fonts["display"], "Ahmad Haidar", 58, 291, 132, accent),
        f'<path d="M64 328H1136" stroke="{border}"/>',
        lettering(fonts["body"], "SOFTWARE, AI & DATA", 64, 366, 17, ink, 1.8),
        lettering(fonts["body"], "Curious by nature. Precise by practice.", 64, 404, 19, muted),
        lettering(fonts["body"], "YOGYAKARTA, INDONESIA", 848, 366, 14, muted, 1.4),
        # An open-ended idea / explore / build / learn motif, styled as a technical drawing.
        f'<g fill="none" stroke="{accent}" stroke-width="1.2">',
        '<path d="M866 94H1014V270H866Z" opacity="0.18"/>',
        '<path d="M828 132H976V232H828Z" opacity="0.3"/>',
        '<path d="M794 166H1104M944 86V282" opacity="0.3"/>',
        '<path d="M882 166H1012V226H1056"/>',
        '<path d="M1012 166V116H1056"/>',
        '<path d="M1050 110L1056 116L1050 122M1050 220L1056 226L1050 232"/>',
        '</g>',
        f'<circle cx="882" cy="166" r="7" fill="{bg}" stroke="{accent}" stroke-width="1.5"/>',
        f'<circle cx="1012" cy="166" r="5" fill="{accent}"/>',
        lettering(fonts["body"], "IDEA", 837, 199, 11, muted, 1.4),
        lettering(fonts["body"], "EXPLORE", 971, 195, 11, muted, 1.4),
        lettering(fonts["body"], "BUILD", 1066, 121, 11, muted, 1.4),
        lettering(fonts["body"], "LEARN", 1052, 252, 11, muted, 1.4),
    ]
    for index, offset in enumerate((6, 3, 1, 0, 0, 1, 3, 6, 10, 14)):
        parts.append(f'<circle cx="{1024 + index * 11}" cy="{389 + offset}" r="2.8" fill="{accent}" opacity="0.65"/>')
    return "\n".join(parts) + "\n</svg>\n"


def main():
    output = ROOT / "assets"
    output.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="azrial-profile-fonts-") as temporary:
        fonts = {}
        for name, url in FONTS.items():
            path = Path(temporary) / f"{name}.ttf"
            urlretrieve(url, path)
            fonts[name] = TTFont(path)
        for theme, colors in PALETTES.items():
            path = output / f"banner-{theme}.svg"
            path.write_text(banner(fonts, colors))
            print(f"Generated {path.name}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
