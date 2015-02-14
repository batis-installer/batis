from os.path import dirname, join as pjoin
from batislib import verify

batis_root = dirname(dirname(__file__))

def test_verify_sampleapp():
    problems = verify.verify_tarball_or_directory(pjoin(batis_root, 'sampleapp'))
    assert problems == []
