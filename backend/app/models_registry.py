# 모든 모델을 여기서 실제로 import → Base의 클래스 레지스트리에 등록됨
from app.domains.kcontents.model import KContent
from app.domains.literatures.model import LiteraryWork
from app.domains.tag.model import KContentTag, LiteraryWorkTag
from app.domains.favorites.model import Favorite
from app.domains.recommendations.model import Recommendation
from app.domains.additional_info.model import Translation, VisualAid