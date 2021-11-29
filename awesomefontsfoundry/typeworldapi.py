import awesomefontsfoundry
from awesomefontsfoundry import classes
from flask import request, Response
import typeworld

from awesomefontsfoundry import helpers


@awesomefontsfoundry.app.route("/typeworldapi", methods=["POST"])
def api():

    commands = request.values.get("commands")
    if not commands:
        return handleAbort(404)

    commandsList = commands.split(",")
    subscriptionID = request.values.get("subscriptionID")
    secretKey = request.values.get("secretKey")
    accessToken = request.values.get("accessToken")
    fonts = request.values.get("fonts")
    anonymousAppID = request.values.get("anonymousAppID")
    anonymousTypeWorldUserID = request.values.get("anonymousTypeWorldUserID")
    userName = request.values.get("userName")
    userEmail = request.values.get("userEmail")
    appVersion = request.values.get("appVersion")
    verifiedTypeWorldUserCredentials = None

    # API Root
    root = typeworld.api.RootResponse()
    subscriptionURL = f"typeworld://json+{subscriptionID}:{secretKey}@awesomefonts.appspot.com/typeworldapi"
    APIKey = awesomefontsfoundry.secret("TYPEWORLD_API_KEY")
    incomingAPIKey = request.values.get("APIKey")

    # Process the commands in the order they were given.
    for command in commandsList:
        if command == "endpoint":

            # Call endpoint()
            success, message = endpoint(root)

            # Process: Return value is of type integer, which means we handle a request abort with HTTP code
            if not success and type(message) == int:
                return handleAbort(message)

        # Call installableFonts() method, hand over root object to fill with data
        elif command == "installableFonts":

            # Call installableFonts()
            success, message = installableFonts(
                root,
                subscriptionURL,
                APIKey,
                subscriptionID,
                secretKey,
                accessToken,
                anonymousAppID,
                anonymousTypeWorldUserID,
                verifiedTypeWorldUserCredentials,
            )

            # Process: Return value is of type integer, which means we handle a request abort with HTTP code
            if not success and type(message) == int:
                return handleAbort(message)

        # Call installFonts() method, hand over root object to fill with data
        elif command == "installFonts":

            # Call installFonts()
            success, message = installFonts(
                root,
                fonts,
                subscriptionURL,
                APIKey,
                subscriptionID,
                secretKey,
                accessToken,
                anonymousAppID,
                anonymousTypeWorldUserID,
                verifiedTypeWorldUserCredentials,
                userName,
                userEmail,
            )

            # Process: Return value is of type integer, which means we handle a request abort with HTTP code
            if not success and type(message) == int:
                return handleAbort(message)

        # Call uninstallFonts() method, hand over root object to fill with data
        elif command == "uninstallFonts":

            # Call uninstallFonts()
            success, message = uninstallFonts(
                root,
                fonts,
                subscriptionURL,
                APIKey,
                subscriptionID,
                secretKey,
                accessToken,
                anonymousAppID,
                anonymousTypeWorldUserID,
                verifiedTypeWorldUserCredentials,
            )

            # Process: Return value is of type integer, which means we handle a request abort with HTTP code
            if not success and type(message) == int:
                return handleAbort(message)

    # Export root object into nicely formatted JSON data.
    # This is the moment of truth if you have indeed used the Python object tree as provided by `typeworld.api`.
    # While individual attributes have already been checked earlier, when they were set, here the entire
    # object tree will undergo a validation process to see that all data has been put together in a logical way
    # and that nothing is missing.
    # If you are not using `typeworld.api` or are implementing your server in another programming language,
    # please validate your server using the online validator at https://type.world/developer/validate
    # In the future, the validator will also be made available offline in `typeworld.tools`
    jsonData = root.dumpJSON()

    # Return the response with the correct MIME type `application/json` (or otherwise the app will complain)
    return Response(jsonData, mimetype="application/json")


