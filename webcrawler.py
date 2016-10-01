from HTMLParser import HTMLParser
import urllib2
import urlparse
from pybloom import BloomFilter
import Queue
import pdb

class LinkParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = urlparse.urljoin(self.baseUrl, value)
                    self.links = self.links + [newUrl]

    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        response = urllib2.urlopen(url)
        if 'text/html' in response.info().getheader('Content-Type'):
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]

def spider(url, word, maxPages):
    location = urlparse.urlparse(url).netloc
    f = open("{0}_from_{1}.txt".format(word, location[4:-4]), 'w')
    f.write('Host: {0}\n\n'.format(location))

    filter = BloomFilter(capacity=maxPages, error_rate=0.001)
    filter.add(url)
    pagesToVisit = Queue.Queue()
    pagesToVisit.put(url)
    numVisited = 0
    totalWordCount = 0
    pageHitCount = 0

    while numVisited < maxPages and not pagesToVisit.empty():
        numVisited += 1
        url = pagesToVisit.get()
        try:
            print(numVisited, "Visiting: ", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)

            for link in links:
                if not(link in filter):
                    filter.add(url)
                    pagesToVisit.put(link)

            word_count = data.find(word)
            if word_count > -1:
                pageHitCount += 1
                totalWordCount += word_count
                f.write(url)
                f.write(': ')
                f.write(str(word_count))
                f.write('\n')
        except:
            f.write("Failed: {0}\n".format(url))

    f.write('\n\n')
    f.write("Total instances of the word \"{0}\": {1}\n".format(word, str(totalWordCount)))
    f.write("Page hit percentage: {0}\n".format(str(float(pageHitCount) / maxPages * 10)))
    f.write("Average hits for hit pages: {0}\n".format(str(totalWordCount / pageHitCount)))
    f.close()
