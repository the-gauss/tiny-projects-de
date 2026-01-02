docker compose down -v
# v flag means to remove named volumes declared in the `volumes` section of the Compose file and anonymous volumes attached to containers.

sleep 5

cd airbyte

docker compose down