# This Dockerfile creates an enviroment / dependancies needed to run the
# neutronics-workshop.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop
# docker pull ghcr.io/fusion-energy/neutronics-workshop:embree
# docker pull ghcr.io/fusion-energy/neutronics-workshop:embree-avx

# To build this Dockerfile into a docker image:
# docker build -t neutronics-workshop .


# To build this Dockerfile with different options --build-arg can be used
# --build-arg compile_cores=1
#   int
#   number of cores to compile codes with
# --build-arg build_double_down=OFF
#   ON OFF
#   controls if DAGMC is built with double down (ON) or not (OFF). Note that if double down is OFF then Embree is not included
# --build-arg include_avx=true
#   true false
#   controls if the Embree is built to use AVX instruction set (true) or not (false). AVX is not supported by all CPUs 

#  docker build -t neutronics-workshop --build-arg compile_cores=7 --build-arg build_double_down=OFF .
#  docker build -t neutronics-workshop:embree --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=true .
#  docker build -t neutronics-workshop:embree-avx --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=false .

# for local testing I tend to use this build command
# docker build -t neutronics-workshop --build-arg compile_cores=14 --build-arg build_double_down=ON .
# and then run with this command
# docker run -p 8888:8888 neutronics-workshop

# docker build -t neutronics-workshop --build-arg compile_cores=14 --target base .
# docker run -p 8888:8888 -v ${PWD}/tasks neutronics-workshop

# This can't be done currently as the base images uses conda installs for moab / dagmc which don't compile with OpenMC
FROM ghcr.io/fusion-energy/neutronics-workshop:base as base

ENV OPENMC_CROSS_SECTIONS=/nuclear_data/cross_sections.xml

# Copy over the local repository files
COPY tasks tasks/
COPY tests tests/

WORKDIR /tasks

# this sets the port, gcr looks for this varible
FROM base as jupyter_cmd

ENV PORT 8888

# could switch to --ip='*'
CMD ["jupyter", "lab", "--notebook-dir=/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
