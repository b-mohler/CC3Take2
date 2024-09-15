# Assignment 3
The final step in this project was to improve on the work done in step 2 by upgrading the functions to create, read, update, and destroy items by incorporating DynamoDB table and an S3 bucket, developing more robust testing measures, and then using Localstack to run a mock of AWS as part of the application stack.

## The Workflow
The workflow file is test.yml. It runs automatically when pushes or pull requests are made to the main branch and can also be triggered manually from the actions tab. It will checkout the code, set up python, install docker compose, install the dependencies, make the shell files executable, build and run stack, and then run the tests. 

## The Code
The app.py file contains all the functions for creating, reading, updating and destroying items as well as groundwork to run locally using AWS. The test_flask_app.py file includes testing to fit the following criteria: 
- Sending a GET request with appropriate parameters returns expected JSON from the database
- Sending a GET request that finds no results returns the appropriate response
- Sending a GET request with no parameters returns the appropriate response
- Sending a GET request with incorrect parameters returns the appropriate response
- Sending a POST request results in the JSON body being stored as an item in the database, and an object in an S3 bucket
- Sending a duplicate POST request returns the appropriate response
- Sending a PUT request that targets an existing resource results in updates to the appropriate item in the database and object in the S3 bucket
- Sending a PUT request with no valid target returns the appropriate response
- Sending a DELETE request results in the appropriate item being removed from the database and object being removed from the S3 bucket
- Sending a DELETE request with no valid target returns the appropriate response
The Dockerfiles, shells, and docker compose ymls all lay the groundwork for properly executing the code using Localstack to run a mock of AWS as part of the application stack. In order to run the code locally you would clone the repo and then use ```pip install -r requirements.txt``` to install the dependencies and use ```chmod +x start_stack.sh``` and ```chmod +x test_script.sh``` to make the shell files executable. Once everything has been set up in that way you can execute the start_stack shell script (and can use the docker-compose ```docker-compose -f docker-compose.local.yml up -d``` to make sure it is correctly configured needs be. The testing can be run using docker compose with the docker-compose.test.yml file ```docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit``` and then once testing is complete the docker containers can be brought down using ```docker-compose -f docker-compose.test.yml down```. 
