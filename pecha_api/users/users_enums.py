from enum import Enum


class RegistrationSource(Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    EMAIL = "email"


class SocialProfile(Enum):
    EMAIL = "email"
    X_COM = 'x.com'
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