def endpoint(root):
    """
    Process `endpoint` command
    """

    # Create `endpoint` object, attach to `root`
    endpoint = typeworld.api.EndpointResponse()
    root.endpoint = endpoint

    # Apply data
    endpoint.name.en = "Awesome Fonts"
    endpoint.name.de = "Geile Schriften"
    endpoint.canonicalURL = "https://awesomefonts.appspot.com/typeworldapi"
    endpoint.websiteURL = "https://awesomefonts.appspot.com"
    endpoint.adminEmail = "tech@type.world"
    endpoint.supportedCommands = [
        "endpoint",
        "installableFonts",
        "installFonts",
        "uninstallFonts",
    ]

    # Return successfully, no message
    return True, None


def installableFonts(
    root,
    subscriptionURL,
    APIKey,
    incomingAPIKey,
    subscriptionID,
    secretKey,
    accessToken,
    anonymousAppID,
    anonymousTypeWorldUserID,
    verifiedTypeWorldUserCredentials,
):
    """
    Process `installableFonts` command
    """

    # Create `installableFonts` object, attach to `root`
    installableFonts = typeworld.api.InstallableFontsResponse()
    root.installableFonts = installableFonts

    # `subscriptionID` is set, so we need to find a particular subscription/user account and serve it
    if subscriptionID:

        # Find user
        __user__ = classes.User.get_by_id(subscriptionID)

        # User doesn't exist, return `validTypeWorldUserAccountRequired` immediately
        if not __user__:
            installableFonts.response = "validTypeWorldUserAccountRequired"
            return True, None

        # Secret Key doesn't match with user, return `insufficientPermission` immediately
        if secretKey != __user__.secretKey:
            installableFonts.response = "insufficientPermission"
            return True, None

        ##################################################################
        # Beginning of SECURITY CHECK

        # Either single-use accessToken needs to match, or we need to verify user with type.world server.
        # Corresponds to "Security Level 2" (see: https://type.world/developer#security-levels)

        # Note: `accessToken` is only ever defined for an `installableFonts` command, as it is only ever used once
        # when accessing a subscription for the first time. In the two other methods that have a security check,
        # installFonts() and uninstallFonts(), we’ll solely rely on `verifiedTypeWorldUserCredentials`, as by that time
        # a subscription has already been accessed at least once, and `accessToken` already processed.

        # Set intial state to False
        securityCheckPassed = False

        # Request has a valid single-use access token for this user, so we allow the request
        if accessToken and accessToken == __user__.accessToken:
            securityCheckPassed = True

            # Since the access token is single-use, we need to invalidate it here and assign a new one immediately.
            # Also, in case anything goes wrong in the whole setup process of a subscription in the Type.World app,
            # you need to make sure that in your website’s download section, where the user clicked on the button to get here,
            # that button needs to be reloaded with the new accessToken as part of the subscription URL.
            __user__.accessToken = helpers.Garbage(40)
            __user__.put()

        # Security check is still not passed
        if securityCheckPassed == False:

            # See if the user has already been verified
            if verifiedTypeWorldUserCredentials != None:

                # User has been successfully verified before
                if verifiedTypeWorldUserCredentials == True:
                    securityCheckPassed = True

            # Has not been verified yet, so we need to verify them now
            else:
                # Verify user with central type.world server now, save into global variable `verifiedTypeWorldUserCredentials`
                verifiedTypeWorldUserCredentials = verifyUserCredentials(
                    APIKey,
                    incomingAPIKey,
                    anonymousAppID,
                    anonymousTypeWorldUserID,
                    subscriptionURL,
                )

                # User was successfully validated:
                if verifiedTypeWorldUserCredentials == True:
                    securityCheckPassed = True

        # Still didn’t pass security check, return `insufficientPermission` immediately
        if securityCheckPassed == False:
            installableFonts.response = "insufficientPermission"
            return True, None

        # End of SECURITY CHECK
        ##################################################################

        # Now we’re passed the security check and may continue ...

        # Create object tree for `installableFonts` out of font data in `__user__`
        success, message = createInstallableFontsObjectTree(installableFonts, __user__)

        # Process: Return value is of type integer, which means we handle a request abort with HTTP code
        if not success and type(message) == int:
            return False, message

    # `subscriptionID` is empty. We have two choices here:
    # Either we serve only protected fonts, in which case we require a `subscriptionID`, so we return an abort here
    # or we have a general selection of free fonts to serve for whenever no `subscriptionID` is defined
    else:

        # Choose either scenario:

        # Scenario 1: Only protected fonts, so quit here with HTTP Code 401 Unauthorized
        return False, 401

    # Successful code execution until here, so we set the response value to 'success'
    installableFonts.response = "success"

    # Return successfully, no message
    return True, None


