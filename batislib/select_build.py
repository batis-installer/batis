import os
import re

def check_match(candidate, kernel, arch):
    if candidate.get('kernel', 'any').lower() not in {'any', kernel}:
        return False
    
    c_arch = candidate.get('arch', 'any').lower()
    if c_arch in {'any', arch}:
        return True

    # Special case arch 'x86' matches i386, i686
    elif (c_arch == 'x86') and (re.match(r'i\d86', arch)):
        return True
    
    return False

def filter_eligible(candidates):
    uname = os.uname()
    kernel = uname[0].lower()
    arch = uname[4].lower()
    found = False
    for c in candidates:
        if check_match(c, kernel, arch):
            found = True
            yield c

    if not found:
        raise NoEligibleBuild(kernel, arch)

class NoEligibleBuild(Exception):
    def __init__(self, kernel, arch):
        self.kernel = kernel
        self.arch = arch

    def __str__(self):
        return "No suitable builds were found for this platform ({} bit {})"\
                    .format(self.kernel, self.arch)

def later_version(subject, compare_to):
    v1 = [int(p) for p in re.findall(r'\d+', subject)]
    v2 = [int(p) for p in re.findall(r'\d+', compare_to)]
    return v1 > v2

def select_latest(candidates):
    latest = None
    for c in candidates:
        if (latest is None) or later_version(c['version'], latest['version']):
            latest = c

    return latest
