sudo docker build -f Dockerfile_openmc -t jbillingsley/multistage:latest .
sudo docker build -f Dockerfile_nuclear_data_tendl -t jbillingsley/multistage:latest .
sudo docker build -f Dockerfile_tasks -t jbillingsley/multistage:latest .
