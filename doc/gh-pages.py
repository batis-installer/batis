"""Script to commit the doc build outputs into the github-pages repo.
"""

import os
import datetime
import sys
from os import chdir as cd
from os.path import dirname, join as pjoin

from subprocess import check_call, check_output

pages_dir = pjoin(dirname(__file__), 'gh-pages')
html_dir = pjoin(dirname(__file__), '_build/html')
batis_index_file = pjoin(dirname(__file__), 'batis_index.json')
pages_repo = 'git@github.com:batis-installer/batis-installer.github.io.git'


def git(*args):
    check_call(['git'] + list(args))

def init_repo(path):
    """clone the gh-pages repo if we haven't already."""
    git('clone', pages_repo, path, '--depth=10')
    # For an <x>.github.io site, the pages go in master, so we don't need
    # to checkout gh-pages.


if __name__ == '__main__':
    startdir = os.getcwd()
    if not os.path.exists(pages_dir):
        init_repo(pages_dir)    # Clone the repo
    else:
        # ensure up-to-date before operating
        cd(pages_dir)
        git('checkout', 'master')
        git('pull')
        cd(startdir)

    # This is pretty unforgiving: we unconditionally nuke the destination
    # directory, and then copy the html tree in there
    check_call('rm -r %s/*' % pages_dir, shell=True)
    
    check_call('cp -r %s/* %s/' % (html_dir, pages_dir), shell=True)
    check_call('cp -r %s %s/' % (batis_index_file, pages_dir), shell=True)
    
    with open(pjoin(pages_dir, '.nojekyll'), 'w'):
        # Creating empty .nojekyll file
        pass

    try:
        cd(pages_dir)
        branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])\
                 .decode('utf-8').rstrip()
        if branch != 'master':
            e = 'On %r, git branch is %r, MUST be "master"' % (pages_dir,
                                                                 branch)
            raise RuntimeError(e)

        git('add', '-A')        

        git('commit', '-m', 'Updated website (automated commit) – %s' %
                    datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

        print()
        print('Most recent 3 commits:')
        sys.stdout.flush()
        git('--no-pager', 'log', '--oneline', 'HEAD~3..')
    finally:
        cd(startdir)

    print()
    print('Now verify the build in: %r' % pages_dir)
    print("If everything looks good, 'git push'")
