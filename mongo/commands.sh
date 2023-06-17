docker network create mongo-network

docker run -p 27017:27017 -d -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password --network mongo-network --name mongodb mongo

docker run -d -it --rm --network mongo-network --name mongo-express -p 8081:8081 -e ME_CONFIG_OPTIONS_EDITORTHEME="ambiance" -e ME_CONFIG_MONGODB_ENABLE_ADMIN=true -e ME_CONFIG_MONGODB_ADMINUSERNAME=admin -e ME_CONFIG_MONGODB_ADMINPASSWORD=password -e ME_CONFIG_MONGODB_SERVER=mongodb mongo-express

docker compose -f <filename> up

docker build --no-cache -t portfolio-app:latest .