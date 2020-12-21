#!/bin/bash
set -eu

function build_embree() {
    if [ -d $PWD/embree ] ; then
	echo "Embree installed"
	return
    fi

    # make embree
    git clone https://github.com/embree/embree
    cd embree
    echo "EMBREE being installed in "$EMBREE_DIR
    mkdir bld
    cd bld
    cmake .. -DCMAKE_INSTALL_PREFIX=.. -DEMBREE_ISPC_SUPPORT=OFF
    make -j4
    make install
    cd ..
    cd ..
}

function build_double() {
    if [ -d $PWD/double-down ] ; then
	echo "double down already installed"
	return
    fi
    echo $EMBREE_DIR
    # make double down
    git clone https://github.com/pshriwise/double-down
    cd double-down
    export DD_DIR=$PWD
    mkdir bld
    cd bld
    cmake .. -DCMAKE_INSTALL_PREFIX=.. -DMOAB_DIR=$MOAB_DIR -DEMBREE_DIR=$EMBREE_DIR -DEMBREE_ROOT=$EMBREE_DIR
    make -j4
    make install 
    cd ..
    cd ..
}

function build_dagmc() {
    if [ -d $PWD/dagmc ] ; then
	echo "dagmc already built"
	return
    fi    
    # make dagmc
    git clone https://github.com/svalinn/dagmc
    cd dagmc
    mkdir bld
    cd bld
    cmake .. -DMOAB_DIR=$MOAB_DIR -DBUILD_STATIC_LIBS=OFF -DDOUBLE_DOWN=ON -DDOUBLE_DOWN_DIR=$DD_DIR -DCMAKE_INSTALL_PREFIX=..
    make -j4
    make install
    cd ..
    cd ..
}

function build_openmc() {
    if [ -d $PWD/openmc ] ; then
	echo "openmc already built"
	return
    fi    
    # make dagmc
    git clone https://github.com/openmc-dev/openmc
    cd openmc
    mkdir bld
    cd bld
    cmake .. -Ddagmc=ON -DDAGMC_DIR=$DAGMC_DIR -DCMAKE_INSTALL_PREFIX=$OPENMC_INSTALL_DIR
    make -j4
    make install
    cd ..
    cd ..
}

# need to know where MOAB is
if [ -z $MOAB_DIR ] ; then
  echo "Must set MOAB_DIR outside the script"
  echo "i.e. export MOAB_DIR=/path/to/moab" 
  exit 1
fi

# need to know where to install openmc is
if [ -z $OPENMC_INSTALL_DIR ] ; then
  echo "Must set OPENMC_INSTALL_DIR outside the script"
  echo "i.e. export MOAB_DIR=/path/to/moab"
  echo " or OPENMC_DIR=/path/to/thing/"
  exit 1
fi

export DAGMC_DIR=$PWD/dagmc/lib/cmake
export EMBREE_DIR=$PWD/embree/lib/cmake/embree-3.12.1
export DD_DIR=$PWD/double-down/lib/cmake

sudo apt-get install cmake-curses-gui
sudo apt-get install libtbb-dev
sudo apt-get install libglfw3-dev
sudo apt-get install libeigen3-dev

build_embree
build_double
build_dagmc
build_openmc

# all done
echo "all done"


