import urllib
import urllib2
import httplib2
import json
from datetime import datetime
import dateutil.parser
from threading import Thread
from core.utils import json_dumps, Credentials

from oauth2client import tools as oauth2tools
from oauth2client import client as oauth2client

from apiclient.discovery import build
from apiclient.errors import HttpError

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
        if query["startdate"]:
            startdate = dateutil.parser.parse(query["startdate"])
        else:
            startdate = None
        if query["enddate"]:
            enddate = dateutil.parser.parse(query["enddate"])
        else:
            enddate = None
        offset = query["offset"]
        count = query["count"]

        # logger.log("ImageSearch:%s:START" % (self.PROVIDER))
        runner = search.create_runner(self.PROVIDER)

        results = self.search(q, lat, lon, radius, startdate, enddate, offset, count)
        for r in results:
            search.create_result(self.PROVIDER, r)

        runner.done = True
        runner.results = len(results)
        runner.save()
        # logger.log("ImageSearch:%s:FINISH" % (self.PROVIDER))

    def json_api_request(self, meta):
        print "ImageSearch:%s:Hitting: %s?%s" % (self.PROVIDER, self.URL, urllib.urlencode(meta))
        r = urllib2.urlopen(self.URL, urllib.urlencode(meta))
        return json.loads(r.read())


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
        if startdate: meta["start_time"] = startdate.strftime("%s")
        if enddate: meta["end_time"] = enddate.strftime("%s")
        meta["offset"] = offset
        meta["count"] = count
        meta["radius"] = self.clamp_radius_to_set(radius)
        meta["v"] = "5.30"

        data = self.json_api_request(meta)
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
    # 
    CLIENT_ID = "3664a35618ef491f8071dde568c08d38"
    CLIENT_SECRET = "49f7cfb9d2d44403b6c4e74000243613"
    CLIENT_CODE = "bec7d320fb084540bc36b91e5e8e6785"
    WEBSITE_URL = "https://investigativedashboard.org"
    REDIRECT_URI = "https://investigativedashboard.org"

    PROVIDER = "Instagram"
    URL = "https://api.instagram.com/v1/media/search"
    OAUTH_TOKEN = {
        "access_token":"2007223339.3664a35.bd4175cee6994603b46b6e66abdedb4b",
        "user": {"username":"id000000id","bio":"","website":"","profile_picture":"https:\/\/igcdn-photos-g-a.akamaihd.net\/hphotos-ak-xpa1\/outbound-distillery\/t0.0-20\/OBPTH\/profiles\/anonymousUser.jpg","full_name":"ID","id":"2007223339"}
    }

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = []
        
        # search metadata
        meta = {}
        meta["access_token"] = self.OAUTH_TOKEN["access_token"]
        #meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        if startdate:
            meta["min_timestamp"] = startdate.strftime("%s")
        if enddate:
            meta["max_timestamp"] = enddate.strftime("%s")
        if radius > 5000: radius = 5000
        meta["distance"] = radius

        data = self.json_api_request(meta)
        for item in data["data"]:
            i = ImageSearchResult(
                item["images"]["low_resolution"], 
                item["link"], 
                item["created_time"], 
                item["caption"], 
                item, 
                self.PROVIDER)
            results.append(i)

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
    URL = "https://graph.facebook.com/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        results = []
        meta = {}
        meta["q"] = q
        meta["type"] = "user"
        meta["center"] = "%f,%f" % (lat, lon)
        meta["distance"] = radius

        #data = self.json_api_request(meta)
        # for d in data:
        #print data

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


class ImageSearchYouTube(ImageSearcher):
    # https://www.flickr.com/services/api/flickr.photos.search.html
    # this needs a mobile phone for registering with flickr/yahoo o_O'
    PROVIDER = "YouTube"

    URL = "https://www.googleapis.com/youtube/v3/search"

    def search(self, q, lat=None, lon=None, radius=50000, startdate=None, enddate=None, offset=0, count=50):
        # results
        #credentials = Credentials().get_oauth2_credentials("google", 
        #    scope='https://www.googleapis.com/auth/youtube.readonly')

        #flow = oauth2client.flow_from_clientsecrets("google_api.cred",
        #    scope='https://www.googleapis.com/auth/youtube.readonly')
        #credentials = oauth2tools.run_flow(flow)

        #http = httplib2.Http()
        #http = credentials.authorize(http)

        youtube = build("youtube", "v3", developerKey="AIzaSyAPzVYxD72NlBNSFC5tByUCs4WZ9i3eypc")
        results = []
        terms = {}
        terms["q"] = q
        if lat and lon:
            terms["location"] = "%s,%s" % (lat, lon)
            terms["locationRadius"] = "%sm" % radius
        if startdate:
            terms["publishedAfter"] = startdate.isoformat()
        if enddate:
            terms["publishedBefore"] = enddate.isoformat()

        response = youtube.search().list(
            part="id,snippet", order="date", type="video", safeSearch="none",
            maxResults=count, 
            **terms
        )
        return response
        print response
        for item in response.get("items", [])["items"]:
            #timestamp = datetime.utcfromtimestamp(item["date"])
            #large_photo = item.get("photo_807", item.get("photo_604", item.get("photo_130", "")))
            #i = ImageSearchResult(item["photo_130"], large_photo, timestamp, item["text"], item, self.PROVIDER)
            #results.append(i)
            print item
            pass

        return results


searchproviders = [ImageSearchFacebook, ImageSearchTwitter, ImageSearchInstagram, 
                   ImageSearchVK, ImageSearchGoogleImages, ImageSearchFlickr]
