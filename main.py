import webapp2
import urllib2
import json
import logging
from uuid import uuid4
from api_data import *
from google.appengine.ext import ndb
from google.appengine.api import users


class Manifest(ndb.Model):
    version = ndb.StringProperty(required=True)
    checked = ndb.DateTimeProperty(auto_now=True, required=True)


class Collection(ndb.Model):
    name = ndb.StringProperty()
    img = ndb.StringProperty()
    x = ndb.IntegerProperty()
    y = ndb.IntegerProperty()
    order = ndb.IntegerProperty()


class Set(ndb.Model):
    collection = ndb.StringProperty()
    shortname = ndb.StringProperty()
    name = ndb.StringProperty()
    img = ndb.StringProperty()
    x = ndb.IntegerProperty()
    y = ndb.IntegerProperty()
    order = ndb.IntegerProperty()


class Card(ndb.Model):
    set = ndb.StringProperty()
    cardid = ndb.IntegerProperty()
    id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    quote = ndb.StringProperty()
    body = ndb.TextProperty()
    icon = ndb.StringProperty()
    iconx = ndb.IntegerProperty()
    icony = ndb.IntegerProperty()
    img = ndb.StringProperty()
    x = ndb.IntegerProperty()
    y = ndb.IntegerProperty()
    order = ndb.IntegerProperty()


class Gamer(ndb.Model):
    userid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    gamertag = ndb.StringProperty()
    platform = ndb.IntegerProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


class Guide(ndb.Model):
    user = ndb.KeyProperty(kind=Gamer, required=True)
    content = ndb.StringProperty()
    youtube = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True, required=True)


class Rate(ndb.Model):
    user = ndb.KeyProperty(kind=Gamer, required=True)
    guide = ndb.KeyProperty(kind=Guide, required=True)
    rating = ndb.BooleanProperty(required=True)


class CollectionHandler(webapp2.RequestHandler):
    def get(self):
        collections = Collection.query().fetch()
        query = [i.to_dict() for i in collections]
        query = sorted(query,key=lambda k: k.get('order',0))
        collections_json = json.dumps({"type": "collectionfeed", "data": query})
        self.response.write(collections_json)


class SetHandler(webapp2.RequestHandler):
    def post(self):
        data = self.request.body
        query = [i.to_dict() for i in Set.query(Set.collection == data).fetch()]
        query = sorted(query,key=lambda k: k.get('order',0))
        set_json = json.dumps({"type": "setfeed", "set": data, "data": query})
        self.response.write(set_json)


class CardHandler(webapp2.RequestHandler):
    def post(self):
        data = self.request.body
        query = [i.to_dict() for i in Card.query(Card.set == data).fetch()]
        query = sorted(query,key=lambda k: k.get('order',0))
        card_json = json.dumps({"type": "cardfeed", "card": data, "data": query})
        self.response.write(card_json)


class CardViewHandler(webapp2.RequestHandler):
    def post(self):
        data = int(self.request.body)
        guides = [{"user": "Username 1", "guide": "Unlock by playing", "url": "http://www.youtube.com"},
                  {"user": "Username 2", "guide": "Unlock by playin", "url": "http://www.youtube.com"},
                  {"user": "Username 3", "guide": "I dunno", "url": "http://www.youtube.com"}]
        card_json = json.dumps({"type": "guides", "card": data, "data": guides})
        self.response.write(card_json)


class ManifestCollectionHandler(webapp2.RequestHandler):
    def get(self):
        request = urllib2.Request(mani, headers={"x-api-key": api_key})
        doc = urllib2.urlopen(request).read()
        json_object = json.loads(doc)
        server = json_object['Response']['version']                     # 1 finds the latest version online
        database = Manifest.get_by_id(101)                              # 2 looks for the version entry
        manifest_data = Manifest(id=101, version=server)
        if database:                                                    # 3 if local version exists, moves on
            pass
        else:                                                           # 4 if local version doesn't exist,
            manifest_data.put()                                         # write entry with current server version
            populatecollections(define)                                 # and trigger definition storage
        local = database.version                                        # 5 gets local version from entry
        if server == local:                                             # 6 if local and server match, moves on
            del local
            del server
            pass
        else:                                                           # 7 if local and server don't match,
            del local                                                   # deletes local version variable,
            del server                                                  # deletes server version variable
            populatecollections(define)                                 # and trigger definition storage
        manifest_data.put()                                             # 8 writes version (updates checked date)