def installFonts(
    root,
    fonts,
    subscriptionURL,
    APIKey,
    incomingAPIKey,
    subscriptionID,
    secretKey,
    accessToken,
    anonymousAppID,
    anonymousTypeWorldUserID,
    verifiedTypeWorldUserCredentials,
    userName,
    userEmail,
):
    """
    Process `installFonts` command
    """

    # Create `installFonts` object, attach to `root`
    installFonts = typeworld.api.InstallFontsResponse()
    root.installFonts = installFonts

    # Find user
    __user__ = classes.User.get_by_id(subscriptionID)

    # User doesn't exist, return `validTypeWorldUserAccountRequired` immediately
    if __user__ == None:
        installFonts.response = "validTypeWorldUserAccountRequired"
        return True, None

    # Secret Key doesn't match with user, return `insufficientPermission` immediately
    if secretKey != __user__.__secretKey__:
        installFonts.response = "insufficientPermission"
        return True, None

    # TODO for later: Add `loginRequired` response here
    # TODO for later: Add `revealedUserIdentityRequired` response here

    ##################################################################
    # Beginning of SECURITY CHECK

    # At this point, in installFonts(), the subscription’s single-use access token has already been verified earlier, so we need not process it here anymore.

    # Set intial state to False
    securityCheckPassed = False

    # See if the user has already been verified
    if verifiedTypeWorldUserCredentials != None:

        # User has been successfully verified before
        if verifiedTypeWorldUserCredentials == True:
            securityCheckPassed = True

    # Has not been verified yet, so we need to verify them now
    else:
        # Verify user with central type.world server now, save into global variable `verifiedTypeWorldUserCredentials`
        verifiedTypeWorldUserCredentials = verifyUserCredentials(
            APIKey,
            incomingAPIKey,
            anonymousAppID,
            anonymousTypeWorldUserID,
            subscriptionURL,
        )

        # User was successfully validated:
        if verifiedTypeWorldUserCredentials == True:
            securityCheckPassed = True

    # Still didn’t pass security check, return `insufficientPermission` immediately
    if securityCheckPassed == False:
        installFonts.response = "insufficientPermission"
        return True, None

    # End of SECURITY CHECK
    ##################################################################

    # Now we’re passed the security check and may continue ...

    # Pull data out of your own data source
    # Note: __subscriptionDataSource__() doesn’t exist in this sample code
    __ownDataSource__ = __user__.__subscriptionDataSource__()

    # Create object tree for `installFonts` out of font data in `__ownDataSource__`
    success, message = createInstallFontsObjectTree(
        installFonts,
        fonts,
        subscriptionID,
        anonymousAppID,
        userName,
        userEmail,
        __ownDataSource__,
    )

    # Process: Return value is of type integer, which means we handle a request abort with HTTP code
    if not success and type(message) == int:
        return False, message

    # Successful code execution until here, so we set the response value to 'success'
    installFonts.response = "success"

    # Return successfully, no message
    return True, None


