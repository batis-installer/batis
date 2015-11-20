Installing applications
=======================

With Batis installed, you can install applications by clicking a link on the
application's webpage. For example: `install a sample application
<batis://batis-installer.github.io/example-apps/pyqt/batis_index.json>`__.

If you prefer to use the command line, copy the URL from the link (it will begin
with ``batis://``), and run::

    batis install batis://...

You can also install an application packaged with Batis by unpacking the tarball
and running the ``install.sh`` file inside it, whether or not you have Batis
installed.

Uninstalling applications
-------------------------

::

    batis uninstall <name>

Run ``batis list`` to see the names of installed applications.

Adapting applications not packaged with Batis
---------------------------------------------

It may be possible to install an application with Batis even if the developers
didn't package it for that. This can add launcher entries and file associations
which would otherwise need to be set up manually. It also gives you a standard
way to uninstall applications.

Adapters for suitable applications are being collected in the
`batis-adapt repository <https://github.com/batis-installer/batis-adapt>`__.
See if there's already an adapter for the application you want, and if not,
consider adding one.
