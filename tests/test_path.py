from splicer.path import pattern_regex, regex_str, tokenize_pattern


def test_tokenize():
    assert list(tokenize_pattern("{artist}/{album}/{track}.{ext}")) == [
        "{artist}",
        "/",
        "{album}",
        "/",
        "{track}",
        ".",
        "{ext}",
    ]

    assert list(tokenize_pattern("{artist}/{album}/{track}-{date}.{ext}")) == [
        "{artist}",
        "/",
        "{album}",
        "/",
        "{track}",
        "-",
        "{date}",
        ".",
        "{ext}",
    ]


def test_compile_regex_str():
    assert regex_str(["{artist}"]) == "(?P<artist>[^/]*)"

    assert (
        regex_str(["{artist}", "/", "ignored", "/", "{foo}"])
        == r"(?P<artist>[^/]*)/ignored/(?P<foo>[^/]*)"
    )


def test_pattern_regex():
    regex, columns = pattern_regex("{artist}/{album}/{track}.{ext}")

    assert regex.match("nirvana/nevermind/02.ogg").groups() == (
        "nirvana",
        "nevermind",
        "02",
        "ogg",
    )
