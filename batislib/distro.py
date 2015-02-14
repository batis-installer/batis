"""Handling of distros and system package managers
"""
from collections import OrderedDict
import os
import subprocess
import errno

from .util import which

def find_distro_name():
    """Try to find the distro name.

    This currently uses lsb_release -i. Fallbacks may be added in the future
    for distributions that don't provide that.

    Returns a string, or None if it couldn't find a name.
    """
    try:
        o = subprocess.check_output(['lsb_release', '-i'])
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    else:
        for line in o.decode('utf-8').splitlines():
            if ':' in line:
                return line.split(':', 1)[1].strip()

    # TODO: Handling for when lsb_release isn't available?
    # This might be useful: http://linuxmafia.com/faq/Admin/release-files.html

package_manager_commands = OrderedDict([
    ('apt-get', ['apt-get', '--yes', 'install', '{packages}']),  # Debian, Ubuntu etc.
    ('yum', ['yum', '--assumeyes', 'install', '{packages}']),    # Fedora
    ('zypper', ['zypper', '--non-interactive', 'install', '{packages}']),  # OpenSUSE
    ('urpmi', ['urpmi', '--auto', '{packages}']),
    ('pacman', ['pacman', '-S', '--noconfirm', '{packages}']),   # Arch
    ('sbopkg', ['sbopkg', '-B', '-e', 'stop', '-i', '{packages_wsjoin}']), # Slackware
    ('equo', ['equo', 'install', '{packages}']),          # Sabayon
    ('emerge', ['emerge', '{packages}']),                 # Gentoo
])

def find_package_manager_command():
    """Find which package manager command is available on the system.

    Returns one of the keys of package_manager_commands, or None if none
    of those are found.
    """
    for cmd in package_manager_commands:
        if which(cmd):
            return cmd

def select_dependencies_spec(candidates):
    """Select the first matching dependency specification from a list.

    candidates should be a list of dictionaries, each with at least one of
    'distro_name' and 'package_manager' keys. The first one where distro_name
    matches the system, or distro_name is missing and package_manager matches,
    will be returned.

    None will be returned if none of the candidates match.
    """
    distro_name = find_distro_name()
    packageman = find_package_manager_command()
    for spec in candidates:
        if 'distro_name' in spec:
            if spec['distro_name'] == distro_name:
                if 'package_manager' not in spec:
                    spec = spec.copy()
                    spec['package_manager'] = packageman
                return spec
            else:
                continue

        if spec['package_manager'] == packageman:
            return spec

def install_packages(package_names, sudo_cmd='sudo', **kwargs):
    """Install a list of packages using the system package manager.

    If not running as root, sudo_cmd will be placed before the list of
    arguments.

    **kwargs will be passed on to :class;`subprocess.Popen`

    Returns a 3-tuple (stdout, stderr, returncode). stdout and stderr will be
    None unless you pass :data:`subprocess.PIPE`.
    """
    pm = find_package_manager_command()
    argv = package_manager_commands[pm][:]  # [:] copies so we don't modify the original
    if '{packages_wsjoin}' in argv:
        ix = argv.index('{packages_wsjoin}')
        argv[ix] = ' '.join(package_names)
    else:
        ix = argv.index('{packages}')
        argv[ix:ix+1] = package_names

    # I'm assuming all distro package managers require root access.
    if os.getuid() != 0:
        argv.insert(0, sudo_cmd)

    p = subprocess.Popen(argv, **kwargs)
    return p.communicate() + (p.returncode,)
