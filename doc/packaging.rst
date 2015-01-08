Packaging an application using Batis
====================================

.. note::

   I hope that, as Batis becomes more widely adopted, there will be tools to
   automate this process for certain kinds of applications. For now, this
   describes building a package manually.

1. Prepare a directory containing your built application, so that it can run
   regardless of where the directory is located (i.e. everything inside the
   application is loaded by relative paths).
2. Add a :file:`batis_info` subdirectory in the top level of this application
   directory. This should contain:
   
   * :file:`metadata.json` - a JSON object containing information about your
     application, including:

     - ``commands`` - list of objects, each with 'name' and 'target' keys.
       ``target``, a path relative to the root of your application directory,
       will be symlinked as ``name`` to a location on :envvar:`PATH`.

   * :file:`desktop/*.desktop` - Zero to many desktop entry files
     (`spec <http://standards.freedesktop.org/desktop-entry-spec/latest/>`_).
     These can add your application to desktop menus or launchers, and associate
     it with given mime types.
   * :file:`mime/*.xml` - Zero to many mime database XML source files
     (`spec <http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625833214912>`_,
     `tutorial <http://www.freedesktop.org/wiki/Specifications/AddingMIMETutor/>`_).
     These can define new file types for your application.
   * :file:`icons/{theme}/{size}x{size}/{category}/{name}.png` - icons for your
     application and new mime types. Theme will normally be 'hicolor', which
     is used as the fallback theme, and you should include hicolor variants
     in addition to any other theme you want to add icons for. You should
     install at least a 48x48 pixel icon; other square sizes are optional.
     Category will typically be either 'apps' or 'mimetype'.
     (`Icon theme spec <http://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html>`_)

3. Copy in installer shim for users who don't have Batis. (Todo: details)
4. Make the directory into a tarball, with a ``.app.tar.gz`` extension. At the
   command line, you can do so like this::
   
       tar -cvzf foo.app.tar.gz app_directory

5. Check the tarball by running::

       batis verify foo.app.tar.gz

   Fix any problems that this reports.


You can now distribute your `.app.tar.gz` file. Users with Batis will be prompted
to install it; users without can unpack the tarball and run ``./install``.

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