class ManifestSetHandler(webapp2.RequestHandler):
    def get(self):
        request = urllib2.Request(mani, headers={"x-api-key": api_key})
        doc = urllib2.urlopen(request).read()
        json_object = json.loads(doc)
        server = json_object['Response']['version']                     # 1 finds the latest version online
        database = Manifest.get_by_id(102)                              # 2 looks for the version entry
        manifest_data = Manifest(id=102, version=server)
        if database:                                                    # 3 if local version exists, moves on
            pass
        else:                                                           # 4 if local version doesn't exist,
            manifest_data.put()                                         # write entry with current server version
            populatesets(define)                                        # and trigger definition storage
        local = database.version                                        # 5 gets local version from entry
        if server == local:                                             # 6 if local and server match, moves on
            del local
            del server
            pass
        else:                                                           # 7 if local and server don't match,
            del local                                                   # deletes local version variable,
            del server                                                  # deletes server version variable
            populatesets(define)                                        # and trigger definition storage
        manifest_data.put()                                             # 8 writes version (updates checked date)


class ManifestCardHandler(webapp2.RequestHandler):
    def get(self):
        request = urllib2.Request(mani, headers={"x-api-key": api_key})
        doc = urllib2.urlopen(request).read()
        json_object = json.loads(doc)
        server = json_object['Response']['version']                     # 1 finds the latest version online
        database = Manifest.get_by_id(103)                              # 2 looks for the version entry
        manifest_data = Manifest(id=103, version=server)
        if database:                                                    # 3 if local version exists, moves on
            pass
        else:                                                           # 4 if local version doesn't exist,
            manifest_data.put()                                         # write entry with current server version
            populatecards(define)                                       # and trigger definition storage
        local = database.version                                        # 5 gets local version from entry
        if server == local:                                             # 6 if local and server match, moves on
            del local
            del server
            pass
        else:                                                           # 7 if local and server don't match,
            del local                                                   # deletes local version variable,
            del server                                                  # deletes server version variable
            populatecards(define)                                       # and trigger definition storage
        manifest_data.put()                                             # 8 writes version (updates checked date)


def populatecollections(self):
    request = urllib2.Request(self, headers={"x-api-key": api_key})
    doc = urllib2.urlopen(request).read()
    json_object = json.loads(doc)
    order = 1
    for c in json_object['Response']['themeCollection']:
        cname = c['themeName']
        cid = c['themeId']
        cimg = c['normalResolution']['smallImage']['sheetPath']
        cx = c['normalResolution']['smallImage']['rect']['x']
        cy = c['normalResolution']['smallImage']['rect']['y']
        col1 = Collection(name=cname, img=cimg, x=cx, y=cy, order=order)
        col1.key = ndb.Key(Collection, cid)
        col1.put()
        order += 1


def populatesets(self):
    request = urllib2.Request(self, headers={"x-api-key": api_key})
    doc = urllib2.urlopen(request).read()
    json_object = json.loads(doc)
    for c in json_object['Response']['themeCollection']:
        cid = c['themeId']
        order = 1
        for s in c['pageCollection']:
            colid = cid
            sname = s['pageName']
            sid = s['pageId']
            simg = s['normalResolution']['smallImage']['sheetPath']
            sx = s['normalResolution']['smallImage']['rect']['x']
            sy = s['normalResolution']['smallImage']['rect']['y']
            set1 = Set(collection=colid, name=sname, shortname=sid, img=simg, x=sx, y=sy, order=order)
            set1.key = ndb.Key(Set, sid)
            set1.put()
            order += 1


def populatecards(self):
    request = urllib2.Request(self, headers={"x-api-key": api_key})
    doc = urllib2.urlopen(request).read()
    json_object = json.loads(doc)
    for c in json_object['Response']['themeCollection']:
        for s in c['pageCollection']:
            sid = s['pageId']
            order = 1
            for ca in s['cardCollection']:
                setid = sid
                caid = ca['cardId']
                caname = ca['cardName']
                cabody = ca['cardDescription']
                caicon = ca['normalResolution']['smallImage']['sheetPath']
                caix = ca['normalResolution']['smallImage']['rect']['x']
                caiy = ca['normalResolution']['smallImage']['rect']['y']
                caimg = ca['normalResolution']['image']['sheetPath']
                cax = ca['normalResolution']['image']['rect']['x']
                cay = ca['normalResolution']['image']['rect']['y']
                if 'cardIntro' not in ca:
                    caquote = '&nbsp;'
                else:
                    caquote = ca['cardIntro']
                card1 = Card(set=setid, id=caid, cardid=caid, name=caname, quote=caquote, body=cabody, icon=caicon,
                             iconx=caix, icony=caiy, img=caimg, x=cax, y=cay, order=order)
                card1.key = ndb.Key(Card, caid)
                card1.put()
                order += 1


app = webapp2.WSGIApplication([
    ('/grim', CollectionHandler),
    ('/set', SetHandler),
    ('/card', CardHandler),
    ('/getcollections', ManifestCollectionHandler),
    ('/getsets', ManifestSetHandler),
    ('/getcards', ManifestCardHandler),
    ('/cardview', CardViewHandler)
], debug=True)
