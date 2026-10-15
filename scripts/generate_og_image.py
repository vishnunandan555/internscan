#!/usr/bin/env python3
"""
Generate an ultra-crisp, high-impact 1200x630 OpenGraph / Twitter preview card for InternScan India.
Saved to docs/og-image.png (Clean modern dark theme, NO gridlines).
"""
import os
from PIL import Image, ImageDraw, ImageFont

def generate():
    width = 1200
    height = 630
    # Deep sleek background: #07090e
    img = Image.new("RGBA", (width, height), (7, 9, 14, 255))
    draw = ImageDraw.Draw(img)

    # 1. Elegant ambient radial glow (Orange top-center flare)
    glow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    center_x, center_y = width // 2, -30
    for r in range(500, 0, -5):
        alpha = int(36 * (1 - r / 500))
        glow_draw.ellipse(
            (center_x - r * 1.6, center_y - r, center_x + r * 1.6, center_y + r),
            fill=(249, 115, 22, alpha)
        )
    # Subtle deep blue ambient glow bottom-right
    for r in range(360, 0, -5):
        alpha = int(26 * (1 - r / 360))
        glow_draw.ellipse(
            (width - 120 - r, height - 60 - r, width - 120 + r, height - 60 + r),
            fill=(37, 99, 235, alpha)
        )
    img = Image.alpha_composite(img, glow_img)
    draw = ImageDraw.Draw(img)

    # Outer sleek card border
    draw.rounded_rectangle([(24, 24), (width - 24, height - 24)], radius=24, outline=(34, 46, 68, 255), width=2)

    # Load fonts
    try:
        font_url = ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 16)
        font_badge = ImageFont.truetype("/usr/share/fonts/jetbrains-mono-fonts/JetBrainsMono-Bold.otf", 14)
        font_title = ImageFont.truetype("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 56)
        font_title_sub = ImageFont.truetype("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 48)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 21)
        font_pill = ImageFont.truetype("/usr/share/fonts/jetbrains-mono-fonts/JetBrainsMono-Bold.otf", 15)
        font_card_num = ImageFont.truetype("/usr/share/fonts/redhat/RedHatDisplay-Bold.otf", 24)
        font_card_desc = ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 14)
    except Exception:
        font_url = font_badge = font_pill = font_card_desc = ImageFont.load_default()
        font_title = font_title_sub = font_subtitle = font_card_num = ImageFont.load_default()

    # Brand badge top-left
    draw.rounded_rectangle([(60, 56), (104, 100)], radius=10, fill=(249, 115, 22, 255))
    # Terminal angle brackets icon in white
    draw.line([(73, 70), (68, 78), (73, 86)], fill=(255, 255, 255, 255), width=3)
    draw.line([(91, 70), (96, 78), (91, 86)], fill=(255, 255, 255, 255), width=3)
    draw.text((118, 64), "InternScan", font=font_card_num, fill=(248, 250, 252, 255))
    # Country pill
    draw.rounded_rectangle([(270, 64), (336, 94)], radius=8, fill=(22, 30, 46, 255), outline=(249, 115, 22, 180), width=1)
    draw.text((281, 71), "INDIA", font=font_pill, fill=(249, 115, 22, 255))

    # Live pulse pill top-right
    pill_right_x = width - 60 - 320
    draw.rounded_rectangle([(pill_right_x, 60), (width - 60, 96)], radius=18, fill=(22, 30, 46, 255), outline=(44, 56, 82, 255), width=1)
    draw.ellipse([(pill_right_x + 16, 73), (pill_right_x + 26, 83)], fill=(34, 197, 94, 255))
    draw.text((pill_right_x + 36, 70), "DIRECT ATS · DAILY AT 3 AM IST", font=font_badge, fill=(148, 163, 184, 255))

    # Main Headline
    draw.text((60, 134), "FAANG & Tech Internships", font=font_title, fill=(248, 250, 252, 255))
    draw.text((60, 204), "India · 2026 & 2027 Batches", font=font_title_sub, fill=(249, 115, 22, 255))

    # Subtitle
    draw.text((60, 274), "Automated directory of verified engineering, AI/ML & systems internships", font=font_subtitle, fill=(226, 232, 240, 255))
    draw.text((60, 308), "scraped directly from 55+ career APIs: Google, Microsoft, Amazon, NVIDIA & more.", font=font_subtitle, fill=(148, 163, 184, 255))

    # Category tags / pills
    tags = ["SDE / SWE", "AI & Machine Learning", "Data Engineering", "Backend & Cloud", "Hardware / Silicon", "Mobile & Frontend"]
    cur_x = 60
    cur_y = 362
    for tag in tags:
        bbox = draw.textbbox((cur_x, cur_y), tag, font=font_pill)
        t_w = bbox[2] - bbox[0]
        t_h = bbox[3] - bbox[1]
        draw.rounded_rectangle([(cur_x - 10, cur_y - 6), (cur_x + t_w + 10, cur_y + t_h + 8)], radius=6, fill=(17, 24, 39, 255), outline=(37, 50, 75, 255), width=1)
        # small orange dot inside tag
        draw.ellipse([(cur_x - 3, cur_y + 4), (cur_x + 3, cur_y + 10)], fill=(249, 115, 22, 220))
        draw.text((cur_x + 10, cur_y), tag, font=font_pill, fill=(226, 232, 240, 255))
        cur_x += t_w + 40

    # 3 Stat / Value Prop Cards
    cards = [
        ("Zero Ghost Jobs", "Direct sync with employer ATS portals", (34, 197, 94, 255)),
        ("Major Tech Hubs", "Bengaluru · Hyderabad · Pune · NCR", (59, 130, 246, 255)),
        ("100% Free & Open Source", "Automated daily GitHub Actions pipeline", (249, 115, 22, 255)),
    ]
    card_w = 340
    card_h = 92
    spacing = (width - 120 - 3 * card_w) // 2
    for i, (head, sub, color) in enumerate(cards):
        cx = 60 + i * (card_w + spacing)
        cy = 440
        # Card background
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=14, fill=(15, 21, 33, 245), outline=(34, 46, 68, 255), width=1)
        # Accent indicator
        draw.rounded_rectangle([(cx + 16, cy + 18), (cx + 20, cy + card_h - 18)], radius=2, fill=color)
        draw.text((cx + 32, cy + 22), head, font=font_card_num, fill=(248, 250, 252, 255))
        draw.text((cx + 32, cy + 54), sub, font=font_card_desc, fill=(148, 163, 184, 255))

    # Bottom footer line
    draw.line([(60, 552), (width - 60, 552)], fill=(28, 38, 56, 255), width=1)
    draw.text((60, 568), "vishnunandan555.github.io/internscan", font=font_url, fill=(148, 163, 184, 255))
    draw.text((width - 60 - 275, 568), "Live Web Tracker · Star on GitHub", font=font_url, fill=(249, 115, 22, 255))

    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "og-image.png")
    img.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated clean social preview card without gridlines: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate()
