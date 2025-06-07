from pecha_api.error_contants import ErrorConstants
from fastapi import HTTPException, UploadFile, status
from PIL import Image
import io
from pecha_api.config import get_int

class ImageUtils:
    @staticmethod
    def validate_and_compress_image(file: UploadFile, content_type: str) -> io.BytesIO:
        max_file_size = get_int("MAX_FILE_SIZE_MB")
        bit_size = 1024 * 1024
        rgba = 'RGBA'
        MAX_FILE_SIZE_BYTES = max_file_size * bit_size
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorConstants.IMAGE_ERROR_MESSAGE
            )
        file.file.seek(0, 2)  # Move to the end of the file to get its size
        file_size = file.file.tell()
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=ErrorConstants.IMAGE_SIZE_ERROR_MESSAGE
            )
        file.file.seek(0)  # Reset file pointer
        # Read and compress the image
        try:
            image = Image.open(file.file)
            if image.mode in (rgba, 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert(rgba)
                background.paste(image, mask=image.split()[3] if image.mode == rgba else image.split()[1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
                
            compressed_image_io = io.BytesIO()
            image.save(compressed_image_io, format="JPEG", quality=get_int("COMPRESSED_QUALITY"))
            compressed_image_io.seek(0)
            return compressed_image_io
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorConstants.IMAGE_PROCESSING_ERROR_MESSAGE
            )
