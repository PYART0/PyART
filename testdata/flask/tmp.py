import hashlib
import warnings
from collections.abc import MutableMapping
from datetime import datetime

from itsdangerous import BadSignature
from itsdangerous import URLSafeTimedSerializer
from werkzeug.datastructures import CallbackDict

from .helpers import is_ip
from .helpers import total_seconds
from .json.tag import TaggedJSONSerializer


class SessionMixin(MutableMapping):

    @property
    def permanent(self):
        return self.get("_permanent", False)

    @permanent.setter
    def permanent(self, value):
        self["_permanent"] = bool(value)

    new = False

    modified = True

    accessed = True


class SecureCookieSession(CallbackDict, SessionMixin):

    modified = False

    accessed = False

    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
            self.accessed = True

        super().__init__(initial, on_update)

    def __getitem__(self, key):
        self.accessed = True
        return super().__getitem__(key)

    def get(self, key, default=None):
        self.accessed = True
        return super().get(key, default)

    def setdefault(self, key, default=None):
        self.accessed = True
        return super().setdefault(key, default)


class NullSession(SecureCookieSession):

    def _fail(self, *args, **kwargs):
        raise RuntimeError(
            "The session is unavailable because no secret "
            "key was set.  Set the secret_key on the "
            "application to something unique and secret."
        )

    __setitem__ = __delitem__ = clear = pop = popitem = update = setdefault = _fail
    del _fail


class SessionInterface:

    null_session_class = NullSession

    pickle_based = False

    def make_null_session(self, app):
        return self.null_session_class()

    def is_null_session(self, obj):
        return isinstance(obj, self.null_session_class)

    def get_cookie_name(self, app):
        return app.session_cookie_name

    def get_cookie_domain(self, app):

        rv = app.config["SESSION_COOKIE_DOMAIN"]

        if rv is not None:
            return rv if rv else None

        rv = app.config["SERVER_NAME"]

        if not rv:
            app.config["SESSION_COOKIE_DOMAIN"] = False
            return None

        rv = rv.rsplit(":", 1)[0].lstrip(".")

        if "." not in rv:
            warnings.warn(
                f"{rv!r} is not a valid cookie domain, it must contain"
                " a '.'. Add an entry to your hosts file, for example"
                f" '{rv}.localdomain', and use that instead."
            )
            app.config["SESSION_COOKIE_DOMAIN"] = False
            return None

        ip = is_ip(rv)

        if ip:
            warnings.warn(
                "The session cookie domain is an IP address. This may not work"
                " as intended in some browsers. Add an entry to your hosts"
                ' file, for example "localhost.localdomain", and use that'
                " instead."
            )

        if self.get_cookie_path(app) == "/" and not ip:
            rv = f".{rv}"

        app.config["SESSION_COOKIE_DOMAIN"] = rv
        return rv

    def get_cookie_path(self, app):
        return app.config["SESSION_COOKIE_PATH"] or app.config["APPLICATION_ROOT"]

    def get_cookie_httponly(self, app):
        return app.config["SESSION_COOKIE_HTTPONLY"]

    def get_cookie_secure(self, app):
        return app.config["SESSION_COOKIE_SECURE"]

    def get_cookie_samesite(self, app):
        return app.config["SESSION_COOKIE_SAMESITE"]

    def get_expiration_time(self, app, session):
        if session.permanent:
            return datetime.utcnow() + app.permanent_session_lifetime

    def should_set_cookie(self, app, session):

        return session.modified or (
            session.permanent and app.config["SESSION_REFRESH_EACH_REQUEST"]
        )

    def open_session(self, app, request):
        raise NotImplementedError()

    def save_session(self, app, session, response):
        raise NotImplementedError()


session_json_serializer = TaggedJSONSerializer()


class SecureCookieSessionInterface(SessionInterface):

    salt = "cookie-session"
    digest_method = staticmethod(hashlib.sha1)
    key_derivation = "hmac"
    serializer = session_json_serializer
    session_class = SecureCookieSession

    def get_signing_serializer(self, app):
        if not app.secret_key:
            return None
        signer_kwargs = dict(
            key_derivation=self.key_derivation, digest_method=self.digest_method
        )
        return URLSafeTimedSerializer(
            app.secret_key,
            salt=self.salt,
            serializer=self.serializer,
            signer_kwargs=signer_kwargs,
        )

    def open_session(self, app, request):
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(self.get_cookie_name(app))
        if not val:
            return self.session_class()
        max_age = total_seconds(app.permanent_session_lifetime)
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        name = self.get_cookie_name(app)
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        if not session:
            if session.modified:
                response.delete_cookie(name, domain=domain, path=path)

            return

        if session.accessed:
            response.vary.add("Cookie")

        if not self.should_set_cookie(app, session):
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)
        reveal_type(self)