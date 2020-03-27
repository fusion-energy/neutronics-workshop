docker build -f Dockerfile_openmc -t openmcworkshop/openmc . --no-cache
docker build -f Dockerfile_openmc_nndc -t openmcworkshop/openmc_nndc . --no-cache

docker build -f Dockerfile_openmc_dagmc -t openmcworkshop/openmc_dagmc . --no-cache
docker build -f Dockerfile_openmc_dagmc_nndc -t openmcworkshop/openmc_dagmc_nndc . --no-cache
docker build -f Dockerfile_openmc_dagmc_nndc -t openmcworkshop/openmc_dagmc_nndc . --no-cache
docker build -f Dockerfile_openmc_dagmc_nndc_dependencies -t openmcworkshop/openmc_dagmc_nndc_dependencies . --no-cache
docker build -f Dockerfile_workshop -t openmcworkshop/workshop . --no-cache