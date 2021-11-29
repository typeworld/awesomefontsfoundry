# project
from os import access
from google.cloud.ndb.model import StringProperty
import awesomefontsfoundry
from awesomefontsfoundry import secret, web, definitions

# other
import requests
from flask import g

awesomefontsfoundry.app.config["modules"].append("classes")


###


class TWNDBModel(web.WebAppModel):
    pass


class User(TWNDBModel):
    typeWorldToken = web.StringProperty()
    admin = web.BooleanProperty(default=False)
    purchasedProductKeys = web.KeyProperty(repeated=True)
    secretKey = web.StringProperty()
    accessToken = web.StringProperty()

    # example = {
    #     "data": {
    #         "account": {"email": "post@yanone.de", "name": "Yanone"},
    #         "billingaddress": {
    #             "country": "Germany",
    #             "countryCode": "DE",
    #             "name": "Jan Gerner",
    #             "state": "",
    #             "street": "Altmobschatz 8",
    #             "street2": "",
    #             "town": "Dresden",
    #             "zipcode": "01156",
    #         },
    #         "euvatid": {"euvatid": ""},
    #         "user_id": "cb3f585f-d6c5-4c41-b1fa-70349c6d56a9",
    #     },
    #     "status": "success",
    # }

    def userdata(self):
        if self.typeWorldToken:
            response = requests.post(
                definitions.TYPEWORLD_GETUSERDATA_URL,
                headers={"Authorization": "Bearer " + self.typeWorldToken},
            ).json()
            return response
        else:
            return {"message": "Token is revoked", "status": "fail"}

    def subscriptionURL(self, accessToken=False):
        url = f"typeworld://json+{self.key.id()}:{self.secretKey}@awesomefonts.appspot.com/typeworldapi"
        if accessToken:
            url = url.replace("@", f":{self.accessToken}@")
        return url


class Session(TWNDBModel):
    data = web.JsonProperty()

    def get(self, key):
        data = self.data or {}
        if key in data:
            return data[key]

    def set(self, key, value):
        data = self.data or {}
        data[key] = value
        self.data = data
        self.put()


class Product(TWNDBModel):
    name = web.StringProperty(required=True)
    googleFontsFamilySuffix = web.StringProperty()
    price = web.IntegerProperty(default=39)

    def overview(self, parameters={}, directCallParameters={}):
        g.html.DIV(class_="clear product")
        g.html.DIV(class_="floatleft font", style=f"font-family: '{self.name}';")
        g.html.T(self.name)
        g.html._DIV()
        g.html.DIV(class_="floatright buy")
        g.html.T(f"{self.price}€")
        g.html.BR()
        g.html.A(onclick=f"buy('{self.name}');")
        g.html.T("Buy")
        g.html._A()
        if g.admin:
            g.html.BR()
            self.edit()
        g.html._DIV()
        g.html._DIV()  # .clear

    def cartview(self, parameters={}, directCallParameters={}):
        g.html.DIV(class_="clear cart")
        g.html.DIV(class_="floatleft font")
        g.html.T(self.name)
        g.html.T(f", 1 License")
        g.html._DIV()
        g.html.DIV(class_="floatright buy")
        g.html.T(f"{self.price}€")
        g.html.T("&nbsp;&nbsp;")
        g.html.A(onclick=f"remove('{self.name}');")
        g.html.T("Remove")
        g.html._A()
        g.html._DIV()
        g.html._DIV()  # .clear

    def accountview(self, parameters={}, directCallParameters={}):
        g.html.DIV(class_="clear account")
        g.html.DIV(class_="floatleft font")
        g.html.T(self.name)
        g.html.T(f", 1 License")
        g.html._DIV()
        # g.html.DIV(class_="floatright buy")
        # g.html.T(f"{self.price}€")
        # g.html.T("&nbsp;&nbsp;")
        # g.html.A(onclick=f"remove('{self.name}');")
        # g.html.T("Remove")
        # g.html._A()
        # g.html._DIV()
        g.html._DIV()  # .clear
