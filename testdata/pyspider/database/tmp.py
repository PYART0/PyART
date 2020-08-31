import os, requests, json
from six.moves.urllib.parse import urlparse, parse_qs


def connect_database(url):
    db = _connect_database(url)
    db.copy = lambda: _connect_database(url)
    return db


def _connect_database(url):  # NOQA
    parsed = urlparse(url)

    scheme = parsed.scheme.split('+')
    if len(scheme) == 1:
        raise Exception('wrong scheme format: %s' % parsed.scheme)
    else:
        engine, dbtype = scheme[0], scheme[-1]
        other_scheme = "+".join(scheme[1:-1])

    if dbtype not in ('taskdb', 'projectdb', 'resultdb'):
        raise LookupError('unknown database type: %s, '
                          'type should be one of ["taskdb", "projectdb", "resultdb"]', dbtype)

    if engine == 'mysql':
        return _connect_mysql(parsed,dbtype)

    elif engine == 'sqlite':
        return _connect_sqlite(parsed,dbtype)
    elif engine == 'mongodb':
        return _connect_mongodb(parsed,dbtype,url)

    elif engine == 'sqlalchemy':
        return _connect_sqlalchemy(parsed, dbtype, url, other_scheme)


    elif engine == 'redis':
        if dbtype == 'taskdb':
            from .redis.taskdb import TaskDB
            return TaskDB(parsed.hostname, parsed.port,
                          int(parsed.path.strip('/') or 0))
        else:
            raise LookupError('not supported dbtype: %s', dbtype)
    elif engine == 'local':
        scripts = url.split('//', 1)[1].split(',')
        if dbtype == 'projectdb':
            from .local.projectdb import ProjectDB
            return ProjectDB(scripts)
        else:
            raise LookupError('not supported dbtype: %s', dbtype)
    elif engine == 'elasticsearch' or engine == 'es':
        return _connect_elasticsearch(parsed, dbtype)

    elif engine == 'couchdb':
        return _connect_couchdb(parsed, dbtype, url)

    else:
        raise Exception('unknown engine: %s' % engine)


def _connect_mysql(parsed,dbtype):
    parames = {}
    if parsed.username:
        parames['user'] = parsed.username
    if parsed.password:
        parames['passwd'] = parsed.password
    if parsed.hostname:
        parames['host'] = parsed.hostname
    if parsed.port:
        parames['port'] = parsed.port
    if parsed.path.strip('/'):
        parames['database'] = parsed.path.strip('/')

    if dbtype == 'taskdb':
        from .mysql.taskdb import TaskDB
        return TaskDB(**parames)
    elif dbtype == 'projectdb':
        from .mysql.projectdb import ProjectDB
        return ProjectDB(**parames)
    elif dbtype == 'resultdb':
        from .mysql.resultdb import ResultDB
        return ResultDB(**parames)
    else:
        raise LookupError


def _connect_sqlite(parsed,dbtype):
    if parsed.path.startswith('//'):
        path = '/' + parsed.path.strip('/')
    elif parsed.path.startswith('/'):
        path = './' + parsed.path.strip('/')
    elif not parsed.path:
        path = ':memory:'
    else:
        raise Exception('error path: %s' % parsed.path)

    if dbtype == 'taskdb':
        from .sqlite.taskdb import TaskDB
        return TaskDB(path)
    elif dbtype == 'projectdb':
        from .sqlite.projectdb import ProjectDB
        return ProjectDB(path)
    elif dbtype == 'resultdb':
        from .sqlite.resultdb import ResultDB
        return ResultDB(path)
    else:
        raise LookupError


def _connect_mongodb(parsed,dbtype,url):
    url = url.replace(parsed.scheme, 'mongodb')
    parames = {}
    if parsed.path.strip('/'):
        parames['database'] = parsed.path.strip('/')

    if dbtype == 'taskdb':
        from .mongodb.taskdb import TaskDB
        return TaskDB(url, **parames)
    elif dbtype == 'projectdb':
        from .mongodb.projectdb import ProjectDB
        return ProjectDB(url, **parames)
    elif dbtype == 'resultdb':
        from .mongodb.resultdb import ResultDB
        return ResultDB(url, **parames)
    else:
        raise LookupError


def _connect_sqlalchemy(parsed, dbtype,url, other_scheme):
    if not other_scheme:
        raise Exception('wrong scheme format: %s' % parsed.scheme)
    url = url.replace(parsed.scheme, other_scheme)
    if dbtype == 'taskdb':
        from .sqlalchemy.taskdb import TaskDB
        return TaskDB(url)
    elif dbtype == 'projectdb':
        from .sqlalchemy.projectdb import ProjectDB
        return ProjectDB(url)
    elif dbtype == 'resultdb':
        from .sqlalchemy.resultdb import ResultDB
        return ResultDB(url)
    else:
        raise LookupError


def _connect_elasticsearch(parsed, dbtype):
    if parsed.path.startswith('/?'):
        index = parse_qs(parsed.path[2:])
    else:
        index = parse_qs(parsed.query)
    if 'index' in index and index['index']:
        index = index['index'][0]
    else:
        index = 'pyspider'

    if dbtype == 'projectdb':
        from .elasticsearch.projectdb import ProjectDB
        return ProjectDB([parsed.netloc], index=index)
    elif dbtype == 'resultdb':
        from .elasticsearch.resultdb import ResultDB
        return ResultDB([parsed.netloc], index=index)
    elif dbtype == 'taskdb':
        from .elasticsearch.taskdb import TaskDB
        return TaskDB([parsed.netloc], index=index)


def _connect_couchdb(parsed, dbtype, url):
    reveal_type(os.environ)