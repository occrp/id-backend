from datetime import datetime

from search.searchers.base import ResultSet
from search.searchers.base import ImageSearcher, ImageSearchResult


class ImageSearchVK(ImageSearcher):
    # http://vk.com/dev.php?method=photos.search
    PROVIDER = "VKontakte"
    URL = "https://api.vk.com/method/photos.search"

    def clamp_radius_to_set(self, radius):
        arr = [10, 100, 800, 5000, 6000, 50000]
        curr = arr[0]
        for val in arr:
            if abs(radius - val) < abs (radius - curr):
                curr = val
        return curr

    def search(self, q, lat, lon, radius=5000, startdate=None, enddate=None,
               offset=0, count=100):
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["long"] = lon
        if startdate: meta["start_time"] = startdate.strftime("%s")
        if enddate: meta["end_time"] = enddate.strftime("%s")
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)
        meta["v"] = "5.30"

        data = self.json_api_request(meta)
        results = ResultSet(total=data["response"]["count"])
        for item in data["response"]["items"]:
            timestamp = datetime.utcfromtimestamp(item["date"])
            large_photo = item.get("photo_604", item.get("photo_130", ""))
            large_photo = item.get("photo_807", large_photo)
            i = ImageSearchResult(self.PROVIDER,
                item["photo_604"],
                large_photo,
                timestamp,
                caption=item.get("text", ""),
                linkurl="",
                linktitle="",
                metadata=item)
            results.append(i)

        return results
