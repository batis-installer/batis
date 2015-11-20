FAQs
====

Security
--------

Batis assumes that the user who installs an application trusts the developer who
wrote it. It aims to ensure that the software you download is what the real author
provided, but it doesn't check that the author is trustworthy, and it doesn't
sandbox installed applications.

This is not a great security model, but in practice it's one we're all used to
using. I deliberately didn't try to do something more secure, because designing
and implementing a good security model is hard. I don't want to promise security
that I can't really provide, and I don't want to put developers off by adding
extra requirements.

I'm still thinking about security, and a future version of Batis might integrate
something like capabilities based security, or a means of calculating reputation.
There are interesting projects like `Subuser <http://subuser.org/>`__ working on
this. But this is not a priority for me at the moment.

Why not use Linux distro packaging?
-----------------------------------

Batis packaging for desktop applications is designed to sit alongside distro
packaging for system components and infrastructure.
There are two major advantages to using Batis:

- Users can install an application as soon as the developers release it.
  There's no need to wait months and upgrade the entire system at once to get
  the latest software.
- One package works on any distribution, so developers can distribute their
  application without having to learn about several different packaging systems.

I've `written more about this <http://takluyver.github.io/posts/why-did-i-write-yet-another-package-manager.html>`__
on my blog.

Can I distribute proprietary applications using Batis?
------------------------------------------------------

Yes. There are no restrictions on what type of application you can distribute.

Where do I upload packages?
---------------------------

Batis is not an app store - users will download the packages directly from your
website. For open source projects, code hosting services like Github, Bitbucket
and Sourceforge let you upload files and make them available.

In the future there might be a centralised index of Batis packages.

'Batis' - The name
------------------

Batis is:

- The Basic Application Tarball Installation Specification
- A Better Approach To Installing Stuff
- A genus of salt tolerant `plants <https://en.wikipedia.org/wiki/Batis_%28plant%29>`_
- A genus of African `birds <https://en.wikipedia.org/wiki/Batis_%28bird%29>`_
- A female `philosopher <https://en.wikipedia.org/wiki/Batis_of_Lampsacus>`_
  in Ancient Greece
- An Achaemenid `military commander <https://en.wikipedia.org/wiki/Batis_%28commander%29>`_

Take your pick!
