import urllib
import urllib2
import json
from datetime import datetime
import dateutil.parser
from threading import Thread
from core.utils import json_dumps, Credentials

from id.apis.elastic import elastic
# from id.apis.googledrive import drive_decorator, Drive
from id.apis import opencorporates
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from apiclient.discovery import build
from apiclient.errors import HttpError

class ImageSearchResult(dict):
    def __init__(self, provider, imageurl, resulturl, timestamp, caption, 
                 linkurl=None, linktitle=None, metadata={}):
        self["provider"] = provider
        self["timestamp"] = timestamp
        self["image_url"] = imageurl
        self["result_url"] = resulturl
        self["caption"] = caption
        self["metadata"] = metadata
        self["link"] = linkurl
        self["linktitle"] = linktitle


class Searcher:
    def start(self, search):
        thread = Thread(target=self.run, args=(search,))
        thread.start()

    def json_api_request(self, meta, force_get=False):
        print "Search:%s:%s:Hitting: %s?%s" % (self.TYPE, self.PROVIDER, self.URL, urllib.urlencode(meta))
        params = urllib.urlencode(meta)
        if force_get:
            r = urllib2.urlopen(self.URL + "?" + params)
        else:
            r = urllib2.urlopen(self.URL, params)
        return json.loads(r.read())

    def prepare_query(self, q):
        # Default query preparation is idempotent
        return q

    def run(self, search):
        runner = search.create_runner(self.PROVIDER)

        query = self.prepare_query(json.loads(search.query))
        results = self.search(**query)
        for r in results:
            search.create_result(self.PROVIDER, r)

        runner.done = True
        runner.results = len(results)
        runner.save()


class SocialSearcher(Searcher):
    TYPE = "social"

class DocumentSearcher(Searcher):
    TYPE = "document"

    def prepare_query(self, query):
        r = {}
        r["q"] = query["q"].encode("utf-8")
        if query["startdate"]:
            r["startdate"] = dateutil.parser.parse(query["startdate"])
        if query["enddate"]:
            r["enddate"] = dateutil.parser.parse(query["enddate"])
        return r

class ImageSearcher(Searcher):
    TYPE = "image"

    def prepare_query(self, query):
        r = {}
        r["q"] = query["q"].encode("utf-8")
        r["lat"] = query["lat"]
        r["lon"] = query["lon"]
        r["radius"] = query["radius"]
        if query["startdate"]:
            r["startdate"] = dateutil.parser.parse(query["startdate"])
        if query["enddate"]:
            r["enddate"] = dateutil.parser.parse(query["enddate"])
        r["offset"] = query["offset"]
        r["count"] = query["count"]
        return r


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


class ImageSearchInstagram(ImageSearcher):
    # https://instagram.com/developer/endpoints/media/
    # https://instagram.com/accounts/login/?next=%2Fdeveloper%2Fregister%2F
    # https://github.com/Instagram/python-instagram/blob/master/README.md
    # https://instagram.com/developer/endpoints/media/#get_media_search
    # you can only create an account via the mobile app o_O'
    # 
    PROVIDER = "Instagram"
    URL = "https://api.instagram.com/v1/media/search"

    def search(self, q, lat, lon, radius, startdate, enddate, offset, count):
        # results
        results = []
        
        # search metadata
        meta = {}
        meta["access_token"] = Credentials().get("instagram", "access_token")
        #meta["q"] = q
        meta["lat"] = lat
        meta["lng"] = lon
        if startdate:
            meta["min_timestamp"] = startdate.strftime("%s")
        if enddate:
            meta["max_timestamp"] = enddate.strftime("%s")
        if radius > 5000: radius = 5000
        meta["distance"] = radius

        data = self.json_api_request(meta, force_get=True)
        for item in data["data"]:
            caption = ""
            if item.get("caption"):
                caption = item.get("caption").get("text", "")

            i = ImageSearchResult(
                provider=self.PROVIDER,
                imageurl=item["images"]["low_resolution"]["url"], 
                resulturl=item["link"], 
                timestamp=datetime.utcfromtimestamp(float(item["created_time"])),
                caption=caption,
                linkurl=item["link"],
                linktitle=item["user"]["full_name"],
                metadata=item)
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
    PROVIDER = "YouTube"
    URL = "https://www.googleapis.com/youtube/v3/search"

    def search(self, q, lat=None, lon=None, radius=50000, startdate=None, enddate=None, offset=0, count=50):
        http = Credentials().get_oauth2_http("google", scope='https://www.googleapis.com/auth/youtube.readonly')

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
            i = ImageSearchResult(self.PROVIDER, thumbnail, link, timestamp, caption, item)
            results.append(i)

        return results


class EntitySearchOpenCorporates(DocumentSearcher):
    PROVIDER = "OpenCorporates"
    SEARCHER = opencorporates.OpenCorpSearch()

    def _search(self, q, offset=0, limit=100, **kwargs):
        results = self.SEARCHER.search(q, offset, limit)
        self.result_count = results.resultcount
        return results.resultdata


class DocumentSearchElasticSearch(DocumentSearcher):
    PROVIDER = "ElasticSearch"

    def _search(self, q, offset, limit, **kwargs):
        results = elastic.search(query,offset=offset,
                                 limit=limit,
                                 index='id_prod', **kwargs)
        self.result_count = results['hits']['total']
        return results['hits']['hits']



searchproviders = [ImageSearchInstagram, ImageSearchVK, ImageSearchYouTube, DocumentSearchElasticSearch]
# ImageSearchFacebook, ImageSearchTwitter, ImageSearchGoogleImages, ImageSearchFlickr, EntitySearchOpenCorporates