def uninstallFonts(
    root,
    fonts,
    subscriptionURL,
    APIKey,
    incomingAPIKey,
    subscriptionID,
    secretKey,
    accessToken,
    anonymousAppID,
    anonymousTypeWorldUserID,
    verifiedTypeWorldUserCredentials,
):
    """
    Process `uninstallFonts` command
    """

    # Create `uninstallFonts` object, attach to `root`
    uninstallFonts = typeworld.api.UninstallFontsResponse()
    root.uninstallFonts = uninstallFonts

    # Find user
    __user__ = classes.User.get_by_id(subscriptionID)

    # User doesn't exist, return `validTypeWorldUserAccountRequired` immediately
    if __user__ == None:
        installableFonts.response = "validTypeWorldUserAccountRequired"
        return True, None

    # Secret Key doesn't match with user, return `insufficientPermission` immediately
    if secretKey != __user__.__secretKey__:
        installableFonts.response = "insufficientPermission"
        return True, None

    ##################################################################
    # Beginning of SECURITY CHECK

    # At this point, in installFonts(), the subscription’s single-use access token has already been verified earlier, so we need not process it here anymore.

    # Set intial state to False
    securityCheckPassed = False

    # See if the user has already been verified
    if verifiedTypeWorldUserCredentials != None:

        # User has been successfully verified before
        if verifiedTypeWorldUserCredentials == True:
            securityCheckPassed = True

    # Has not been verified yet, so we need to verify them now
    else:
        # Verify user with central type.world server now, save into global variable `verifiedTypeWorldUserCredentials`
        verifiedTypeWorldUserCredentials = verifyUserCredentials(
            APIKey,
            incomingAPIKey,
            anonymousAppID,
            anonymousTypeWorldUserID,
            subscriptionURL,
        )

        # User was successfully validated:
        if verifiedTypeWorldUserCredentials == True:
            securityCheckPassed = True

    # Still didn’t pass security check, return `insufficientPermission` immediately
    if securityCheckPassed == False:
        installableFonts.response = "insufficientPermission"
        return True, None

    # End of SECURITY CHECK
    ##################################################################

    # Now we’re passed the security check and may continue ...

    # Pull data out of your own data source
    # Note: __subscriptionDataSource__() doesn’t exist in this sample code
    __ownDataSource__ = __user__.__subscriptionDataSource__()

    # Create object tree for `uninstallFonts` out of font data in `__ownDataSource__`
    success, message = createUninstallFontsObjectTree(
        installFonts, fonts, subscriptionID, anonymousAppID, __ownDataSource__
    )

    # Process: Return value is of type integer, which means we handle a request abort with HTTP code
    if not success and type(message) == int:
        return False, message

    # Successful code execution until here, so we set the response value to 'success'
    uninstallFonts.response = "success"

    # Return successfully, no message
    return True, None


def createInstallableFontsObjectTree(installableFonts, __ownDataSource__):
    """
    Apply incoming data of `__ownDataSource__` to `installableFonts`.
    This sample code here is very abstract and incomplete.
    Each font publisher has their own database structure and therefore
    a complete example cannot be created.
    You may not even want to use __ownDataSource__ or this method at all.
    Basically, you need to fill in all the minimal required data (and more) into
    the object structure indicated below following your own logic.
    The object structure is defined in detail here:
    https://github.com/typeworld/typeworld/tree/master/Lib/typeworld/api
    """

    # Designers
    for __designerDataSource__ in __ownDataSource__.__designers__():

        # Create Designer object, attach to `installableFonts.designers`, apply data
        designer = typeworld.api.Designer()
        installableFonts.designers.append(designer)

        # Apply data
        designer.keyword = __designerDataSource__.__keyword__
        designer.name.en = __designerDataSource__.__name__
        # etc ...

    # Foundry
    for __foundryDataSource__ in __ownDataSource__.__foundries__():

        # Create Foundry object, attach to `installableFonts.foundries`, apply data
        foundry = typeworld.api.Foundry()
        installableFonts.foundry.append(foundry)

        # Apply data
        designer.keyword = __foundryDataSource__.__keyword__
        designer.name.en = __foundryDataSource__.__name__
        # etc ...

        # License Definitions
        for __licenseDataSource__ in __foundryDataSource__.licenses():

            # Create LicenseDefinition object, attach to `foundry`
            licenseDefition = typeworld.api.LicenseDefinition()
            foundry.licenses.append(licenseDefition)

            # Apply data
            licenseDefition.keyword = __licenseDataSource__.__keyword__
            # etc ...

        # Families
        for __familyDataSource__ in __foundryDataSource__.licenses():

            # Create Family object, attach to `foundry`
            family = typeworld.api.Family()
            foundry.families.append(family)

            # Apply data
            family.uniqueID = __familyDataSource__.__uniqueID__
            # etc ...

            # Family-level Font Versions
            # Here, we’re defining family-wide font versions.
            # You could also set the on font-level instead, or a combination of both
            for __versionDataSource__ in __familyDataSource__.__versions__():

                # Create Version object, attach to `family.versions`
                version = typeworld.api.Version()
                family.versions.append(version)

                # Apply data
                version.number = __versionDataSource__.__versionNumber__
                # etc ...

            # Fonts
            for __fontDataSource__ in __familyDataSource__.__fonts__():

                # Create Font object, attach to `family.fonts`
                font = typeworld.api.Font()
                family.fonts.append(font)

                # Apply data
                font.uniqueID = __fontDataSource__.__uniqueID__
                # etc ...

    # Return successfully, no message
    return True, None


