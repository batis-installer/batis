Why distribute applications using Batis?
========================================

Instead of distro packaging
---------------------------

Using Batis, when you release your application, users can get it instantly,
rather than waiting months or years for it to be available in Linux distribution
repositories.

Batis is distro-agnostic, so you can make one package for all Linux users,
instead of dealing with several different packaging technologies, or waiting for
distribution maintainers to take an interest in your package.

*The Linux distribution model is very useful for infrastructure - you don't want
that changing unexpectedly, and you can probably wait a few months to take
advantage of the newest features. But it's terrible for rapidly-developed,
user-facing applications, because it invariably leaves users a version behind
what the developers have released.*

Instead of plain tarballs
-------------------------

Batis packages are plain tarballs! If users don't have Batis installed, they
can unpack the tarball and run ``./install`` from the command line, or run your
application directly from the unpacked tarball. If they do have Batis, when they
click on the tarball, they will be prompted to install it.

Batis packages have a ``.app.tar.gz`` file extension. If the system doesn't know
about this, it just treats it as a regular ``.tar.gz`` tarball.

So you lose nothing by making your tarballs using Batis.
