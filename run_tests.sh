info "setting up environment"
docker compose up -d

info "running tests"
hatch run test

info "tearing down environment"
docker compose down -v