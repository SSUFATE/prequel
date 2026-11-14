# app/models.py

from app.domains.additional_info.model import Translation, VisualAid
from app.domains.favorites.model import Favorite
from app.domains.kcontents.model import KContent
from app.domains.literatures.model import LiteraryWork
from app.domains.recommendations.model import Recommendation
from app.domains.tags.model import KContentTag, LiteraryWorkTag, Tag
from app.domains.users.model import User

__all__ = [
    "User",
    "KContent",
    "LiteraryWork",
    "Tag",
    "KContentTag",
    "LiteraryWorkTag",
    "Favorite",
    "Recommendation",
    "Translation",
    "VisualAid",
]