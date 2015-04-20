import urllib2

class ImageSearch:
    def search(lat, lon, radius, startdate, enddate):
        # This is stupid
        global searchproviders
        results = []
        for prov in searchproviders:
            results.extend(prov.search(lat, lon, radius, startdate, enddate))

        return results

class ImageSearchResult:
    def __init__(self, imageurl, resulturl, metadata, provider):
        self.imageurl = imageurl
        self.resulturl = resulturl
        self.metadata = metadata
        self.provider = provider


class ImageSearchVK:
    # http://vk.com/dev.php?method=photos.search
    PROVIDER = "VKontakte"

    def clamp_radius_to_set(self, radius):
        arr = [10, 100, 800, 5000, 6000, 50000]:
        curr = arr[0]
        for val in arr:
            if abs(radius - val) < abs (radius - curr):
                curr = val
        return curr

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["long"] = lon
        meta["start_time"] = startdate.strftime("%s")
        meta["end_time"] = enddate.strftime("%s")
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)

        

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
