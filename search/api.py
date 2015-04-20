import urllib
import urllib2

class ImageSearch:
    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # This is stupid
        global searchproviders
        results = []
        for prov in searchproviders:
            results.extend(prov.search(lat, lon, radius, startdate, enddate))

        return results

class ImageSearchResultSet(list):
    def sort_by_timestamp_asc():
        pass

    def sort_by_timestamp_desc():
        pass

    def sort_by_metadata_value():
        pass


class ImageSearchResult:
    def __init__(self, imageurl, resulturl, timestamp, metadata, provider):
        self.imageurl = imageurl
        self.resulturl = resulturl
        self.metadata = metadata
        self.provider = provider
        self.timestamp = timestamp


class ImageSearchVK:
    # http://vk.com/dev.php?method=photos.search
    PROVIDER = "VKontakte"
    URL = "https://api.vk.com/method/photos.search"

    def clamp_radius_to_set(self, radius):
        arr = [10, 100, 800, 5000, 6000, 50000]:
        curr = arr[0]
        for val in arr:
            if abs(radius - val) < abs (radius - curr):
                curr = val
        return curr

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        results = ImageSearchResultSet()
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["long"] = lon
        meta["start_time"] = startdate.strftime("%s")
        meta["end_time"] = enddate.strftime("%s")
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)

        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        data = json.loads(r.content)
        for item in data["response"][1:]:
            i = ImageSearchResult(item["src"], item["src"], item["created"], item, self.PROVIDER)
            results.append(i)


class ImageSearchInstagram:
    # https://instagram.com/developer/endpoints/locations/
    PROVIDER = "Instagram"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        pass

class ImageSearchGoogleImages:
    PROVIDER = "Google Images"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        pass

class ImageSearchTwitter:
    PROVIDER = "Twitter"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        pass

class ImageSearchFacebook:
    PROVIDER = "Facebook"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        pass


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, ImageSearchVK, ImageSearchGoogleImages]
