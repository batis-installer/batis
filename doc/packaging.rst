Packaging an application using Batis
====================================

.. note::

   This describes how to work directly with Batis to distribute an application.
   I hope that higher level tools will offer simpler ways to do this in the
   future.

1. Prepare a directory containing your built application, so that it can run
   regardless of where the directory is located (i.e. everything inside the
   application is loaded by relative paths).
2. Add a :file:`batis_info` subdirectory in the top level of this application
   directory. This should contain:
   
   * :file:`metadata.json` - a JSON object containing information about your
     application, including:

     - ``name`` - the human readable name of your application.
     - ``byline`` - a very brief description of your application, which may be
       displayed by installers.
     - ``icon`` - the relative path to an icon file within your application
       directory. This may be displayed by graphical installers.
     - ``commands`` - list of objects, each with 'name' and 'target' keys.
       ``target``, a path relative to the root of your application directory,
       will be symlinked as ``name`` to a location on :envvar:`PATH`. E.g.::
       
           "commands": [{"target": "bin/launch.sh", "name": "myapp"}]
       
   * :file:`dependencies.json` - optional, a JSON object with details about
     external packages that need to be installed for you application. See
     :ref:`dependencies` for more details.
     
     - ``system_packages`` - a specification of distro packages that the user
       must have installed. See :ref:`dependencies` for details.
     - ``description`` - a string listing the same distro
       packages in human-readable form. This will be shown to the user if Batis
       can't automatically install the dependencies. E.g. for a PyQt application,
       this could be ``"Python 3, PyQt5"``.

   * :file:`desktop/*.desktop` - Zero to many desktop entry files
     (`spec <http://standards.freedesktop.org/desktop-entry-spec/latest/>`__).
     These can add your application to desktop menus or launchers, and associate
     it with given mime types. You can use ``{{INSTALL_DIR}}`` inside these to
     refer to your application's directory::
     
         Exec="{{INSTALL_DIR}}/bin/foo" %F
     
   * :file:`mime/*.xml` - Zero to many mime database XML source files
     (`spec <http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625833214912>`__,
     `tutorial <http://www.freedesktop.org/wiki/Specifications/AddingMIMETutor/>`_).
     These can define new file types for your application.
   * :file:`icons/{theme}/{size}x{size}/{category}/{name}.png` - icons for your
     application and new mime types. Theme will normally be 'hicolor', which
     is used as the fallback theme, and you should include hicolor variants
     in addition to any other theme you want to add icons for. You should
     install at least a 48x48 pixel icon; other square sizes are optional.
     Category will typically be either 'apps' or 'mimetype'.
     (`Icon theme spec <http://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html>`_)

3. Use ``batis verify`` to check that all the necessary information is in
   place::

       batis verify path/to/app_directory

   Fix any problems that this reports.

4. Pack the directory into a tarball::

       batis pack path/to/app_directory -n myapp -o myapp-0.1.app.tgz

   This makes a gzipped tarball of the directory you're using, and adds an
   ``install.sh`` script, along with the necessary Batis files, so that users
   without Batis can easily install your application. Upload the tarball
   somewhere publicly accessible.

5. Prepare a :ref:`build index file <build_index>`, and add it to your project's
   website as ``/batis_index.json``.

You can now invite users with Batis to install your application by running::

    batis install example.com/myapp/

For users without Batis installed, provide links directly to the tarballs, and
instructions to download, un-tar and run ``./install.sh``.

.. _dependencies:

Dependencies
------------

Dependencies are third party code or resources that your application uses. Batis
lets you choose whether to bundle dependencies inside your tarball, or specify
that they should be installed by a system package manager. Each has advantages:

- Bundled dependencies isolate you from API changes in your dependency, because
  the version your code uses is fixed until you decide to update it.
- Separately installed dependencies mean your users can benefit from security
  and performance improvements in the dependencies without you needing to make a
  new release. It also means your tarball is smaller.

In general, I recommend that you specify only large, stable dependencies - such
as Python, Java or Qt - for external installation.

Different distributions use different naming schemes for packages, so the
``system_packages`` field in dependencies.json is a list of possible specifications,
allowing Batis to choose one suited to the user's distribution. For instance::

    [
        {
            "package_manager": "apt-get",
            "packages": ["python3", "python3-pyqt5", "python3-pyqt5.qtsvg"]
        },
        {
            "package_manager": "yum",
            "packages": ["python3", "python3-qt5"]
        }
    ]

Each specification has either a ``package_manager`` field or a
``distribution`` field. Use ``package_manager`` where possible, because it's
less specific: ``"package_manager": "apt-get"`` will work on Debian,
Ubuntu, Linux Mint, and many other derivatives. Batis recognises these
package managers::

    apt-get, yum, zypper, urpmi, pacman, sbopkg, equo, emerge

If you need to do something different for a specific distribution, run
``lsb_release -i`` to find the name to use. Put it before the more general
specification in the list; Batis will use the first one that matches when
installing.

The user will be prompted for their password for sudo access to install the
necessary system packages.

If no specification matches, or installing the system packages fails, Batis
will ask the user to ensure the dependencies are installed. It uses the
``description`` field in ``dependencies.json`` for this.

If your package doesn't require any system packages, you can leave the
``dependencies.json`` file out.

.. _build_index:

The builds index
----------------

When users install an application using a URL, Batis looks for an index
file called ``batis_index.json``. For example, to let users
``batis install https://example.com/``, you would put the index at::

    https://example.com/batis_index.json

The index file must be available over HTTPS. Hosting your website on
`Github Pages <https://pages.github.com/>`__ is one easy and free way to support
HTTPS.

The index should be JSON, looking like this::

    {
      "name": "My App",
      "builds": [
        {
          "url": "https://example.com/downloads/myapp_0.1_linux_64bit.app.tar.gz",
          "sha512": "48157035840[...]bd4a14146b9",
          "version": "0.1",
          "kernel": "Linux",
          "arch": "x86_64"
        },
        ...
      ]
    }

.. topic:: Checking your index

   When you create or update your index, check that it has the necessary
   information by running::
   
       batis verify-index <path_or_url>

Batis will select an appropriate build for the user's system based on the
``kernel`` and ``arch`` fields. These should match the results of ``uname -s``
and ``uname -m`` respectively, and are not case sensitive. As a special case,
``"arch": "x86"`` will match ``i386``, ``i686``, and any ``i<N>86``.

If your application doesn't need separate builds for different kernels or
architectures—for instance, if it only contains Python code with no C extensions
—you can set these fields to "any", or omit them entirely.

If there are multiple suitable builds, Batis will take the one with the highest
version number. The version number should contain one or more numeric parts,
separated by non-numeric characters such as ``.``. Batis ignores any non-numeric
parts. You can use negative numbers for pre-releases (e.g. ``2.0.-1.3``).

The preferred build will be downloaded from the URL given. HTTP URLs are allowed
here, but they must have a hash.

The ``sha512`` field is recommended if you specify an https URL, and mandatory
for http. If provided, it must match the SHA-512 hash of the tarball available
for download.

.. topic:: Future extensions

   Future versions of Batis may use extra fields in the index to download
   incremental upgrades, smaller packages containing just the differences
   between two versions of the application.
   The index could also contain information for downloading tarballs using
   peer-to-peer mechanisms like IPFS or BitTorrent.
