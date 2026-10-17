#!/usr/bin/env python3
"""
Generate an ultra-crisp, high-impact 1200x630 OpenGraph / Twitter preview card for InternScan.
Saved to docs/og-image.png (Clean modern dark theme with verified global multi-region support).
"""
import os
from PIL import Image, ImageDraw, ImageFont

def draw_star(draw, center_x, center_y, radius, fill):
    import math
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = i * math.pi / 5 - math.pi / 2
        points.append((center_x + r * math.cos(angle), center_y + r * math.sin(angle)))
    draw.polygon(points, fill=fill)

def generate():
    width = 1200
    height = 630

    # Deep sleek slate background: #07090e
    img = Image.new("RGBA", (width, height), (7, 9, 14, 255))

    # 1. Elegant ambient mesh glow (Warm Amber top-left + Electric Blue bottom-right + Violet core)
    glow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)

    # Warm Amber glow (top-left)
    center_x, center_y = 360, -40
    for r in range(540, 0, -6):
        alpha = int(40 * (1 - r / 540))
        glow_draw.ellipse(
            (center_x - r * 1.5, center_y - r, center_x + r * 1.5, center_y + r),
            fill=(249, 115, 22, alpha)
        )

    # Electric Blue ambient glow (bottom-right)
    for r in range(460, 0, -6):
        alpha = int(32 * (1 - r / 460))
        glow_draw.ellipse(
            (width - 150 - r * 1.4, height - 80 - r, width - 150 + r * 1.4, height - 80 + r),
            fill=(37, 99, 235, alpha)
        )

    # Subtle violet depth flare (center-right)
    for r in range(320, 0, -8):
        alpha = int(18 * (1 - r / 320))
        glow_draw.ellipse(
            (680 - r, 300 - r * 0.7, 680 + r, 300 + r * 0.7),
            fill=(139, 92, 246, alpha)
        )

    img = Image.alpha_composite(img, glow_img)
    draw = ImageDraw.Draw(img)

    # Outer sleek card border with subtle glass outline
    draw.rounded_rectangle([(24, 24), (width - 24, height - 24)], radius=24, outline=(34, 46, 68, 255), width=2)

    # Load high-quality system fonts with robust fallbacks
    def load_font(font_path, size):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            return ImageFont.load_default()

    font_brand = load_font("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 26)
    font_version = load_font("/usr/share/fonts/google-noto/NotoSansMono-CondensedBold.ttf", 13)
    font_pulse = load_font("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 13)
    font_title = load_font("/usr/share/fonts/redhat/RedHatDisplay-ExtraBold.otf", 48)
    font_title_sub = load_font("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 34)
    font_desc_bold = load_font("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 17)
    font_desc = load_font("/usr/share/fonts/google-noto/NotoSans-SemiBold.ttf", 15)
    font_pill_bold = load_font("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 13)
    font_pill = load_font("/usr/share/fonts/google-noto/NotoSans-SemiBold.ttf", 13)
    font_card_head = load_font("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 19)
    font_card_sub = load_font("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 13)
    font_card_body = load_font("/usr/share/fonts/google-noto/NotoSans-SemiBold.ttf", 12)
    font_footer = load_font("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 14)

    # -----------------------------
    # 1. Brand Header Row
    # -----------------------------
    logo_x, logo_y = 56, 44
    logo_size = 40
    draw.rounded_rectangle([(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], radius=10, fill=(249, 115, 22, 255))
    # Crisp terminal angle brackets < >
    draw.line([(logo_x + 14, logo_y + 12), (logo_x + 8, logo_y + 20), (logo_x + 14, logo_y + 28)], fill=(255, 255, 255, 255), width=3)
    draw.line([(logo_x + 26, logo_y + 12), (logo_x + 32, logo_y + 20), (logo_x + 26, logo_y + 28)], fill=(255, 255, 255, 255), width=3)

    # Brand Title
    draw.text((logo_x + 52, logo_y + 5), "InternScan", font=font_brand, fill=(248, 250, 252, 255))

    # Version / Global pill
    draw.rounded_rectangle([(logo_x + 196, logo_y + 6), (logo_x + 332, logo_y + 34)], radius=6, fill=(20, 28, 44, 255), outline=(44, 58, 86, 255), width=1)
    draw.text((logo_x + 208, logo_y + 11), "GLOBAL DIRECTORY", font=font_version, fill=(249, 115, 22, 255))

    # Live pulse badge top-right
    pill_w = 330
    pill_right_x = width - 56 - pill_w
    draw.rounded_rectangle([(pill_right_x, logo_y + 3), (width - 56, logo_y + 37)], radius=17, fill=(16, 24, 38, 255), outline=(37, 50, 75, 255), width=1)
    # Glowing green indicator
    draw.ellipse([(pill_right_x + 15, logo_y + 15), (pill_right_x + 25, logo_y + 25)], fill=(34, 197, 94, 255))
    draw.text((pill_right_x + 34, logo_y + 12), "DIRECT ATS · DAILY AT 3 AM IST", font=font_pulse, fill=(203, 213, 225, 255))

    # -----------------------------
    # 2. Main Hero Typography
    # -----------------------------
    draw.text((56, 108), "FAANG & Top Tech Internships", font=font_title, fill=(248, 250, 252, 255))
    draw.text((56, 164), "Global Engineering Roles · 2026 & 2027 Batches", font=font_title_sub, fill=(249, 115, 22, 255))

    draw.text((56, 214), "Automated, verified software, AI/ML, and systems internships tracked directly from 65+ official ATS APIs.", font=font_desc_bold, fill=(226, 232, 240, 255))
    draw.text((56, 240), "Zero ghost jobs · Exact place locations & tech hubs · Free REST & RSS APIs · Instant Telegram alerts", font=font_desc, fill=(148, 163, 184, 255))

    # -----------------------------
    # 3. Regional Hub Badges (Equally balanced)
    # -----------------------------
    regions = [
        ("IN", "India (BLR · HYD · DEL)"),
        ("US", "USA (Bay Area · SEA · NYC)"),
        ("CA", "Canada (TOR · WAT · VAN)"),
        ("UK", "UK (London · Cambridge)"),
        ("EU", "Europe (BER · DUB · MUC)"),
    ]
    cur_x = 56
    cur_y = 278
    for flag, label in regions:
        text = f"{flag} · {label}"
        bbox = draw.textbbox((cur_x, cur_y), text, font=font_pill_bold)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rounded_rectangle([(cur_x - 8, cur_y - 4), (cur_x + tw + 8, cur_y + th + 6)], radius=6, fill=(18, 26, 40, 255), outline=(42, 56, 82, 255), width=1)
        draw.text((cur_x, cur_y), text, font=font_pill_bold, fill=(203, 213, 225, 255))
        cur_x += tw + 16 + 12

    # Category pills row
    cur_x = 56
    cur_y = 318
    categories = [
        "SDE / Software", "AI & Machine Learning", "Data Engineering",
        "Systems & Cloud", "Hardware / Silicon", "Security"
    ]
    for cat in categories:
        bbox = draw.textbbox((cur_x, cur_y), cat, font=font_pill)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rounded_rectangle([(cur_x - 8, cur_y - 4), (cur_x + tw + 8, cur_y + th + 5)], radius=6, fill=(13, 19, 31, 240), outline=(32, 44, 66, 255), width=1)
        # Small accent dot
        draw.ellipse([(cur_x - 2, cur_y + 4), (cur_x + 3, cur_y + 9)], fill=(249, 115, 22, 230))
        draw.text((cur_x + 8, cur_y), cat, font=font_pill, fill=(148, 163, 184, 255))
        cur_x += tw + 22

    # -----------------------------
    # 4. Three High-Impact Feature Cards (Multi-line descriptions)
    # -----------------------------
    cards = [
        (
            "Zero Ghost Jobs",
            "100% Direct Official ATS Sync",
            ["Crawled from Workday, Greenhouse,", "Lever, SmartRecruiters. Never third-party."],
            (34, 197, 94, 255) # Green
        ),
        (
            "Place-Level Precision",
            "Exact Cities & Tech Hub Filters",
            ["Filter by specific office locations,", "recognized tech hubs, or remote roles."],
            (59, 130, 246, 255) # Blue
        ),
        (
            "Developer First & Open",
            "Public REST, RSS & Telegram Bot",
            ["CORS-enabled JSON endpoints, instant", "push alerts, 100% open source on GitHub."],
            (249, 115, 22, 255) # Orange
        ),
    ]

    card_w = 344
    card_h = 118
    card_y = 370
    spacing = (width - 112 - 3 * card_w) // 2

    for i, (title, subtitle, desc_lines, accent_color) in enumerate(cards):
        cx = 56 + i * (card_w + spacing)
        # Card background with glass surface
        draw.rounded_rectangle([(cx, card_y), (cx + card_w, card_y + card_h)], radius=14, fill=(13, 19, 31, 250), outline=(34, 46, 68, 255), width=1)
        # Left accent line
        draw.rounded_rectangle([(cx + 14, card_y + 16), (cx + 18, card_y + card_h - 16)], radius=2, fill=accent_color)
        # Text
        draw.text((cx + 30, card_y + 16), title, font=font_card_head, fill=(248, 250, 252, 255))
        draw.text((cx + 30, card_y + 42), subtitle, font=font_card_sub, fill=(203, 213, 225, 255))
        line_y = card_y + 68
        for line in desc_lines:
            draw.text((cx + 30, line_y), line, font=font_card_body, fill=(148, 163, 184, 255))
            line_y += 18

    # -----------------------------
    # 5. Bottom Footer Bar
    # -----------------------------
    draw.line([(56, 524), (width - 56, 524)], fill=(28, 38, 56, 255), width=1)

    url_text = "internscan.vercel.app"
    draw.text((56, 546), url_text, font=font_footer, fill=(203, 213, 225, 255))

    # Star icon and GitHub handle on right
    gh_x = width - 56 - 320
    draw_star(draw, gh_x - 14, 555, 7, fill=(249, 115, 22, 255))
    draw.text((gh_x, 546), "Star on GitHub · vishnunandan555/internscan", font=font_footer, fill=(249, 115, 22, 255))

    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "og-image.png")
    img.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated upgraded OpenGraph social preview card: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate()