def createInstallFontsObjectTree(
    installFonts,
    fonts,
    subscriptionID,
    anonymousAppID,
    userName,
    userEmail,
    __ownDataSource__,
):
    """
    Apply incoming data of `__ownDataSource__` to `installFonts`
    """

    # Parse fonts into list
    # They come as comma-separated pairs of fontID/fontVersion, so
    # "font1ID/font1Version,font2ID/font2Version" becomes [['font1ID', 'font1Version'], ['font2ID', 'font2Version']]
    fontsList = [x.split("/") for x in fonts.split(",")]

    # Loop over incoming fonts list
    for fontID, fontVersion in fontsList:

        # Load own data source
        __fontDataSource__ = __ownDataSource__.__fontDataSource__(fontID)

        # Create InstallFontAsset object, attach to `installFonts.assets`
        asset = typeworld.api.InstallFontAsset()
        installFonts.assets.append(asset)

        # Couldn't find data source by ID, return `unknownFont`
        if __fontDataSource__ == None:
            asset.response = "unknownFont"

        # In case your server observes license compliance, it needs to track
        # font installations. These are identified by the tripled
        # `subscriptionID, anonymousAppID, fontID`.

        # See whether user’s seat allowance has been reached for this font
        seats = __ownDataSource__.__recordedFontInstallations__(subscriptionID, anonymousAppID, fontID)

        # Installed seats have reached seat allowance, return `seatAllowanceReached`
        if seats >= __fontDataSource__.__licenseDataSource__.__allowedSeats__:
            asset.response = "seatAllowanceReached"

        # All go, let’s serve the font

        # Apply data
        asset.response = "success"
        asset.uniqueID = __fontDataSource__.__uniqueID__
        asset.encoding = "base64"
        asset.mimeType = "font/otf"
        asset.data = __fontDataSource__.__binaryFontData__

        # Font is not a free font
        if __fontDataSource__.__protected__:

            # Finally, let’s record this installation in the database, to count seats for each font per license
            # This call is related to `__fontDataSource__.__recordedFontInstallations__(fontID, subscriptionID, anonymousAppID)` from above where
            # number of previously installed seats is checked, which is a result of this following recording.
            # The parameters `fontVersion`, `userName`, and `userEmail` are not strictly necessary for this recording, but you may
            # want to save them into your database for analysis.

            # Font is a trial font, so we may have to update previously existing font installation records
            if __fontDataSource__.__isTrialFont__:

                # Font has not been previously installed, so no record exists:
                if seats == None:
                    __ownDataSource__.__recordFontInstallation__(
                        subscriptionID,
                        anonymousAppID,
                        fontID,
                        fontVersion,  # Not to be used for installation identification
                        userName,  # Not to be used for installation identification
                        userEmail,  # Not to be used for installation identification
                    )

                # Font has been previously installed (so a record exists), but is marked as 'uninstalled', so we update that
                else:
                    __ownDataSource__.__updateFontInstallation__(
                        subscriptionID,
                        anonymousAppID,
                        fontID,
                        trialInstalledStatus=True,
                    )

            # Font is not a trial font, so just record installation normally
            else:
                __ownDataSource__.__recordFontInstallation__(
                    subscriptionID,
                    anonymousAppID,
                    fontID,
                    fontVersion,  # Not to be used for installation identification
                    userName,  # Not to be used for installation identification
                    userEmail,  # Not to be used for installation identification
                )

    # Return successfully, no message
    return True, None


