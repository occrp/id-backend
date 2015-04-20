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
    # https://instagram.com/developer/endpoints/media/
    # https://instagram.com/accounts/login/?next=%2Fdeveloper%2Fregister%2F
    # https://github.com/Instagram/python-instagram/blob/master/README.md
    # https://instagram.com/developer/endpoints/media/#get_media_search
    # you can only create an account via the mobile app o_O'
    PROVIDER = "Instagram"
    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = ImageSearchResultSet()
        
        # search metadata
        meta = {}
        #meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        meta["min_timestamp"] = startdate.strftime("%s")
        meta["max_timestamp"] = enddate.strftime("%s")
        #meta["offset"] = offset
        #meta["count"] = count
        meta["distance"] = self.clamp_radius_to_set(radius)

        # run the query
        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        data = json.loads(r.content)
        
        # get a nice results
        for item in data["response"]:
            i = ImageSearchResult(item.images["standard_resolution"]["url"], item["link"], item["created_time"], item, self.PROVIDER)
            results.append(i)
        

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

class ImageSearchFlickr:
    # https://www.flickr.com/services/api/flickr.photos.search.html
    # this needs a mobile phone for registering with flickr/yahoo o_O'
    PROVIDER = "Flickr"

    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = ImageSearchResultSet()
        
        # search metadata
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        meta["min_timestamp"] = startdate.strftime("%s")
        meta["max_timestamp"] = enddate.strftime("%s")
        #meta["offset"] = offset
        #meta["count"] = count
        meta["distance"] = self.clamp_radius_to_set(radius)

        # run the query
        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        data = json.loads(r.content)
        
        # get a nice results
        for item in data["response"]:
            i = ImageSearchResult(item.images["standard_resolution"]["url"], item["link"], item["created_time"], item, self.PROVIDER)
            results.append(i)


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, ImageSearchVK, ImageSearchGoogleImages, ImageSearchFlickr]
