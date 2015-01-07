import os
import tarfile
from tempfile import mkdtemp


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