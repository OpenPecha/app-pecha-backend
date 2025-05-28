import logging
import textwrap
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

FONT_PATHS = {
    "bo": "pecha_api/share/static/fonts/wujin+gangbi.ttf",
    "en": "pecha_api/share/static/fonts/Noto-font/NotoFont-en.ttf",
    "FALL_BACK": "pecha_api/share/static/fonts/Noto-font/NotoFont-en.ttf"
}

FONT_SIZE = {
    "bo": 25,
    "en": 22,
    "FALL_BACK": 22
}

DEFAULT_OUTPUT_PATH = "pecha_api/share/static/img/output.png"


def _clean_text(content: str, max_lines: int = 4) -> str:
    """
    Clean HTML content to plain text, limit to max_lines, add ellipsis if truncated.
    """
    soup = BeautifulSoup(content, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for tag in soup.find_all():
        tag.decompose()
    text = soup.get_text()
    lines = text.strip().splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append("...")
    return "\n".join(lines)


def _add_logo_to_image(img, logo_path, image_width, image_height, header_ratio=0.05, logo_height_ratio=0.06):
    """
    Add a centered logo to an RGBA image, returns composited image.
    """
    try:
        logo = Image.open(logo_path).convert('RGBA')
        logo_height = int(image_height * logo_height_ratio)
        logo_ratio = logo.size[0] / logo.size[1]
        logo_width = int(logo_height * logo_ratio)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        logo_padded = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
        logo_x = int(image_width/2 - logo_width/2)
        logo_y = int(image_height * header_ratio - logo_height/2)
        logo_padded.paste(logo, (logo_x, logo_y))
        return Image.alpha_composite(img, logo_padded)
    except Exception as e:
        logging.warning(f"Error adding logo: {e}")
        return img

class SyntheticImageGenerator:

    def __init__(self, image_width, image_height, font_size=24, font_type="en", bg_color="#ac1c22") -> None:
        self.image_width = int(image_width)
        self.image_height = int(image_height)
        self.font_size = int(font_size)
        self.font_type = font_type
        self.bg_color = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
    def calc_letters_per_line(self, text, font, max_width):
        """Calculate approximately how many characters can fit in the given width."""
        avg_char_width = font.getlength("བ")  # Use a typical character for estimation
        return int(max_width / avg_char_width)

    def add_borders(self, draw):
        """Add borders to the image"""
        # Draw border lines
        border_color = "#666666"
        draw.line((0, 0, self.image_width, 0), fill=border_color, width=1)  # Top
        draw.line((0, 0, 0, self.image_height), fill=border_color, width=1)  # Left
        draw.line((self.image_width-1, 0, self.image_width-1, self.image_height), fill=border_color, width=1)  # Right
        draw.line((0, self.image_height-1, self.image_width, self.image_height-1), fill=border_color, width=1)  # Bottom

    def add_header(self, draw):
        """Add white header section"""
        header_height = int(self.image_height * 0.05)
        # White header background
        draw.line((0, header_height, self.image_width, header_height), 
                 fill=(255, 255, 255), 
                 width=int(self.image_height * 0.1))
        # Gray separator line
        draw.line((0, header_height * 2, self.image_width, header_height * 2), 
                 fill="#CCCCCC", 
                 width=int(self.image_height * 0.0025))

    def save_image(self, text, ref_str, lang, img_file_name=DEFAULT_OUTPUT_PATH, logo_path=None):
        """
        Generate and save a synthetic image with the given text, reference, and options.
        """
        font_file_name = FONT_PATHS.get(self.font_type, FONT_PATHS['FALL_BACK'])
        # Create base image with RGBA mode to support transparency
        img = Image.new('RGBA', (self.image_width, self.image_height), color=self.bg_color + (255,))
        d = ImageDraw.Draw(img)
        # Add header and borders
        self.add_header(d)
        self.add_borders(d)
        # Define fonts and text color
        if len(text) < 100:
            main_font_size = int(self.font_size * 1.5)
        else:
            main_font_size = self.font_size
        main_font = ImageFont.truetype(font_file_name, size=main_font_size, encoding='utf-16')
        ref_font = ImageFont.truetype(font_file_name, size=int(main_font_size/2), encoding='utf-16')
        text_color = (255, 255, 255)
        # Calculate padding and max width
        padding_x = 5  # Padding from edges
        max_width = self.image_width - (padding_x * 2)
        # Wrap text using textwrap
        chars_per_line = self.calc_letters_per_line(text, main_font, max_width)
        wrapped_text = textwrap.fill(text=text, width=chars_per_line)
        # Draw main text
        d.text(
            xy=(self.image_width / 2, self.image_height / 2),
            text=wrapped_text,
            font=main_font,
            fill=text_color,
            anchor='mm',
            align='center',
            spacing=int(main_font_size * 0.5)
        )
        # Draw reference text
        d.text(
            xy=(self.image_width / 2, self.image_height - 40),
            text=ref_str,
            font=ref_font,
            fill=text_color,
            anchor='mm'
        )
        # Add logo if provided
        if logo_path:
            img = _add_logo_to_image(img, logo_path, self.image_width, self.image_height)
        # Save the image
        img.save(img_file_name)


def create_synthetic_data(text, ref_str, lang, logo_path=None, output_path=DEFAULT_OUTPUT_PATH):
    """
    Generate a synthetic image from text and reference string, saving to output_path.
    """
    cleaned_text = _clean_text(text)
    font_type_lang = lang
    generator = SyntheticImageGenerator(
        image_width=700,
        image_height=400,
        font_size=FONT_SIZE.get(font_type_lang, FONT_SIZE['FALL_BACK']),
        font_type=font_type_lang,
        bg_color="#ac1c22"
    )
    generator.save_image(cleaned_text, ref_str, lang, img_file_name=output_path, logo_path=logo_path)

def generate_text_image(text: str = None, ref_str: str = None, lang: str = None, logo_path: str = None, output_path: str = DEFAULT_OUTPUT_PATH):
    """
    Main entry to generate a text image or fallback logo image.
    """
    if text is not None and text != "":
        create_synthetic_data(text, ref_str, lang, logo_path, output_path)
    else:
        width = 1200
        height = 630
        img = Image.new('RGBA', (width, height), color="#b5343c")
        try:
            img = _add_logo_to_image(img, "pecha_api/share/static/img/pecha-logo.png", width, height, header_ratio=0.5, logo_height_ratio=0.3)
        except Exception as e:
            logging.warning(f"Error adding fallback logo: {e}")
        img.save(output_path)


# if __name__ == "__main__":
#     text = os.environ.get("SEGMENT_TEXT")
#     ref_str = os.environ.get("REFERENCE_TEXT")
#     lang = os.environ.get("LANGUAGE")
#     create_synthetic_data(text, ref_str, lang, logo_path="pecha_api/share/static/img/pecha-logo.png")