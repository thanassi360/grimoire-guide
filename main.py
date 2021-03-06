import webapp2
import urllib2
import json
import re
import datetime
from uuid import uuid4
from api_data import *
from google.appengine.ext import ndb
from google.appengine.api import users


class TimeEncoder(json.JSONEncoder):  # Defines time format
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%d/%m/%Y %H:%M')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%d/%m/%Y')


class Manifest(ndb.Model):  # Defines Manifest entities
    version = ndb.StringProperty(required=True)
    checked = ndb.DateTimeProperty(auto_now=True, required=True)


class Collection(ndb.Model):  # Defines Collection entities
    name = ndb.StringProperty()
    img = ndb.StringProperty()
    x = ndb.IntegerProperty()
    y = ndb.IntegerProperty()
    order = ndb.IntegerProperty()


class Set(ndb.Model):  # Defines Set entities
    collection = ndb.StringProperty()
    shortname = ndb.StringProperty()
    name = ndb.StringProperty()
    img = ndb.StringProperty()
    x = ndb.IntegerProperty()
    y = ndb.IntegerProperty()
    order = ndb.IntegerProperty()


class Card(ndb.Model):  # Defines Card entities
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


class User(ndb.Model):  # Defines User entities
    userid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    gamertag = ndb.StringProperty()
    platform = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def tojson(self):
        return '{"user": "%s",' \
               '"name": "%s",' \
               '"email": "%s",' \
               '"gamertag": "%s",' \
               '"platform": "%s",' \
               '"joined": "%s"}' % (self.userid,
                                    self.name,
                                    self.email,
                                    self.gamertag,
                                    self.platform,
                                    self.joined.strftime("%d/%m/%Y"))


class Guide(ndb.Model):  # Defines Guide entities
    userid = ndb.KeyProperty(kind=User, required=True)
    cardid = ndb.IntegerProperty(required=True)
    content = ndb.StringProperty()
    gid = ndb.StringProperty()
    youtube = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True, required=True)


class CollectionHandler(webapp2.RequestHandler):  # Checks user and gets collection data
    def get(self):
        collections = Collection.query().fetch()
        user = users.get_current_user()
        if not user:
            current = "NotLoggedIn"
        else:
            currentuser = User.get_by_id(user.user_id())
            current = currentuser.name
        query = [i.to_dict() for i in collections]
        query = sorted(query, key=lambda k: k.get('order', 0))
        collections_json = json.dumps({"type": "collectionfeed", "name": current, "data": query})
        self.response.write(collections_json)


class SetHandler(webapp2.RequestHandler):  # Gets set data
    def post(self):
        data = self.request.body
        query = [i.to_dict() for i in Set.query(Set.collection == data).fetch()]
        query = sorted(query, key=lambda k: k.get('order', 0))
        set_json = json.dumps({"type": "setfeed", "set": data, "data": query})
        self.response.write(set_json)


class CardHandler(webapp2.RequestHandler):  # Gets card data
    def post(self):
        data = self.request.body
        query = [i.to_dict() for i in Card.query(Card.set == data).fetch()]
        query = sorted(query, key=lambda k: k.get('order', 0))
        card_json = json.dumps({"type": "cardfeed", "card": data, "data": query})
        self.response.write(card_json)


class CardViewHandler(webapp2.RequestHandler):  # Gets guide data for a card
    def post(self):
        data = int(self.request.body)
        guides = Guide.query(Guide.cardid == data).fetch()
        guidelist = []
        currentuser = users.get_current_user()
        if currentuser:
            username = users.get_current_user().user_id()
        else:
            username = "NotAUser"
        for guide in guides:
            if guide.userid.get().userid == username:
                current = "true"
            else:
                current = "false"
            name = guide.userid.get().name
            response = {
                'user': name,
                'content': guide.content,
                'youtube': guide.youtube,
                'created': guide.created.strftime("%H:%M %d/%m/%Y"),
                'id': guide.gid,
                'current': current
            }
            guidelist.append(response)
        self.response.write(json.dumps(guidelist))


