
# Makefile to build dynamic sources for OpenMC
# this assumes that your source sampling filename is
# source_sampling.cpp 
#
# you can add fortran, c and cpp dependencies to this source
# adding them in FC_DEPS, C_DEPS, and CXX_DEPS accordingly

ifeq ($(FC), f77)
FC = gfortran 
endif 

default: all 

ALL = source_sampling
# add your fortran depencies here
FC_DEPS =
# add your c dependencies here
C_DEPS = 
# add your cpp dependencies here 
CPP_DEPS = plasma_source.cpp
DEPS = $(FC_DEPS) $(C_DEPS) $(CPP_DEPS)
OPT_LEVEL = -O3
FFLAGS = $(OPT_LEVEL) -fPIC
C_FLAGS = -fPIC
CXX_FLAGS = -fPIC

OPENMC_DIR = /home/shimwell/openmc
OPENMC_INC_DIR = $(OPENMC_DIR)/include
OPENMC_LIB_DIR = $(OPENMC_DIR)/lib
# setting the so name is important
LINK_FLAGS = $(OPT_LEVEL) -Wall -Wl,-soname,source_sampling.so 
# setting shared is important
LINK_FLAGS += -L$(OPENMC_LIB_DIR) -lopenmc -lgfortran -fPIC -shared
OPENMC_INCLUDES = -I$(OPENMC_INC_DIR) -I$(OPENMC_DIR)/vendor/pugixml

all: $(ALL) 

source_sampling: $(DEPS)
	$(CXX) source_sampling.cpp $(DEPS) $(OPENMC_INCLUDES) $(LINK_FLAGS) -o $@.so 
# make any fortran objects
%.o : %.F90 
	$(FC) -c $(FFLAGS) $*.F90 -o $@
# make any c objects
%.o : %.c
	$(CC) -c $(FFLAGS) $*.c -o $@
#make any cpp objects
%.o : %.cpp
	$(CXX) -c $(FFLAGS) $*.cpp -o $@
clean: 
	rm -rf *.o *.mod
