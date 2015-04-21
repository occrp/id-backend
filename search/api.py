import urllib
import urllib2
import json
from datetime import datetime
from threading import Thread
from core.utils import json_dumps

class ImageSearchResult(dict):
    def __init__(self, imageurl, resulturl, timestamp, caption, metadata, provider):
        self["provider"] = provider
        self["timestamp"] = timestamp
        self["image_url"] = imageurl
        self["result_url"] = resulturl
        self["caption"] = caption
        self["metadata"] = metadata


class ImageSearcher():
    def start(self, search):
        thread = Thread(target=self.run, args=(search,))
        thread.start()

    def run(self, search):
        # id, q, lat, lon, radius, startdate, enddate, offset, count
        query = json.loads(search.query)
        q = query["q"].encode("utf-8")
        lat = query["lat"]
        lon = query["lon"]
        radius = query["radius"]
        startdate = query["startdate"]
        enddate = query["enddate"]
        offset = query["offset"]
        count = query["count"]

        print "ImageSearch:%s:START" % (self.PROVIDER)
        runner = search.create_runner(self.PROVIDER)

        results = self.search(q, lat, lon, radius, startdate, enddate, offset, count)
        for r in results:
            search.create_result(self.PROVIDER, r)

        runner.done = True
        runner.results = len(results)
        runner.save()
        print "ImageSearch:%s:FINISH" % (self.PROVIDER)


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

    def search(self, q, lat, lon, radius=5000, startdate=None, enddate=None, offset=0, count=100):
        results = []
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["long"] = lon
        if startdate: meta["start_time"] = startdate
        if enddate: meta["end_time"] = enddate
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)
        meta["v"] = "5.30"

        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        print "Hitting: %s?%s" % (self.URL, urllib.urlencode(meta))
        data = json.loads(r.read())
        for item in data["response"]["items"]:
            timestamp = datetime.utcfromtimestamp(item["date"])
            large_photo = item.get("photo_807", item.get("photo_604", item.get("photo_130", "")))
            i = ImageSearchResult(item["photo_130"], large_photo, timestamp, item["text"], item, self.PROVIDER)
            results.append(i)

        return results


class ImageSearchInstagram(ImageSearcher):
    # https://instagram.com/developer/endpoints/media/
    # https://instagram.com/accounts/login/?next=%2Fdeveloper%2Fregister%2F
    # https://github.com/Instagram/python-instagram/blob/master/README.md
    # https://instagram.com/developer/endpoints/media/#get_media_search
    # you can only create an account via the mobile app o_O'
    PROVIDER = "Instagram"
    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = []
        
        # search metadata
        meta = {}
        #meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        meta["min_timestamp"] = startdate
        meta["max_timestamp"] = enddate
        #meta["offset"] = offset
        #meta["count"] = count
        #meta["distance"] = self.clamp_radius_to_set(radius)

        # run the query
        #r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        #data = json.loads(r.content)
        
        # get a nice results
        #for item in data["response"]:
        #    i = ImageSearchResult(item.images["standard_resolution"]["url"], item["link"], item["created_time"], item, self.PROVIDER)
        #    results.append(i)

        return results

class ImageSearchGoogleImages(ImageSearcher):
    PROVIDER = "Google Images"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return []

class ImageSearchTwitter(ImageSearcher):
    PROVIDER = "Twitter"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return []

class ImageSearchFacebook(ImageSearcher):
    PROVIDER = "Facebook"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        return []

class ImageSearchFlickr(ImageSearcher):
    # https://www.flickr.com/services/api/flickr.photos.search.html
    # this needs a mobile phone for registering with flickr/yahoo o_O'
    PROVIDER = "Flickr"

    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = []
        
        # search metadata
        meta = {}
        meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        meta["min_timestamp"] = startdate
        meta["max_timestamp"] = enddate
        #meta["offset"] = offset
        #meta["count"] = count
        #meta["distance"] = self.clamp_radius_to_set(radius)

        # run the query
        #r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        #data = json.loads(r.content)
        
        # get a nice results
        #for item in data["response"]:
        #    i = ImageSearchResult(item.images["standard_resolution"]["url"], item["link"], item["created_time"], item, self.PROVIDER)
        #    results.append(i)
        return []


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, 
                   ImageSearchVK, ImageSearchGoogleImages, ImageSearchFlickr]
