# build with the following command
# sudo docker build -t openmcworkshop/workshop .

FROM openmcworkshop/openmc_workshop_dependencies:openmc_dagmc_nndc_dependencies

RUN git clone https://github.com/ukaea/openmc_workshop

WORKDIR /openmc_workshop