Why distribute applications using Batis?
========================================

Instead of distro packaging
---------------------------

When you release your application using Batis, users can get it from you instantly,
rather than waiting months or years for it to be available in Linux distribution
repositories.

Batis is distro-agnostic, so you can make one package for all Linux users,
instead of dealing with several different packaging technologies, or waiting for
distribution maintainers to take an interest in your package.

The Linux distribution model is very useful for infrastructure, like the Python
runtime or Apache web server - you don't want those changing unexpectedly, and
you can probably wait a few months to take advantage of the newest features.
But it's not great for rapidly-developed, user-facing applications, because it
invariably leaves users a version behind what the developers have released.

Instead of plain tarballs
-------------------------

Batis packages are plain tarballs! If users don't have Batis installed, they
can unpack the tarball and run ``./install.sh`` from the command line, or run
your application directly from the unpacked tarball.

You lose nothing by making your tarballs using Batis, and you get a robust
installer for free.

Users with Batis installed can download and install your application with a
single command. Batis automatically selects an appropriate build for the user's
computer if necessary.
