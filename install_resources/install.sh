#!/bin/sh
appdir=`dirname $0`
# Run the Python installer script with python3 if it exists, python if not
if which python3; then
    python3 $appdir/batis_info/selfinstall.py $appdir
else
    python  $appdir/batis_info/selfinstall.py $appdir
fi
