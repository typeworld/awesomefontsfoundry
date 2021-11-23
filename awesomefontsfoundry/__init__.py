import logging
import os
import time

from google.cloud import ndb, storage
from google.cloud import secretmanager
from flask import Flask, g, request
from flask import session as flaskSession

logging.basicConfig(level=logging.WARNING)

# Google
client = ndb.Client()

# Google Cloud Secrets
secretClient = secretmanager.SecretManagerServiceClient()

# Google Cloud Storage
storage_client = storage.Client()
bucket = storage_client.bucket("awesomefonts")

GAE = os.getenv("GAE_ENV", "").startswith("standard")
LIVE = GAE

# Pre-initialize datastore context
def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


app = Flask(__name__)
app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)  # Wrap the app in middleware.
app.config["modules"] = ["__main__"]

# Local imports
# happen here because of circular imports,
from . import classes  # noqa: E402
from . import hypertext  # noqa: E402
from . import web  # noqa: E402,F401


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

    if not g.user and "sessionID" in flaskSession:
        sessionID = flaskSession["sessionID"]
        if sessionID:

            g.session = ndb.Key(urlsafe=flaskSession["sessionID"].encode()).get(read_consistency=ndb.STRONG)

            # Init user
            if g.session:
                g.user = g.session.getUser()
                if g.user:
                    g.admin = g.user.admin
                else:
                    g.session.key.delete()


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


@app.route("/", methods=["GET"])
def index():

    g.html.H1()
    g.html.T("Welcome to Awesome Fonts")
    g.html._H1()

    return g.html.generate()


def performLogin(user):
    # Create session
    session = classes.Session()
    session.userKey = user.key
    session.putnow()

    g.user = user
    g.admin = g.user.admin

    flaskSession["sessionID"] = session.key.urlsafe().decode()


def performLogout():
    if g.session:
        g.session.key.delete()
    g.session = None
    g.user = None
    g.admin = False

    flaskSession.clear()


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
    performLogout()
    return "<script>location.reload();</script>"


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
    # [END gae_python37_app]

print("READY...")
