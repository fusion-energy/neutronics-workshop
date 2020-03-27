docker build -f Dockerfile_openmc -t openmcworkshop/openmc .
docker build -f Dockerfile_openmc_nndc -t openmcworkshop/openmc_nndc .

docker build -f Dockerfile_openmc_dagmc -t openmcworkshop/openmc_dagmc .
docker build -f Dockerfile_openmc_dagmc_nndc -t openmcworkshop/openmc_dagmc_nndc .
docker build -f Dockerfile_openmc_dagmc_nndc_dependencies -t openmcworkshop/openmc_dagmc_nndc_dependencies .
docker build -f Dockerfile_workshop -t openmcworkshop/workshop .