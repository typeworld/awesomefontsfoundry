import logging
import os
import time
from google.cloud.ndb.model import Expando
import requests
from google.cloud import ndb
from google.cloud import secretmanager
from flask import Flask, g, request, Response
from flask import session as flaskSession

# from flask_session import Session

# from flask_session import Session

logging.basicConfig(level=logging.WARNING)
GAE = os.getenv("GAE_ENV", "").startswith("standard")

# Google
if GAE:
    client = ndb.Client()
    secretClient = secretmanager.SecretManagerServiceClient()
else:
    keyfile = os.path.join(os.path.dirname(__file__), "..", ".secrets", "awesomefonts-b36861fed221.json")
    client = ndb.Client.from_service_account_json(keyfile)
    secretClient = secretmanager.SecretManagerServiceClient.from_service_account_json(keyfile)


def secret(secret_id, version_id="latest"):
    """
    Access Google Cloud Secrets
    https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#access
    """
    name = f"projects/293955791033/secrets/{secret_id}/versions/{version_id}"
    response = secretClient.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


# Pre-initialize datastore context
def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


app = Flask(__name__)
app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)  # Wrap the app in middleware.
app.secret_key = secret("FLASK_SECRET_KEY")
app.config.update(SESSION_COOKIE_NAME="awesomefonts")
app.config["modules"] = ["__main__"]

# Local imports
# happen here because of circular imports,
from . import account  # noqa: E402,F401
from . import classes  # noqa: E402
from . import checkout  # noqa: E402
from . import definitions  # noqa: E402
from . import helpers  # noqa: E402
from . import hypertext  # noqa: E402
from . import web  # noqa: E402,F401
from . import typeworldapi  # noqa: E402,F401


def tooltip(name, text):

    tooltips = g.session.get("tooltips") or []
    if name not in tooltips:
        tooltips.append(name)
        g.session.set("tooltips", tooltips)
        return text


@app.before_request
def before_request():

    if "GAE_VERSION" in os.environ:
        g.instanceVersion = os.environ["GAE_VERSION"]
    else:
        g.instanceVersion = str(int(time.time()))

    g.user = None
    g.admin = None
    g.session = None
    g.ndb_puts = []
    g.html = hypertext.HTML()

    # Session
    # flaskSession.permanent = True
    if "sessionID" in flaskSession and flaskSession["sessionID"]:
        sessionID = flaskSession["sessionID"]
        g.session = ndb.Key(urlsafe=sessionID.encode()).get(read_consistency=ndb.STRONG)
    else:
        g.session = classes.Session()
        g.session.put()
        flaskSession["sessionID"] = g.session.key.urlsafe().decode()

    # Set random loginCode
    if not g.session.get("loginCode"):
        g.session.set("loginCode", helpers.Garbage(40))

    # Catch Type.World Sign In here
    if g.form._get("code") and g.form._get("state") and g.form._get("state") == g.session.get("loginCode"):

        # Get token with code
        getTokenResponse = requests.post(
            definitions.TYPEWORLD_GETTOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": g.form._get("code"),
                "redirect_uri": "http://0.0.0.0:8080",
                "client_id": secret("TYPEWORLD_SIGNIN_CLIENTID"),
                "client_secret": secret("TYPEWORLD_SIGNIN_CLIENTSECRET"),
            },
        ).json()

        # Redeem token for user data
        if getTokenResponse["status"] == "success":
            getUserDataResponse = requests.post(
                definitions.TYPEWORLD_GETUSERDATA_URL,
                headers={"Authorization": "Bearer " + getTokenResponse["access_token"]},
            ).json()
            # Create user if necessary and save token
            if getUserDataResponse["status"] == "success":
                user = classes.User.get_or_insert(getUserDataResponse["userdata"]["user_id"])
                user.typeWorldToken = getTokenResponse["access_token"]
                user.put()
                g.session.set("userID", user.userdata()["userdata"]["user_id"])
                g.user = user

                g.html.SCRIPT()
                g.html.T("window.history.pushState('', '', window.location.href.split('?')[0]);")
                g.html._SCRIPT()

    # Restore user from session
    else:
        if g.session.get("userID"):
            g.user = classes.User.get_or_insert(g.session.get("userID"))

    # Test token
    if g.user:
        try:
            response = g.user.userdata()
            if response["status"] == "fail":
                g.user.typeWorldToken = None
                g.user.put()
                g.user = None
                g.session.set("loginCode", helpers.Garbage(40))
        except Exception:
            g.user = None

    # Admin
    if g.user and g.user.admin:
        g.admin = True


@app.after_request
def after_request(response):

    if response.mimetype == "text/html":

        html = hypertext.HTML()

        if g.form._get("inline") == "true" or "</body>" in response.get_data().decode():
            pass

        else:

            response.direct_passthrough = False

            html.header()
            html.T("---replace---")
            html.footer()

            html = html.GeneratePage()
            html = html.replace("---replace---", response.get_data().decode())
            response.set_data(html)

    if g.ndb_puts:
        ndb.put_multi(g.ndb_puts)
        for object in g.ndb_puts:
            object._cleanupPut()
        g.ndb_puts = []

    return response


@app.route("/", methods=["GET", "POST"])
def index():

    g.html.DIV(class_="content", style="width: 700px;")

    # g.html.H1()
    # if g.user:
    #     g.html.T(
    #         f"Hello {g.user.userdata()['userdata']['scope']['account']['data']['name']},<br />Welcome to Awesome Fonts"
    #     )
    # else:
    #     g.html.T("Welcome to Awesome Fonts")
    # g.html._H1()

    if g.admin:
        g.html.P()
        classes.Product().new()
        g.html._P()

    googleFontsFamilies = []
    for product in classes.Product.query().fetch():
        product.container("overview")
        string = product.name
        if product.googleFontsFamilySuffix:
            string += product.googleFontsFamilySuffix
        googleFontsFamilies.append(string)

    familyCode = "&".join(("family=" + x) for x in googleFontsFamilies).replace(" ", "+")
    g.html.T(
        f"""

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{familyCode}&display=swap" rel="stylesheet">    
    """
    )

    g.html._DIV()  # .content

    return g.html.generate()


def performLogin(user):
    # Create session
    # session = classes.Session()
    # session.userKey = user.key
    # session.putnow()

    g.user = user
    g.admin = g.user.admin

    # flaskSession["sessionID"] = session.key.urlsafe().decode()


@app.route("/login", methods=["POST"])
def login():

    user = (
        classes.User.query()
        .filter(classes.User.email == request.values.get("username"))
        .get(read_consistency=ndb.STRONG)
    )

    if not user:
        return "<script>warning('Unknown user');</script>"

    if not user.checkPassword(request.values.get("password")):
        return "<script>warning('Wrong password');</script>"

    performLogin(user)
    return "<script>location.reload();</script>"


@app.route("/logout", methods=["POST"])
def logout():

    g.user = None
    g.admin = False

    # Set random loginCode
    g.session.set("loginCode", helpers.Garbage(40))
    g.session.set("userID", None)

    return "<script>window.location.reload();</script>"


@app.route("/resettooltips", methods=["GET"])
def resettooltips():

    g.session.set("tooltips", [])

    return Response("ok", 200, mimetype="text/plain")


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
    # [END gae_python37_app]

print("READY...")
