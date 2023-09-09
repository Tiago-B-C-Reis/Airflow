Start the "docker-compose.yaml" procees:
    - docker-compose up -d

Check the servers in "docker-compose.yaml".
    - docker-compose ps


Section 4 -------------------------------------------------------------------------

# check if a task is running:
Enter inside the "airflow-webserver" container:
    - docker exec -it materials-airflow-scheduler-1 /bin/bash
Check all the commands that can be executed inside the container above:
    - airflow -h
Check if some taks was executed with success: (in the case the "create_table" taks inside the "user_processing" DAG)
    - airflow tasks test user_processing create_table 2023-01-01
    - control + D to exit

# Check if after the DAG was successfuly runned if the csv file was created:
Enter inside the "materials-airflow-worker-1" container:
    - docker exec -it materials-airflow-worker-1 /bin/bash
Verify the existing files:
    - ls /tmp/

# Check the "processed_user.csv" content:
Enter inside the "materials-postgres-1" container:
    - docker exec -it materials-postgres-1 /bin/bash
Enter inside the Postgres cli and check the content of the table "users":
    - psql -Uairflow
    - SELECT * FROM users;




Section 5 -------------------------------------------------------------------------

# Copy the configuration file of arflow from the container to the host (the machine that is being used)
Enter this code:
    - docker cp materials-airflow-scheduler-1:/opt/airflow/airflow.cfg .

# How to acess "flower" wich is a web base tool to manage and monitor "Celery" clusters.
Enter this code:
    - docker-compose down && docker-compose --profile flower up -d

# Restart the docker compose:
    - docker-compose down && docker-compose up -d



Section 7 -------------------------------------------------------------------------

# Set up ElasticSearch docker compose:
    - docker-compose -f docker-compose-es.yaml up -d
# Check the containers state:
    - docker-compose -f docker-compose-es.yaml ps
# Enter inside the scheduler from docker compose es:
    - docker exec -it materials-airflow-scheduler-1 /bin/bash
# If this command runs it means that ElasticSearch with Docker was successfuly installed:
    - curl -X GET 'http://elastic:9200'



Section 8 -------------------------------------------------------------------------

# Set up or register plugins into Airflow:
Step 1, enter the shedule container:
    - docker exec -it materials-airflow-scheduler-1 /bin/bash
step 2, check the existin plugins:
    - airflow plugins
step 3, for this exaple, register the "elastic" hook thorught the airflow plugin manager:
    - one this case, add this class at the end of the "elastic_hook.py" plugin:
    "class AirflowElasticPlugin(AirflowPlugin):
    name = 'elastic'
    hooks = [ElasticHook]"

step 4, restart the airflow instance:
    - docker-compose -f docker-compose-es.yaml stop && docker-compose -f docker-compose-es.yaml up -d