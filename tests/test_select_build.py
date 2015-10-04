try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock
import pytest

from batislib import select_build

def test_filter_eligible():
    candidates = [
        {'kernel': 'Linux', 'arch': 'x86_64'},
        # ----
        {'kernel': 'Linux', 'arch': 'i686'},
        {'kernel': 'FreeBSD', 'arch': 'x86_64'},
        {'kernel': 'FreeBSD', 'arch': 'i386'},
    ]
    with mock.patch('os.uname', return_value=('Linux', '','','', 'x86_64')):
        result = list(select_build.filter_eligible(candidates))
        assert result == candidates[:1]
    
    with mock.patch('os.uname', return_value=('Linux', '','','', 'i999')):
        with pytest.raises(select_build.NoEligibleBuild):
            list(select_build.filter_eligible(candidates))
    
    with mock.patch('os.uname', return_value=('DragonFly', '','','', 'i386')):
        with pytest.raises(select_build.NoEligibleBuild):
            list(select_build.filter_eligible(candidates))

def test_filter_eligible_x86():
    candidates = [
        {'kernel': 'Linux', 'arch': 'x86'},
        # ----
        {'kernel': 'Linux', 'arch': 'x86_64'},
        {'kernel': 'FreeBSD', 'arch': 'x86_64'},
        {'kernel': 'FreeBSD', 'arch': 'i386'},
    ]
    with mock.patch('os.uname', return_value=('Linux', '','','', 'i386')):
        result = list(select_build.filter_eligible(candidates))
        assert result == candidates[:1]
    
    with mock.patch('os.uname', return_value=('Linux', '','','', 'i686')):
        result = list(select_build.filter_eligible(candidates))
        assert result == candidates[:1]
    
    with mock.patch('os.uname', return_value=('Linux', '','','', 'i687')):
        with pytest.raises(select_build.NoEligibleBuild):
            list(select_build.filter_eligible(candidates))

def test_later_version():
    later_version = select_build.later_version
    assert later_version('2.0', '1.9')
    assert later_version('1.0.1', '1')
    assert not later_version('1.2', '1.2')
    assert not later_version('1.2.8', '1.5.3')