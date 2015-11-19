from batislib import verify_index

SAMPLE_OK = {
    'name': 'My App',
    'byline': 'Easily frobulate pufoos on demand',
    'icon_url': 'https://example.com/myapp_logo.png',
    'builds': [
        {
          "url": "https://example.com/downloads/myapp_0.1_linux_64bit.app.tar.gz",
          "sha512": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
          "version": "0.1",
          "kernel": "Linux",
          "arch": "x86_64"
        },
    ],
    'format_version': [1, 0],
}

def test_ok():
    problems = verify_index.IndexVerifier(SAMPLE_OK).verify()
    assert problems == []

SAMPLE_NO_BUILDS = {
    'name': 'My App',
    'byline': 'Frobulate pufoos',
    'icon_url': 'https://example.com/myapp_logo.png',
    'builds': [],
    'format_version': [1, 0],
}

def test_no_builds():
    problems = verify_index.IndexVerifier(SAMPLE_NO_BUILDS).verify()
    assert len(problems) == 1

SAMPLE_BAD_FORMAT_VERSION = {
    'name': 'My App',
    'byline': 'Easily frobulate pufoos on demand',
    'icon_url': 'https://example.com/myapp_logo.png',
    'builds': [
        {
          "url": "https://example.com/downloads/myapp_0.1_linux_64bit.app.tar.gz",
          "sha512": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
          "version": "0.1",
        },
    ],
    'format_version': [0, 3],
}

def test_bad_format_version():
    problems = verify_index.IndexVerifier(SAMPLE_BAD_FORMAT_VERSION).verify()
    assert len(problems) == 1

SAMPLE_BUILD_HTTP_NO_HASH = {
    "url": "http://example.com/downloads/myapp_0.1_linux_64bit.app.tar.gz",
    "version": "0.1",
}

def test_http_no_hash():
    problems = []
    iv = verify_index.IndexVerifier(None)
    iv.verify_build_json(SAMPLE_BUILD_HTTP_NO_HASH, problems)
    assert len(problems) == 1
