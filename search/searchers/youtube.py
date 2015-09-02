from apiclient.discovery import build

from core.utils import Credentials
from search.searchers.base import ImageSearcher, ImageSearchResult

OAUTH_SCOPE = 'https://www.googleapis.com/auth/youtube.readonly'


class ImageSearchYouTube(ImageSearcher):
    PROVIDER = "YouTube"
    URL = "https://www.googleapis.com/youtube/v3/search"

    def search(self, q, lat=None, lon=None, radius=50000, startdate=None,
               enddate=None, offset=0, count=50):
        http = Credentials().get_oauth2_http("google", scope=OAUTH_SCOPE)

        youtube = build("youtube", "v3", http=http)
        results = []
        terms = {}
        terms["q"] = q
        if lat and lon:
            terms["location"] = "%s,%s" % (lat, lon)
            terms["locationRadius"] = "%sm" % radius
        if startdate:
            terms["publishedAfter"] = startdate.isoformat()+"Z"
        if enddate:
            terms["publishedBefore"] = enddate.isoformat()+"Z"

        if count > 50:
            count = 50

        response = youtube.search().list(
            part="id,snippet", order="date", type="video", safeSearch="none",
            maxResults=count,
            **terms
        ).execute()

        for item in response.get("items", []):
            timestamp = item["snippet"]["publishedAt"]
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
            caption = item["snippet"]["title"]
            link = "http://youtu.be/%s" % item["id"]["videoId"]
            i = ImageSearchResult(self.PROVIDER, thumbnail, link, timestamp,
                                  caption, item)
            results.append(i)

        return results
