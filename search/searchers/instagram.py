from datetime import datetime

from core.utils import Credentials
from search.searchers.base import ResultSet, MediaSearcher, MediaSearchResult


class MediaSearchInstagram(MediaSearcher):
    # https://instagram.com/developer/endpoints/media/
    # https://instagram.com/accounts/login/?next=%2Fdeveloper%2Fregister%2F
    # https://github.com/Instagram/python-instagram/blob/master/README.md
    # https://instagram.com/developer/endpoints/media/#get_media_search
    # you can only create an account via the mobile app o_O'
    #
    PROVIDER = "Instagram"
    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius=5000, startdate=None, enddate=None,
               offset=0, count=100):
        # search metadata
        meta = {}
        meta["access_token"] = Credentials().get("instagram", "access_token")
        # meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        if startdate:
            meta["min_timestamp"] = startdate.strftime("%s")
        if enddate:
            meta["max_timestamp"] = enddate.strftime("%s")
        if radius > 5000:
            radius = 5000
        meta["distance"] = radius

        data = self.json_api_request(meta, force_get=True)
        results = ResultSet(total=len(data["data"]))
        for item in data["data"]:
            caption = ""
            if item.get("caption"):
                caption = item.get("caption").get("text", "")

            ts = datetime.utcfromtimestamp(float(item["created_time"]))
            i = MediaSearchResult(
                provider=self.PROVIDER,
                imageurl=item["images"]["low_resolution"]["url"],
                resulturl=item["link"],
                timestamp=ts,
                caption=caption,
                linkurl=item["link"],
                linktitle=item["user"]["full_name"],
                metadata=item)
            results.append(i)

        return results
