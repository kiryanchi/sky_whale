import asyncio
from unittest import main, IsolatedAsyncioTestCase

from setting import NUM_OF_SEARCH
from sky_whale.search.youtube import search_from_youtube, YoutubeSearchResult


class YoutubeSearchTest(IsolatedAsyncioTestCase):

    async def test_검색_결과가_None이_아니어야_한다(self):
        # given
        query: str = "Lucy"

        # when
        result: list[YoutubeSearchResult] = await search_from_youtube(query)

        # then
        self.assertIsNotNone(result, "검색 결과가 None이 아니어야 한다.")

    async def test_검색_결과는_NUM_OF_SEARCH와_같아야_한다(self):
        # given
        query: str = "Lucy"

        # when
        result = await search_from_youtube(query)

        # then
        self.assertEqual(len(result), NUM_OF_SEARCH)

    async def test_검색_결과는_YoutubeSearchResult_객체여야_한다(self):
        # given
        query: str = "Lucy"

        # when
        result = await search_from_youtube(query)

        # then
        self.assertIsInstance(
            result[0],
            YoutubeSearchResult,
            "검색 결과는 YoutubeSearchResult 객체여야 한다.",
        )

    async def test_YoutubeSearchResult_객체는_제대로_생성되어야_한다(self):
        # given
        query: str = "Lucy"

        # when
        result = await search_from_youtube(query)

        # then
        self.assertIsNotNone(result[0].title, "title이 None이 아니어야 한다.")
        self.assertIsNotNone(result[0].uploader, "uploader가 None이 아니어야 한다.")
        self.assertIsNotNone(result[0].duration, "duration이 None이 아니어야 한다.")
        self.assertIsNotNone(result[0].link, "link가 None이 아니어야 한다.")

    async def test_YoutubeSearchResult_객체는_제대로_표현되어야_한다(self):
        # given
        query: str = "Lucy"

        # when
        result = await search_from_youtube(query)

        # then
        self.assertEqual(
            str(result[0]),
            f"Title: {result[0].title}, Uploader: {result[0].uploader}, Duration: {result[0].duration}",
        )

    def test_만약_YoutubeSearchResult_속성에_None이_들어가면_ValueError가_발생해야_한다(
        self,
    ):
        # given
        title: str = None
        uploader: str = None
        duration: str = None
        link: str = None

        # when, then
        with self.assertRaises(ValueError):
            YoutubeSearchResult(title, uploader, duration, link)


if __name__ == "__main__":
    main()
