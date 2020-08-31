import inspect


def _generate_marshmallow_validator(location):

    def _validator(request, schema=None, deserializer=None, **kwargs):
        import marshmallow
        import marshmallow.schema
        try:
            from marshmallow.utils import EXCLUDE
        except ImportError:
            EXCLUDE = 'exclude'

        if schema is None:
            return

        schema_kwargs = kwargs.get('schema_kwargs', {})
        schema = _instantiate_schema(schema, **schema_kwargs)

        class ValidatedField(marshmallow.fields.Field):
            def _deserialize(self, value, attr, data, **kwargs):
                schema.context.setdefault('request', request)
                deserialized = schema.load(value)
                if isinstance(deserialized, tuple):
                    deserialized, errors = deserialized[0], deserialized[1]
                    if errors:
                        raise marshmallow.ValidationError(
                            errors)  # pragma: no cover
                return deserialized

        class Meta(object):
            strict = True
            ordered = True
            unknown = EXCLUDE

        class RequestSchemaMeta(marshmallow.schema.SchemaMeta):

            def __new__(cls, name, bases, class_attrs):

                class_attrs[location] = ValidatedField(
                    required=True, load_from=location)
                class_attrs['Meta'] = Meta
                return type(name, bases, class_attrs)

        class RequestSchema(marshmallow.Schema, metaclass=RequestSchemaMeta):  # noqa
            pass

        validator(request, RequestSchema, deserializer, **kwargs)
        request.validated = request.validated.get(location, {})

    return _validator


body_validator = _generate_marshmallow_validator('body')
headers_validator = _generate_marshmallow_validator('header')
path_validator = _generate_marshmallow_validator('path')
querystring_validator = _generate_marshmallow_validator('querystring')


def _message_normalizer(exc, no_field_name="_schema"):
    if isinstance(exc.messages, dict):
        if '_schema' in exc.messages:
            new_dict = {}
            if not hasattr(exc.messages['_schema'], 'keys'):
                for item in exc.messages['_schema']:
                    new_dict.update(item)
                return {'_schema': new_dict}
        return exc.messages
    if len(exc.field_names) == 0:
        return {no_field_name: exc.messages}
    return dict((name, exc.messages) for name in exc.field_names)


def validator(request, schema=None, deserializer=None, **kwargs):
    import marshmallow
    from cornice.validators import extract_cstruct

    if deserializer is None:
        deserializer = extract_cstruct

    if schema is None:
        return

    schema = _instantiate_schema(schema)
    schema.context.setdefault('request', request)

    cstruct = deserializer(request)
    try:
        deserialized = schema.load(cstruct)
        if isinstance(deserialized, tuple):
            deserialized, errors = deserialized[0], deserialized[1]
            if errors:
                raise marshmallow.ValidationError(errors)
    except marshmallow.ValidationError as err:
        normalized_errors = _message_normalizer(err)
        for location, details in normalized_errors.items():
            location = location if location != '_schema' else ''
            if hasattr(details, 'items'):
                for subfield, msg in details.items():
                    request.errors.add(location, subfield, msg)
            else:
                request.errors.add(location, location, details)
    else:
        request.validated.update(deserialized)


def _instantiate_schema(schema, **kwargs):
    reveal_type(inspect)