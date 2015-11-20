Installing Batis
================

.. raw:: html

   <div style="float: right;text-align:center;padding:0 1em;">
   <a href="https://github.com/batis-installer/batis/releases/download/v0.1/batis-0.1.app.tgz" style="text-decoration:none;">
     <img src="_static/download.svg" style="width:96px;display:block;"></object>
     Get tarball
   </a></div>

Naturally, Batis is a Batis package itself. To install Batis the first time,
`download it from here <https://github.com/batis-installer/batis/releases/download/v0.1/batis-0.1.app.tgz>`__,
unpack it and run ``install.sh``::

    tar xzf batis-0.1.app.tgz
    cd batis
    ./install.sh

When a new version of Batis is released, you'll be able to upgrade using the
version you already installed by `clicking here <batis://batis-installer.github.io/batis_index.json>`__,
or by running::

    batis install https://batis-installer.github.io/batis_index.json


.. topic:: Batis packaging from other operating systems

   You can use Batis to make Linux packages from other platforms, such as Mac OS.
   `Download the tarball <https://github.com/batis-installer/batis/releases/download/v0.1/batis-0.1.app.tgz>`__
   and unpack it, and then symlink the ``batis`` script to somewhere on ``$PATH``.

   Packaging from Windows is not yet supported, but it should be possible.
