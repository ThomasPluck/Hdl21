#!/bin/bash

# Install the sky130 PDK
git clone https://github.com/RTimothyEdwards/open_pdks.git
cd open_pdks
./configure --enable-sky130-pdk
make

# this is intended for use in a docker container, so we don't need to
# use sudo, however, if you are installing on a local machine, you
# will need to use sudo.
make install