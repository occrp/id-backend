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

    def search(lat, lon, radius, startdate, enddate):
        pass

class ImageSearchInstagram:
    # https://instagram.com/developer/endpoints/locations/
    PROVIDER = "Instagram"

    def search(lat, lon, radius, startdate, enddate):
        pass

class ImageSearchGoogleImages:
    PROVIDER = "Google Images"

    def search(lat, lon, radius, startdate, enddate):
        pass

class ImageSearchTwitter:
    PROVIDER = "Twitter"

    def search(lat, lon, radius, startdate, enddate):
        pass

class ImageSearchFacebook:
    PROVIDER = "Facebook"

    def search(lat, lon, radius, startdate, enddate):
        pass


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, ImageSearchVK, ImageSearchGoogleImages]