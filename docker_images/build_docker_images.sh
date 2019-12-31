docker build -f Dockerfile_openmc -t openmcworkshop/openmc .
docker build -f Dockerfile_nuclear_data_nndc -t openmcworkshop/openmc_nndc .
docker build -f Dockerfile_workshop -t openmcworkshop/openmc_nndc_workshop .
