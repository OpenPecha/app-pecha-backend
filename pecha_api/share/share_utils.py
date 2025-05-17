from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

class ShareUtils:

    @staticmethod
    def get_font_path(language: str) -> str:
        language_font_path = {
            "en": "../assets/fonts/en.ttf",
            "bo": "../assets/fonts/bo.ttf"
        }
        return language_font_path.get(language, "../assets/fonts/en.ttf")

    @staticmethod
    def clean_html(content: str, max_lines: int = 4) -> str:
        soup = BeautifulSoup(content, "html.parser")

        # Replace <br> with newline character
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # Remove all other HTML tags and their contents
        for tag in soup.find_all():
            tag.decompose()

        # Get cleaned text
        text = soup.get_text()
        lines = text.strip().splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append("...")
        return "\n".join(lines)
    
    @staticmethod
    def create_image_bytes(text: str, language: str) -> BytesIO:
        width, height = 1200, 630
        background_color = (165, 42, 42)     # Brown
        text_color = (255, 255, 255)        # White

        # Create a blank red image
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # NOTE: PIL ImageFont.truetype does NOT support .woff files. Use .ttf or .otf instead.
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ShareUtils.get_font_path(language)))
        if not os.path.exists(font_path):
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, 64)

        # Draw the cleaned text
        draw.multiline_text((100, 100), text, fill=text_color, font=font, spacing=10)

        # Save to BytesIO
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        return buf