What Batis is not
=================

Batis is not:

* A replacement for system package managers. Applications can depend on system
  packages, but they cannot depend on each other.
* Especially secure. Concepts like capabilities based security and containerisation
  are very much needed for user applications, and there are other projects
  such as `Subuser <http://subuser.org/>`_ exploring those. In the interests
  of keeping it simple, Batis does not implement anything like this.
* A ground-up rethink of installing applications. There are interesting ideas
  out there to redesign how applications are installed and run, using technologies
  like btrfs volumes or OverlayFS. Batis aims at incrementally improving the
  status quo, both to keep things simple for application developers, and to
  avoid the catch 22 situation where neither users not developers are interested
  in a technology until it's adopted by the other group.
