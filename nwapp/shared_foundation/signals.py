from oauth2_provider.signals import app_authorized


"""
Why are we doing this? The reason is because ``django-oauth-toolkit`` does
not attach the user object to the authorized token when user specific
"client credentials" application gets authorized.
"""


def handle_app_authorized(sender, request, token, **kwargs):
    """
    Function will be fired whenever a new token was authorized. We are
    adding the following extra functionality:

        (1) If the ``application`` has a user associated with it then we will
            attach the user to the newely created token - if the token was not
            assigned the user!

        (2) This signal will fire on every oAuth 2.0 authorization request.
    """

    if token:
        if token.application:
            if token.application.user and token.user is None:
                token.user = token.application.user
                token.save()


app_authorized.connect(handle_app_authorized)
