# -*- coding: utf-8 -*-
"""Test XonshLexer for pygments"""

import pytest
import os
from pygments.token import (Keyword, Name, Comment, String, Error, Number,
                            Operator, Generic, Whitespace, Token, Punctuation,
                            Text)
from tools import (skip_if_on_unix, skip_if_on_windows)

from xonsh.built_ins import load_builtins, unload_builtins
from xonsh.pyghooks import XonshLexer


@pytest.yield_fixture(autouse=True)
def load_command_cache():
    load_builtins()
    yield
    unload_builtins()


def check_token(code, tokens):
    """Make sure that all tokens appears in code in order"""
    load_builtins()
    lx = XonshLexer()
    tks = list(lx.get_tokens(code))

    for tk in tokens:
        while tks:
            if tk == tks[0]:
                break
            tks = tks[1:]
        else:
            msg = "Token {!r} missing: {!r}".format(tk,
                                                    list(lx.get_tokens(code)))
            pytest.fail(msg)
            break


@skip_if_on_windows
def test_ls():
    check_token('ls -al', [(Keyword, 'ls')])


@skip_if_on_windows
def test_bin_ls():
    check_token('/bin/ls -al', [(Keyword, '/bin/ls')])


def test_py_print():
    check_token('print("hello")', [(Keyword, 'print'),
                                   (String.Double, 'hello')])


def test_invalid_cmd():
    check_token('non-existance-cmd -al', [(Name, 'non')])  # parse as python
    check_token('![non-existance-cmd -al]',
                [(Error, 'non-existance-cmd')])  # parse as error
    check_token('for i in range(10):', [(Keyword, 'for')])  # as py keyword


def test_multi_cmd():
    check_token('cd && cd', [(Keyword, 'cd'),
                             (Operator, '&&'),
                             (Keyword, 'cd')])
    check_token('cd || non-existance-cmd', [(Keyword, 'cd'),
                                            (Operator, '||'),
                                            (Error, 'non-existance-cmd')
                                            ])


def test_nested():
    check_token('echo @("hello")', [(Keyword, 'echo'),
                                    (Keyword, '@'),
                                    (Punctuation, '('),
                                    (String.Double, 'hello'),
                                    (Punctuation, ')')])
    check_token('print($(cd))', [(Keyword, 'print'),
                                 (Punctuation, '('),
                                 (Keyword, '$'),
                                 (Punctuation, '('),
                                 (Keyword, 'cd'),
                                 (Punctuation, ')'),
                                 (Punctuation, ')')])
    check_token('print(![echo "])"])', [(Keyword, 'print'),
                                        (Keyword, '!'),
                                        (Punctuation, '['),
                                        (Keyword, 'echo'),
                                        (String.Double, '"])"'),
                                        (Punctuation, ']')])


def test_path():
    HERE = os.path.abspath(os.path.dirname(__file__))
    test_dir = os.path.join(HERE, 'xonsh-test-highlight-path')
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    check_token('cd {}'.format(test_dir), [(Keyword, 'cd'),
                                           (Name.Builtin, test_dir)])
    check_token('cd {}-xxx'.format(test_dir), [(Keyword, 'cd'),
                                               (Text,
                                                '{}-xxx'.format(test_dir))
                                               ])


def test_backtick():
    check_token(r'echo g`.*\w+`', [(String.Affix, 'g'),
                                   (String.Backtick, '`'),
                                   (String.Regex, '.'),
                                   (String.Regex, '*'),
                                   (String.Escape, r'\w'),
                                   ])
