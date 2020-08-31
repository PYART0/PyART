from __future__ import with_statement

import sys
import unittest
from unittest import TestCase

import simplejson
from simplejson import encoder, decoder, scanner
from simplejson.compat import PY3, long_type, b


def has_speedups():
    return encoder.c_make_encoder is not None


def skip_if_speedups_missing(func):
    def wrapper(*args, **kwargs):
        if not has_speedups():
            if hasattr(unittest, 'SkipTest'):
                raise unittest.SkipTest("C Extension not available")
            else:
                sys.stdout.write("C Extension not available")
                return
        return func(*args, **kwargs)

    return wrapper


class BadBool:
    def __bool__(self):
        1/0
    __nonzero__ = __bool__


class TestDecode(TestCase):
    @skip_if_speedups_missing
    def test_make_scanner(self):
        self.assertRaises(AttributeError, scanner.c_make_scanner, 1)

    @skip_if_speedups_missing
    def test_bad_bool_args(self):
        def test(value):
            decoder.JSONDecoder(strict=BadBool()).decode(value)
        self.assertRaises(ZeroDivisionError, test, '""')
        self.assertRaises(ZeroDivisionError, test, '{}')
        if not PY3:
            self.assertRaises(ZeroDivisionError, test, u'""')
            self.assertRaises(ZeroDivisionError, test, u'{}')

class TestEncode(TestCase):
    @skip_if_speedups_missing
    def test_make_encoder(self):
        self.assertRaises(
            TypeError,
            encoder.c_make_encoder,
            None,
            ("\xCD\x7D\x3D\x4E\x12\x4C\xF9\x79\xD7"
             "\x52\xBA\x82\xF2\x27\x4A\x7D\xA0\xCA\x75"),
            None
        )

    @skip_if_speedups_missing
    def test_bad_str_encoder(self):
        import decimal
        def bad_encoder1(*args):
            return None
        enc = encoder.c_make_encoder(
                None, lambda obj: str(obj),
                bad_encoder1, None, ': ', ', ',
                False, False, False, {}, False, False, False,
                None, None, 'utf-8', False, False, decimal.Decimal, False)
        self.assertRaises(TypeError, enc, 'spam', 4)
        self.assertRaises(TypeError, enc, {'spam': 42}, 4)

        def bad_encoder2(*args):
            1/0
        enc = encoder.c_make_encoder(
                None, lambda obj: str(obj),
                bad_encoder2, None, ': ', ', ',
                False, False, False, {}, False, False, False,
                None, None, 'utf-8', False, False, decimal.Decimal, False)
        self.assertRaises(ZeroDivisionError, enc, 'spam', 4)

    @skip_if_speedups_missing
    def test_bad_bool_args(self):
        def test(name):
            reveal_type(encoder)