from sqlalchemy.orm import Session

from app.domains.kcontents.home_sections import HOME_SECTIONS
from app.domains.kcontents.crud import get_home_section_contents

# 홈 화면 -> 섹션별 영화 조회
def get_home_sections(db: Session):
    sections = []

    for section in HOME_SECTIONS:
        contents = get_home_section_contents(
            db=db,
            section=section,
        )

        sections.append(
            {
                "key": section["key"],
                "title": section["title"],
                "type": section["type"],
                "contents": [
                    {
                        "content_id": content.content_id,
                        "title": content.title,
                        "poster_url": content.poster_url,
                        "release_date": content.release_date,
                    }
                    for content in contents
                ],
            }
        )

    return {"sections": sections}