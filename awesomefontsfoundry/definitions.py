import awesomefontsfoundry

TYPEWORLD_SIGNIN_SCOPE = "account,billingaddress,euvatid"

if awesomefontsfoundry.GAE:
    TYPEWORLD_SIGNIN_URL = "https://type.world/signin"
    TYPEWORLD_GETTOKEN_URL = "https://type.world/auth/token"
    TYPEWORLD_GETUSERDATA_URL = "https://type.world/auth/userdata"
    ROOT = "https://awesomefonts.appspot.com"

else:
    TYPEWORLD_SIGNIN_URL = "http://0.0.0.0/signin"
    TYPEWORLD_GETTOKEN_URL = "http://0.0.0.0/auth/token"
    TYPEWORLD_GETUSERDATA_URL = "http://0.0.0.0/auth/userdata"
    ROOT = "http://0.0.0.0:8080"
