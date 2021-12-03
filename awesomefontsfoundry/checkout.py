import awesomefontsfoundry
from awesomefontsfoundry import classes, definitions, account, helpers
from flask import g
import requests
from awesomefontsfoundry.helpers import Garbage
from awesomefontsfoundry.web import resetpassword


@awesomefontsfoundry.app.route("/cart", methods=["GET", "POST"])
def cart():

    g.html.DIV(class_="content", style="width: 700px;")

    g.html.H1()
    g.html.T("Shopping Cart")
    g.html._H1()

    products = g.session.get("cart")
    sum = 0
    if products:
        for productName in products:
            product = classes.Product.query(classes.Product.name == productName).get()
            product.container("cartview")
            sum += product.price

        g.html.DIV(class_="clear cart")
        g.html.DIV(class_="floatleft font")
        g.html.T("<b>Total</b>")
        g.html._DIV()
        g.html.DIV(class_="floatright buy")
        g.html.T(f"<b>{sum}€</b>")
        g.html._DIV()
        g.html._DIV()  # .clear

        g.html.separator()

        g.html.P(style="text-align: center;")
        g.html.SPAN(class_="link")
        g.html.A(href="/checkout")
        g.html.T('<span class="material-icons-outlined">shopping_cart_checkout</span> Proceed to Checkout')
        g.html._A()
        g.html._SPAN()
        g.html._P()

    else:
        g.html.T('You don’t have any products in your cart yet. <a href="/">Continue shopping</a>.')

    g.html._DIV()  # .content

    return g.html.generate()


@awesomefontsfoundry.app.route("/checkout", methods=["GET", "POST"])
def checkout():

    g.html.DIV(class_="content", style="width: 700px;")

    g.html.H1()
    g.html.T("Checkout")
    g.html._H1()

    if not g.user:

        g.html.P()
        g.html.T("You’re not signed in.<br />Please sign in with your Type.World account below:")
        g.html._P()

        g.html.P()
        g.html.SPAN(class_="link")
        g.html.A(
            onclick=(
                f"login('{definitions.TYPEWORLD_SIGNIN_URL}',"
                f" '{awesomefontsfoundry.secret('TYPEWORLD_SIGNIN_CLIENTID')}', window.location.href,"
                f" '{definitions.TYPEWORLD_SIGNIN_SCOPE}', '{g.session.get('loginCode')}')"
            )
        )
        g.html.T('<span class="material-icons-outlined">login</span> Sign In with Type.World')
        g.html._A()
        g.html._SPAN()
        g.html._P()

    else:

        g.html.P()
        g.html.T("Please povide your payment details below:")
        g.html._P()

        g.html.P()
        g.html.T('<span class="material-icons-outlined">credit_card</span> Credit Card Number')
        g.html.BR()
        tooltip = "You can use the fake credit card number 1234&nbsp;0000&nbsp;0000&nbsp;0000 here."
        g.html.INPUT(
            type="text",
            id="creditcard",
            placeholder="0000 0000 0000 0000",
            title=awesomefontsfoundry.tooltip("creditcard", tooltip),
            alt=tooltip,
        )
        g.html._P()

        account.printUserData()

        g.html.mediumSeparator()

        g.html.P()
        g.html.SPAN(class_="link")
        g.html.A(onclick="checkout();")
        g.html.T('<span class="material-icons-outlined">shopping_cart_checkout</span> Buy Fonts')
        g.html._A()
        g.html._SPAN()
        g.html._P()

    g.html._DIV()  # .content

    return g.html.generate()


@awesomefontsfoundry.app.route("/done", methods=["GET", "POST"])
def done():

    g.html.DIV(class_="content", style="width: 700px;")

    g.html.H1()
    g.html.T("Thank you for shopping with Awesome Fonts")
    g.html._H1()

    g.html.P()
    g.html.T(
        'We sent you an invitation to install the purchased fonts via the <a href="https://type.world"'
        ' target="_blank">Type.World</a> app to your Type.World user account at '
        f' <b>{g.user.userdata()["userdata"]["scope"]["account"]["data"]["email"]}</b>'
    )
    g.html._P()

    g.html.P()
    g.html.T('Additionally, you can download the fonts via the <a href="/account">User Account</a>')
    g.html._P()

    g.html._DIV()  # .content

    return g.html.generate()


@awesomefontsfoundry.app.route("/cart/checkout", methods=["GET", "POST"])
def cart_checkout():

    # Add products to user account
    products = g.session.get("cart")
    for productName in products:
        product = classes.Product.query(classes.Product.name == productName).get()
        if product.key not in g.user.purchasedProductKeys:
            g.user.purchasedProductKeys.append(product.key)

    # Type.World API Secret Key
    if not g.user.secretKey:
        g.user.secretKey = helpers.Garbage(40)

    # Type.World API Access token
    g.user.accessToken = helpers.Garbage(40)
    g.user.put()

    # Reset Cart
    g.session.set("cart", [])

    # Update subscription
    url = g.user.subscriptionURL()
    parameters = {
        "APIKey": awesomefontsfoundry.secret("TYPEWORLD_API_KEY"),
        "subscriptionURL": url,
    }
    print("updateSubscription")
    print("updateSubscription parameters", parameters)
    response = requests.post("https://api.type.world/v1/updateSubscription", data=parameters).json()
    print("updateSubscription response", response)

    # Invite user to share subscription
    url = g.user.subscriptionURL()
    parameters = {
        "targetUserEmail": g.user.userdata()["userdata"]["scope"]["account"]["data"]["email"],
        "APIKey": awesomefontsfoundry.secret("TYPEWORLD_API_KEY"),
        "subscriptionURL": url,
    }
    print("inviteUserToSubscription")
    print("inviteUserToSubscription parameters", parameters)
    response = requests.post("https://api.type.world/v1/inviteUserToSubscription", data=parameters).json()
    print("inviteUserToSubscription response", response)

    return "<script>window.location.href='/done';</script>"


@awesomefontsfoundry.app.route("/cart/add", methods=["POST"])
def cart_add():

    assert g.form._get("products")

    products = g.session.get("cart") or []
    for product in g.form._get("products").split(","):
        if product not in products:
            products.append(product)
    g.session.set("cart", products)

    return "<script>window.location.reload();</script>"


@awesomefontsfoundry.app.route("/cart/remove", methods=["POST"])
def cart_remove():

    assert g.form._get("products")

    products = g.session.get("cart") or []
    for product in g.form._get("products").split(","):
        products.remove(product)
    g.session.set("cart", products)

    return "<script>window.location.reload();</script>"
