Installing applications using Batis
===================================

You can install an application packaged with Batis by unpacking the tarball and
running the ``install.sh`` file inside it. But if you :doc:`install Batis <install-batis>`,
you can install applications with a single command::

    batis install www.some-app.com

The application's website should tell you what URL to use in that command.

Uninstalling applications
-------------------------

::

    batis uninstall <name>

.. todo: finding the name

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
