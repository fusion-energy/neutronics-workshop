docker build -f Dockerfile_openmc_dagmc -t openmcworkshop/openmc_dagmc . --no-cache
docker build -f Dockerfile_nuclear_data_nndc -t openmcworkshop/openmc_dagmc_nndc .
docker build -f Dockerfile_workshop -t openmcworkshop/workshop .