class LoginHandler(webapp2.RequestHandler):  # Logs a user in or registers new user
    def get(self):
        currentuser = users.get_current_user()
        if currentuser:
            find = User.query(User.userid == currentuser.user_id()).fetch()
            if find:
                user = users.get_current_user().user_id()
                callback = self.request.get("callback")
                self.request.headers["Content-Type"] = 'application/json'
                current = User.query(User.userid == user)
                sresponse = ""
                jsonop = None
                for user in current:
                    sresponse += user.tojson()
                    if callback is '':
                        jsonop = sresponse
                    else:
                        jsonop = callback+"("+sresponse+")"
                self.response.write(jsonop)
            else:
                guid = str(uuid4())
                user = User(userid=currentuser.user_id(),
                            email=currentuser.email(),
                            name=guid,
                            index=guid.lower())
                user.key = ndb.Key(User, currentuser.user_id())
                user.put()
        else:
            self.redirect(users.create_login_url('/loggedin'))


class LogoutHandler(webapp2.RequestHandler):  # Logs user out
    def post(self):
        self.redirect(users.create_logout_url('/'))


class UpdateHandler(webapp2.RequestHandler):  # Updates users details
    def post(self):
        data = json.loads(self.request.body)
        name = data["name"]
        gamertag = data["gamertag"]
        platform = data["platform"]
        min_len = 4
        max_len = 15
        pattern = r"^(?i)[a-z0-9_-]{%s,%s}$" % (min_len, max_len)
        user = users.get_current_user().user_id()
        currentuser = User.get_by_id(user)
        checkavail = User.query(User.index == name.lower()).fetch()
        if checkavail:
            currentuser.gamertag = gamertag
            currentuser.platform = platform
            currentuser.put()
            stat = "userexists"
            msg = "Profile updated, except Username (already in use)."
            usr = currentuser.name
        else:
            if re.match(pattern, name):  # regular expression to ensure that the username entered is valid
                currentuser.name = name
                currentuser.index = name.lower()
                currentuser.platform = platform
                currentuser.gamertag = gamertag
                currentuser.put()
                stat = "updated"
                msg = "Profile updated successfully."
                usr = name
            else:
                stat = "failed"
                msg = "Please check the details you inputted."
                usr = currentuser.name
        status = json.dumps({"status": stat, "msg": msg, "user": usr})
        self.response.write(status)


class GuideHandler(webapp2.RedirectHandler):  # Saves users guide for a card
    def post(self):
        data = json.loads(self.request.body)
        cardid = data["card"]
        guide = data["body"]
        url = data["link"]
        user = users.get_current_user().user_id()
        userid = ndb.Key(User, user)
        ident = "G"+str(cardid) + str(user)
        guideobj = Guide(gid=ident, userid=userid, cardid=cardid, content=guide, youtube=url)
        guideobj.key = ndb.Key(Guide, ident)
        guideobj.put()
        stat = "Guide Saved"
        status = json.dumps({"status": stat})
        self.response.write(status)


class ManifestCollectionHandler(webapp2.RequestHandler):  # Cron jobs is set to check Bungie.net DB version for Collections
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


class ManifestSetHandler(webapp2.RequestHandler):  # Cron jobs is set to check Bungie.net DB version for Sets
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


class ManifestCardHandler(webapp2.RequestHandler):  # Cron jobs is set to check Bungie.net DB version for Cards
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


def populatecollections(self):  # Populates Collections
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


def populatesets(self):  # Populates Sets
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


def populatecards(self):  # Populates Cards
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
                card1.key = ndb.Key(Card, str(caid))
                card1.put()
                order += 1


app = webapp2.WSGIApplication([
    ('/grim', CollectionHandler),
    ('/set', SetHandler),
    ('/card', CardHandler),
    ('/getcollections', ManifestCollectionHandler),
    ('/getsets', ManifestSetHandler),
    ('/getcards', ManifestCardHandler),
    ('/cardview', CardViewHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/guide', GuideHandler),
    ('/update', UpdateHandler)
], debug=True)
