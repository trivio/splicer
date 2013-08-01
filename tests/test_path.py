from nose.tools import *

from splicer.path import tokenize_pattern, regex_str, pattern_regex

def test_tokenize():
  eq_(
    list(tokenize_pattern("{artist}/{album}/{track}.{ext}")),
    ['{artist}','/','{album}','/','{track}', '.','{ext}'] 
  )

  eq_(
    list(tokenize_pattern("{artist}/{album}/{track}-{date}.{ext}")),
    ['{artist}','/','{album}','/','{track}', '-', '{date}', '.','{ext}'] 
  )

def test_compile_regex_str():
  eq_(
    regex_str(['{artist}']),
    '(?P<artist>[^/]*)'
  )

  eq_(
    regex_str(['{artist}', '/','ignored', '/', '{foo}']),
    r'(?P<artist>[^/]*)\/ignored\/(?P<foo>[^/]*)'
  )

def test_pattern_regex():
  regex, columns = pattern_regex("{artist}/{album}/{track}.{ext}")

  eq_(
    regex.match("nirvana/nevermind/02.ogg").groups(),
    ("nirvana", "nevermind", "02", "ogg")
  )


