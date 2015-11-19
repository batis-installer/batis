"""Verify a batis_index.json file"""
import argparse
import json
import os.path
import re
import requests

from .urlinstall import prepare_index_url

def load_index(path_or_url):
    if path_or_url.startswith(('http://', 'https://')) \
            or not os.path.isfile(path_or_url):
        url = prepare_index_url(path_or_url)
        return requests.get(url).json()
    else:
        with open(path_or_url) as f:
            return json.load(f)

class IndexVerifier:
    def __init__(self, contents):
        self.contents = contents

    def verify_json(self, problems):
        pa = problems.append
        c = self.contents
        if not isinstance(c, dict):
            pa("Index must be a JSON object at the top level, not {}"
                .format(type(c)))
            return
        
        if 'name' in c:
            if not isinstance(c['name'], str):
                pa("'name' field should be a string")
            elif c['name'] == '':
                pa("'name' field must not be empty")
        else:
            pa("Index must have a 'name' field at the top level")

        if 'byline' in c:
            if not isinstance(c['byline'], str):
                pa("'byline' field should be a string")
            elif c['byline'] == '':
                pa("'byline' field must not be empty")
        else:
            pa("Index must have a 'byline' field at the top level")

        if 'icon_url' in c:
            if not isinstance(c['icon_url'], str):
                pa("'icon_url' field should be a string")
            elif c['icon_url'] == '':
                pa("'icon_url' field must not be empty")
        else:
            pa("Index should have a 'icon_url' field")
        
        if 'format_version' in c:
            fv = c['format_version']
            if isinstance(fv, list) and len(fv) == 2:
                if fv != [1, 0]:
                    pa('This code is only to verify format_version 1.0 (found %s.%s)' % tuple(fv))
            else:
                pa('format_version is not a list of length 2: %r' % fv)
        else:
            pa('Index should have a format_version field')

        if 'builds' not in c:
            pa("Index must have a 'builds' field at the top level")
            return
            
        builds = self.contents['builds']
        
        if not isinstance(builds, list):
            pa("'builds' field should be a JSON array, not {}"
                .format(type(builds)))
            return
        elif builds == []:
            pa("'builds' is an empty list")
        
        for b in builds:
            self.verify_build_json(b, problems)
    
    def verify_build_json(self, b, problems):
        pa = problems.append
        if not isinstance(b, dict):
            pa("'builds' should be an array of objects - found {}"
                .format(type(b)))
            return
        
        if 'url' in b:
            if not b['url'].startswith(('http://', 'https://')):
                pa("Build URL should start with 'https://' or 'http://'")
            if b['url'].startswith('http://') and 'sha512' not in b:
                pa("Build must have 'sha512' field with http:// URL")
        else:
            pa("Build is missing 'url' field")
        
        if 'sha512' in b:
            if not isinstance(b['sha512'], str):
                pa("build 'sha512' field should be a string, not {}"
                    .format(type(b['sha512'])))
            elif len(b['sha512']) != 128:
                pa("sha512 hahes are 128 characters long, but '{}...' is only {} characters"
                    .format(b['sha512'][:8], len(b['sha512'])))
        
        if 'version' in b:
            if not isinstance(b['version'], str):
                pa("Build 'version' field should be a string, not {}"
                    .format(type(b['version'])))
            elif not re.search(r'\d+', b['version']):
                pa("No numeric part found in version string {!r}"
                    .format(b['version']))
        else:
            pa("Build is missing 'version' field")
        
        for field in ('kernel', 'arch'):
            if field in b:
                if not isinstance(b[field], str):
                    pa("Build '{}' field should be a string, not {}"
                        .format(field, type(b[field])))
                elif b[field] == '':
                    pa(("Build '{}' field should not be empty. "
                        "If it doesn't matter, set it to 'any' or omit it")
                        .format(field))
        

    def verify(self):
        problems = []
        self.verify_json(problems)
        return problems

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis verify-index')
    ap.add_argument('url',
            help="URL or file path of batis_index.json")
    args = ap.parse_args(argv)

    contents = load_index(args.url)
    problems = IndexVerifier(contents).verify()
    
    for problem in problems:
        print(problem)
    
    if problems:
        print()
        print(len(problems), "problems found in", args.url)
        return 1
    else:
        print("No problems found in", args.url)
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())