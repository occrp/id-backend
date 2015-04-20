import urllib
import urllib2
import json
from datetime import datetime

class ImageSearchDispatcher:
    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # This is stupid
        global searchproviders
        results = ImageSearchResultSet()

        try: startdate = datetime.utcfromtimestamp(float(startdate))
        except: startdate = None
        try: enddate = datetime.utcfromtimestamp(float(enddate))
        except: enddate = None

        for prov in searchproviders:
            provider = prov()
            results.extend(provider.search(q, lat, lon, radius, startdate, enddate, offset, count))

        return results

class ImageSearchResultSet(list):
    def sort_by_timestamp_asc():
        pass

    def sort_by_timestamp_desc():
        pass

    def sort_by_metadata_value():
        pass


class ImageSearchResult:
    def __init__(self, imageurl, resulturl, timestamp, caption, metadata, provider):
        self.imageurl = imageurl
        self.resulturl = resulturl
        self.metadata = metadata
        self.provider = provider
        self.timestamp = timestamp
        self.caption = caption


class ImageSearchVK:
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

    def search(self, q, lat, lon, radius=5000, startdate=None, enddate=None, offset=0, count=100):
        results = ImageSearchResultSet()
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["lon"] = lon
        if startdate: meta["start_time"] = startdate.strftime("%s")
        if enddate: meta["end_time"] = enddate.strftime("%s")
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)

        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        data = json.loads(r.read())
        for item in data["response"][1:]:
            timestamp = datetime.utcfromtimestamp(item["created"])
            i = ImageSearchResult(item["src"], item["src"], timestamp, item["text"], item, self.PROVIDER)
            results.append(i)

        return results


class ImageSearchInstagram:
    # https://instagram.com/developer/endpoints/locations/
    PROVIDER = "Instagram"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return ImageSearchResultSet()

class ImageSearchGoogleImages:
    PROVIDER = "Google Images"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return ImageSearchResultSet()

class ImageSearchTwitter:
    PROVIDER = "Twitter"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return ImageSearchResultSet()

class ImageSearchFacebook:
    PROVIDER = "Facebook"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return ImageSearchResultSet()


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, ImageSearchVK, ImageSearchGoogleImages]
