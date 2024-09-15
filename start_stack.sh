#!/bin/bash

# Start the Docker Compose stack in detached mode
docker-compose up -d

# Wait for user input to stop the stack
echo "Stack is running. Press [CTRL+C] to stop."

# Wait for the user to stop the services
trap 'docker-compose down' SIGINT
wait

chmod +x start_stack.sh
