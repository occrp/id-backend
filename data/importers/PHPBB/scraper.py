import requests
from BeautifulSoup import BeautifulSoup

class PHPBBMessage:
    def __init__(self, user, text):
        pass


class PHPBBPost:
    def __init__(self, scraper, forum, url, title):
        self.scraper = scraper
        self.url = url
        self.messages = []
        self.users = []

    def scrape(self):
        pass


class PHPBBForum:
    def __init__(self, scraper, url):
        self.scraper = scraper
        self.url = url
        self.posts = []

    def scrape(self):
        soup = self.scraper.get_page(self.url)
        posts = soup.findAll("a", attrs={"class": "forumtitle"})
        for post in posts:
            print "---> %s" % (post.text)
            p = PHPBBPost(self.scraper, self, post['href'], post.text)
            self.posts.append(p)
            p.scrape()


class PHPBBScraper:
    def __init__(self, url):
        self.url = url
        self.forums = []

    def get_page(self, url):
        page = requests.get(url)
        return BeautifulSoup(page.content)

    def get_forum(self, url, title):
        print "Fetching forum '%s':" % title
        forum = PHPBBForum(self, url)
        self.forums.append(forum)
        forum.scrape()

    def scrape(self):
        soup = self.get_page(self.url)
        forumlists = soup.findAll("table", attrs={"class": "forum-list"})
        for forumlist in forumlists:
            forums = forumlist.findAll("a", attrs={"class": "forumtitle"})
            for forum in forums:
                self.get_forum(forum['href'], forum.text)


if __name__ == "__main__":
    p = PHPBBScraper("http://www.mycity-military.com/")
    p.scrape()
