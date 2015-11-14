import argparse
import logging
import os
import sys
import tarfile
from tempfile import mkdtemp

from .log import enable_colourful_output

pjoin = os.path.join

log = logging.getLogger(__name__)

def unpack_app_tarball(path):
    """Unpack the .app.tar.gz file to a temporary directory.

    Returns the path of the directory containing ``batis_info``.
    """
    tf = tarfile.open(path)

    # Sanity check file names: shouldn't extract files outside the target dir
    for name in tf.getnames():
        if name.startswith('/') or '..' in name.split(os.sep):
            raise ValueError("Bad filename in tarball: %r" % name)

    target = mkdtemp()
    tf.extractall(target)

    if os.path.isdir(os.path.join(target, 'batis_info')):
        return target

    contents = os.listdir(target)
    if len(contents) == 1 and os.path.isdir(
            os.path.join(target, contents[0], 'batis_info')):
        return os.path.join(target, contents[0])

    raise ValueError("Could not find batis_info directory in tarball")

def pack_tarball(directory, output_file=None, name=None, install_script=True):
    directory = os.path.abspath(directory).rstrip(os.sep)
    if name is None:
        name = os.path.basename(directory)
    
    if output_file is None:
        td = mkdtemp()
        output_file = pjoin(td, name+'.app.tar.gz')
    elif os.path.exists(output_file):
        os.unlink(output_file)
    
    tf = tarfile.open(output_file, mode='w:gz')
    log.info('Creating tarball %s', output_file)
    tf.add(directory, arcname=name)
    
    if install_script:
        log.info('Adding install.sh script and Batis files')
        batislibdir = os.path.dirname(__file__)
        install_res = pjoin(os.path.dirname(batislibdir), 'install_resources')
        tf.add(pjoin(install_res, 'install.sh'), arcname=name+'/install.sh')
        tf.add(pjoin(install_res, 'selfinstall.py'),
               arcname=name+'/batis_info/selfinstall.py')

        def filter_exclude_pycache(tarinfo):
            if '__pycache__' not in tarinfo.name:
                return tarinfo
        tf.add(batislibdir, arcname=name+'/batis_info/batislib',
               filter=filter_exclude_pycache)
    
    tf.close()
    return output_file

def pack_main(argv=None):
    ap = argparse.ArgumentParser(prog='batis pack')
    ap.add_argument('-n', '--name',
        help="The application name to use. Uses the directory name if not specified")
    ap.add_argument('-o', '--output-file',
        help="The tarball will be written to this location")
    ap.add_argument('--no-verify', action='store_true',
        help="Skip verifying the application directory before packing it")
    ap.add_argument('--no-install-script', action='store_true',
        help="Don't include a ./install.sh script inside the tarball")
    ap.add_argument('directory', help="The directory to package")
    args = ap.parse_args(argv)
    
    enable_colourful_output(level=logging.INFO)
    
    if not args.no_verify:
        from .verify import UnpackedDirVerifier
        problems = UnpackedDirVerifier(args.directory).verify()
        if problems:
            for problem in problems:
                print(problem)

            print()
            print(len(problems), "problems found in", args.directory)
            sys.exit(1)
    
    pack_tarball(args.directory, args.output_file, args.name,
                 install_script=(not args.no_install_script))
