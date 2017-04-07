from tastypie.models import ApiKey
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import AuthenticationFailed
from perma.models import LinkUser

from api2.authentication import TokenAuthentication
from .utils import ApiResourceTransactionTestCase


class TokenAuthenticationTestCase(ApiResourceTransactionTestCase):
    '''
        Pop up test users possessing API keys. Test whether the
        authentication function works, independent of any real
        auth-protected routes in the application, using a request
        factory.

        Note that the request factory returns HttpRequest objects,
        and not REST framework's Request objects. We manually create
        the latter from the former, which, for non-GET http requests,
        requires a parser instance as an argument, which is used to
        parse the data included in the request. Any necessary parsers
        can be imported directly from rest_framework.parsers: match
        the content-type of your data with the parser name.

        N.B. api authentication configured in app settings, and can include
        multiple authenticators. E.g.
        ```
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'api2.authentication.TokenAuthentication',  # authenticate with ApiKey token
                'rest_framework.authentication.SessionAuthentication',  # authenticate with Django login
            ),
            ...
        }
        ```
    '''

    def new_api_user(*args, **kwargs):
        u = LinkUser(**kwargs)
        u.save()
        ApiKey.objects.create(user=u)
        return u

    def setUp(self):
        super(TokenAuthenticationTestCase, self).setUp()
        self.factory = APIRequestFactory()
        self.authenticator = TokenAuthentication()
        self.active_user = self.new_api_user(is_active=True, is_confirmed=True, email="new_active_user@example.com")
        self.inactive_user = self.new_api_user(is_active=False, is_confirmed=False, email="new_inactive_user@example.com")

    def auth_via_query_string(self, user, key):
        # independent of http method; GET used arbitrarily
        request = Request(self.factory.get('some_url?api_key=' + key))
        try:
            self.authenticator.authenticate(request)
            return True
        except AuthenticationFailed:
            return False

    def auth_via_post_object(self, user, key):
        # for a posted value to appear in request.POST rather than request.data,
        # the format must be form rather than json
        request = Request(self.factory.post('some_url', {"api_key": key}, format='multipart'), parsers=(MultiPartParser(),));
        try:
            self.authenticator.authenticate(request)
            return True
        except AuthenticationFailed:
            return False

    def test_successful_with_active_user_via_query_string(self):
        self.assertTrue(self.auth_via_query_string(self.active_user, self.active_user.api_key.key))

    def test_successful_with_active_user_via_post(self):
        self.assertTrue(self.auth_via_post_object(self.active_user, self.active_user.api_key.key))

    def test_fails_with_wrong_key_via_query_string(self):
        self.assertFalse(self.auth_via_query_string(self.active_user, 'notthekey'))

    def test_fails_with_wrong_key_via_post(self):
        self.assertFalse(self.auth_via_post_object(self.active_user, 'notthekey'))

    def test_fails_with_inactive_user_via_query_string(self):
        self.assertFalse(self.auth_via_query_string(self.inactive_user, self.inactive_user.api_key.key))

    def test_fails_with_inactive_user_via_post(self):
        self.assertFalse(self.auth_via_post_object(self.inactive_user, self.inactive_user.api_key.key))
