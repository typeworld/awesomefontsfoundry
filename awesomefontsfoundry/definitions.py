import awesomefontsfoundry

TYPEWORLD_SIGNIN_CLIENTID = "4XZ3b0cPdMkVMQF3Sm5bxT92fOczbE9sHtq6Gchs"
TYPEWORLD_SIGNIN_CLIENTSECRET = "tFGYpe9TU4PftILdWW1mNvyaXOPNP3lzMC4MhjiC"
TYPEWORLD_SIGNIN_SCOPE = "account,billingaddress,euvatid"

if awesomefontsfoundry.GAE:
    TYPEWORLD_SIGNIN_URL = "https://type.world/signin"
    TYPEWORLD_GETTOKEN_URL = "https://type.world/auth/token"
    TYPEWORLD_GETUSERDATA_URL = "https://type.world/auth/userdata"
    ROOT = "https%3A%2F%2Fawesomefonts.appspot.com"
else:
    TYPEWORLD_SIGNIN_URL = "http://0.0.0.0/signin"
    TYPEWORLD_GETTOKEN_URL = "http://0.0.0.0/auth/token"
    TYPEWORLD_GETUSERDATA_URL = "http://0.0.0.0/auth/userdata"
    ROOT = "http%3A%2F%2F0.0.0.0%3A8080"
