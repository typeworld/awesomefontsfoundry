# project
import awesomefontsfoundry
from awesomefontsfoundry import web

# other
from google.cloud import ndb


awesomefontsfoundry.app.config["modules"].append("classes")


###


class TWNDBModel(web.WebAppModel):
    pass


class User(TWNDBModel):
    typeWorldUserID = web.StringProperty(required=True)


class Session(TWNDBModel):
    userKey = web.KeyProperty(required=True)

    def getUser(self):
        if self.userKey:
            return self.userKey.get(read_consistency=ndb.STRONG)
