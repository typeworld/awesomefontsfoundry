# project
import awesomefontsfoundry
from awesomefontsfoundry import definitions

# other
import urllib.parse
from flask import g


awesomefontsfoundry.app.config["modules"].append("account")


def printUserData(userdata=None):

    if not userdata:
        userdata = g.user.userdata()["userdata"]

    for scope in userdata["scope"]:
        g.html.H3()
        g.html.T(userdata["scope"][scope]["name"])
        if "edit_uri" in userdata["scope"][scope]:
            g.html.T(" ")
            g.html.A(onclick=f"edit('{userdata['scope'][scope]['edit_uri']}', window.location.href);")
            g.html.T('(<span class="material-icons-outlined">edit</span> Edit)')
            g.html._A()
        g.html._H3()

        g.html.P()
        for value in userdata["scope"][scope]["data"]:
            if value not in ["country_code"]:
                g.html.T(userdata["scope"][scope]["data"][value] or '<span style="opacity: .5;">&lt;empty&gt;</span>')
                g.html.BR()
        g.html._P()


@awesomefontsfoundry.app.route("/account", methods=["GET", "POST"])
def account():

    if not g.user:
        return "<script>window.location.href='/';</script>"

    userdata = g.user.userdata()["userdata"]

    g.html.DIV(class_="content", style="width: 700px;")

    g.html.H1()
    g.html.T("User Account")
    g.html._H1()

    printUserData(userdata)

    if g.user.purchasedProductKeys:

        g.html.mediumSeparator()
        g.html.H1()
        g.html.T("Purchased Fonts")
        g.html._H1()
        for key in g.user.purchasedProductKeys:
            product = key.get()
            product.container("accountview")

        g.html.mediumSeparator()
        g.html.H1()
        g.html.T("Install in Type.World&nbsp;App")
        g.html._H1()
        g.html.P()
        g.html.A(href=g.user.subscriptionURL(accessToken=True))
        g.html.T('<span class="material-icons-outlined">file_download</span> Install in Type.World App')
        g.html._A()
        g.html._P()

    g.html._DIV()  # .content

    return g.html.generate()
