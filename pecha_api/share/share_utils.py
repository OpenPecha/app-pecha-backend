from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class ShareUtils:

    @staticmethod
    def clean_html(content: str, max_lines: int = 4) -> str:
        soup = BeautifulSoup(content, "html.parser")

        # Convert <br> to \n
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # Get cleaned text
        text = soup.get_text()
        lines = text.strip().splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append("...")
        return "\n".join(lines)
    
    @staticmethod
    def create_image_bytes(text: str) -> BytesIO:
        width, height = 800, 600
        background_color = (255, 0, 0)      # Red
        text_color = (255, 255, 255)        # White

        # Create a blank red image
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # Load a font that supports Tibetan script
        try:
            font = ImageFont.truetype("NotoSansTibetan-Regular.ttf", 32)
        except:
            font = ImageFont.load_default()  # Fallback font

        # Draw the cleaned text
        draw.multiline_text((50, 50), text, fill=text_color, font=font, spacing=10)

        # Save to BytesIO
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        return buf