def createUninstallFontsObjectTree(
    uninstallFonts,
    fonts,
    subscriptionID,
    anonymousAppID,
    userName,
    userEmail,
    __ownDataSource__,
):
    """
    Apply incoming data of `__ownDataSource__` to `uninstallFonts`
    """

    # Parse fonts into list
    # They come as comma-separated pairs of fontID/fontVersion, so
    # "font1ID,font2ID" becomes ['font1ID', 'font2ID']
    fontsList = fonts.split(",")

    # Loop over incoming fonts list
    for fontID in fontsList:

        # Load own data source
        __fontDataSource__ = __ownDataSource__.__fontDataSource__(fontID)

        # Create UninstallFontAsset object, attach to `uninstallFonts.assets`
        asset = typeworld.api.UninstallFontAsset()
        uninstallFonts.assets.append(asset)

        # Couldn't find data source by ID, set response, return immediately
        if __fontDataSource__ == None:
            asset.response = "unknownFont"

        # See how many seats the user has installed
        seats = __ownDataSource__.__recordedFontInstallations__(fontID, subscriptionID, anonymousAppID)

        # No seats have been recorded for this `anonymousAppID`, so we return the `unknownInstallation` command
        # Note: This is critical for the remote de-authorization for entire app instances to work properly,
        # and will be checked by the API Endpoint Validator (see: https://type.world/developer/validate)
        # See: https://type.world/developer#remote-de-authorization-of-app-instances-by-the-user
        if seats == None:
            asset.response = "unknownInstallation"

        # All go, let’s delete the font
        asset.response = "success"

        # Font is not a free font
        if __fontDataSource__.__protected__:

            # Finally, let’s delete this installation record from the database

            # Font is a trial font, so instead of deleting this font installation from our records, we’ll just update it, marked as not installed,
            # because if you delete it instead, you effectively reset the the user’s trial period of that font.
            if __fontDataSource__.__isTrialFont__:
                __ownDataSource__.__updateFontInstallation__(
                    fontID, subscriptionID, anonymousAppID, trialInstalledStatus=False
                )

            # Font is not a trial font, so just delete the installation record normally
            else:
                __ownDataSource__.__deleteFontInstallationRecord__(fontID, subscriptionID, anonymousAppID)

    # Return successfully, no message
    return True, None


def verifyUserCredentials(
    APIKey,
    incomingAPIKey,
    anonymousAppID,
    anonymousTypeWorldUserID,
    subscriptionURL=None,
):
    """
    Verify a valid Type.World user account with the central server
    """

    # Shortcut: if APIKey is identical to incomingAPIKey, that means that the
    # request comes from the central server and since it sent your own API key for
    # verification, we can instantly return the verification to be successful
    if APIKey == incomingAPIKey:
        return True

    # Otherwise, send the normal verification request to the central server

    # Default parameters
    parameters = {
        "APIKey": APIKey,
        "anonymousTypeWorldUserID": anonymousTypeWorldUserID,
        "anonymousAppID": anonymousAppID,
    }

    # Optional `subscriptionURL` is defined, sadd it
    if subscriptionURL:
        parameters["subscriptionURL"] = subscriptionURL

    # We’re using typeworld’s built-in request() method here which loops through a request up to 10 times
    # in case an instance of the central server disappears during the request.
    # See the WARNING at https://type.world/developer#typeworld-api
    # If you’re implementing this in a language other than Python, make sure to read and follow that warning.
    success, response, responseObject = typeworld.client.request(
        "https://api.type.world/v1/verifyCredentials", parameters
    )

    # Request was successfully returned
    # Note: This means that the HTTP request was successful, not that the user has been verified. This will be confirmed a few lines down.
    if success:

        # Read response data from a JSON string
        responseData = json.loads(response.decode())

        # Verfification process was successful
        if responseData["response"] == "success":

            # Return True immediately
            return True

    # No previous success, so let’s return False
    return False


def handleAbort(code):
    """
    You can use this method to handle all malformed requests.
    Depending on what kind of security shields you have in place, you could keep informing them
    about malformed requests so that eventually a DOS attack shield could kick in, for instance.
    """

    # Handle malformed request here
    # ...

    # Return flask’s abort() method with HTTP status code
    return abort(code)
