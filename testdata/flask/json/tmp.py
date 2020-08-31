from base64 import b64decode
from base64 import b64encode
from datetime import datetime
from uuid import UUID

from markupsafe import Markup
from werkzeug.http import http_date
from werkzeug.http import parse_date

from ..json import dumps
from ..json import loads


class JSONTag:

    __slots__ = ("serializer",)

    key = None

    def __init__(self, serializer):
        self.serializer = serializer

    def check(self, value):
        raise NotImplementedError

    def to_json(self, value):
        raise NotImplementedError

    def to_python(self, value):
        raise NotImplementedError

    def tag(self, value):
        return {self.key: self.to_json(value)}


class TagDict(JSONTag):

    __slots__ = ()
    key = " di"

    def check(self, value):
        return (
            isinstance(value, dict)
            and len(value) == 1
            and next(iter(value)) in self.serializer.tags
        )

    def to_json(self, value):
        key = next(iter(value))
        return {f"{key}__": self.serializer.tag(value[key])}

    def to_python(self, value):
        key = next(iter(value))
        return {key[:-2]: value[key]}


class PassDict(JSONTag):
    __slots__ = ()

    def check(self, value):
        return isinstance(value, dict)

    def to_json(self, value):
        return {k: self.serializer.tag(v) for k, v in value.items()}

    tag = to_json


class TagTuple(JSONTag):
    __slots__ = ()
    key = " t"

    def check(self, value):
        return isinstance(value, tuple)

    def to_json(self, value):
        return [self.serializer.tag(item) for item in value]

    def to_python(self, value):
        return tuple(value)


class PassList(JSONTag):
    __slots__ = ()

    def check(self, value):
        return isinstance(value, list)

    def to_json(self, value):
        return [self.serializer.tag(item) for item in value]

    tag = to_json


class TagBytes(JSONTag):
    __slots__ = ()
    key = " b"

    def check(self, value):
        return isinstance(value, bytes)

    def to_json(self, value):
        return b64encode(value).decode("ascii")

    def to_python(self, value):
        return b64decode(value)


class TagMarkup(JSONTag):

    __slots__ = ()
    key = " m"

    def check(self, value):
        return callable(getattr(value, "__html__", None))

    def to_json(self, value):
        return str(value.__html__())

    def to_python(self, value):
        return Markup(value)


class TagUUID(JSONTag):
    __slots__ = ()
    key = " u"

    def check(self, value):
        return isinstance(value, UUID)

    def to_json(self, value):
        return value.hex

    def to_python(self, value):
        return UUID(value)


class TagDateTime(JSONTag):
    __slots__ = ()
    key = " d"

    def check(self, value):
        return isinstance(value, datetime)

    def to_json(self, value):
        return http_date(value)

    def to_python(self, value):
        return parse_date(value)


class TaggedJSONSerializer:

    __slots__ = ("tags", "order")

    default_tags = [
        TagDict,
        PassDict,
        TagTuple,
        PassList,
        TagBytes,
        TagMarkup,
        TagUUID,
        TagDateTime,
    ]

    def __init__(self):
        self.tags = {}
        self.order = []

        for cls in self.default_tags:

    def register(self, tag_class, force=False, index=None):
        tag = tag_class(self)
        key = tag.key

        if key is not None:
            if not force and key in self.tags:
                raise KeyError(f"Tag '{key}' is already registered.")

            self.tags[key] = tag

        if index is None:
        else:

    def tag(self, value):
        for tag in self.order:
            if tag.check(value):

        return value

    def untag(self, value):
        if len(value) != 1:
            return value

        key = next(iter(value))

        if key not in self.tags:
            return value

        return self.tags[key].to_python(value[key])

    def dumps(self, value):
        reveal_type(self)