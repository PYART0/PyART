import fnmatch
import functools


CORS_PARAMETERS = ('cors_headers', 'cors_enabled', 'cors_origins',
                   'cors_credentials', 'cors_max_age',
                   'cors_expose_all_headers')


def get_cors_preflight_view(service):

    def _preflight_view(request):
        response = request.response
        origin = request.headers.get('Origin')
        supported_headers = service.cors_supported_headers_for()

        if not origin:
            request.errors.add('header', 'Origin',
                               'this header is mandatory')

        requested_method = request.headers.get('Access-Control-Request-Method')
        if not requested_method:
            request.errors.add('header', 'Access-Control-Request-Method',
                               'this header is mandatory')

        if not (requested_method and origin):
            return

        requested_headers = (
            request.headers.get('Access-Control-Request-Headers', ()))

        if requested_headers:
            requested_headers = map(str.strip, requested_headers.split(','))

        if requested_method not in service.cors_supported_methods:
            request.errors.add('header', 'Access-Control-Request-Method',
                               'Method not allowed')

        if not service.cors_expose_all_headers:
            for h in requested_headers:
                if not h.lower() in [s.lower() for s in supported_headers]:
                    request.errors.add(
                        'header',
                        'Access-Control-Request-Headers',
                        'Header "%s" not allowed' % h)

        supported_headers = set(supported_headers) | set(requested_headers)

        response.headers['Access-Control-Allow-Headers'] = (
            ','.join(supported_headers))

        response.headers['Access-Control-Allow-Methods'] = (
            ','.join(service.cors_supported_methods))

        max_age = service.cors_max_age_for(requested_method)
        if max_age is not None:
            response.headers['Access-Control-Max-Age'] = str(max_age)

        return None
    return _preflight_view


def _get_method(request):
    if request.method == 'OPTIONS':
        method = request.headers.get('Access-Control-Request-Method',
                                     request.method)
    else:
        method = request.method
    return method


def ensure_origin(service, request, response=None, **kwargs):
    response = response or request.response

    if not request.info.get('cors_checked', False):
        method = _get_method(request)

        origin = request.headers.get('Origin')
        if origin:
            if not any([fnmatch.fnmatchcase(origin, o)
                        for o in service.cors_origins_for(method)]):
                request.errors.add('header', 'Origin',
                                   '%s not allowed' % origin)
            elif service.cors_support_credentials_for(method):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                if any([o == "*" for o in service.cors_origins_for(method)]):
                    response.headers['Access-Control-Allow-Origin'] = '*'
                else:
                    response.headers['Access-Control-Allow-Origin'] = origin
        request.info['cors_checked'] = True
    return response


def get_cors_validator(service):
    reveal_type(functools)