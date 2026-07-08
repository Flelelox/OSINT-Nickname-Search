from core.models import SearchResult


class ResultBuilder:

    @staticmethod
    def build(
        service: str,
        username: str,
        url: str,
        similarity: int = 100,
    ) -> SearchResult:

        return SearchResult(

            service=service,

            username=username,

            profile_url=url,

            exists=True,

            similarity=similarity,

            display_name=None,

            biography=None,

            avatar_url=None,

            website=None,

            followers=None,

            created_at=None,

            raw_data={}

        )