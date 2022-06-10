docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp/codalab:/tmp/codalab \
    -d \
    --name compute_worker \
    --env-file .env \
    --restart unless-stopped \
    --log-opt max-size=50m \
    --log-opt max-file=3 \
    codalab/competitions-v1-compute-worker:docker
