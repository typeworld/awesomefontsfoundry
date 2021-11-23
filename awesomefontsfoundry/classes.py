# project
import awesomefontsfoundry
from awesomefontsfoundry import web, definitions

# other
import requests


awesomefontsfoundry.app.config["modules"].append("classes")


###


class TWNDBModel(web.WebAppModel):
    pass


class User(TWNDBModel):
    typeWorldToken = web.StringProperty()

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
        response = requests.post(
            definitions.TYPEWORLD_GETUSERDATA_URL,
            headers={"Authorization": "Bearer " + self.typeWorldToken},
        ).json()
        if response["status"] == "success":
            return response["data"]
        else:
            return {}


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
