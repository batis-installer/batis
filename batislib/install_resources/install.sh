#!/bin/sh
appdir=`dirname $0`
# Run the Python installer script with python3 if it exists, python if not
which python3 && python3 $appdir/batis_info/selfinstall.py $appdir \
              || python  $appdir/batis_info/selfinstall.py $appdir
