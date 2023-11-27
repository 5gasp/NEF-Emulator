SHELL := /bin/bash

# Function to determine Docker Compose command
define docker_compose_cmd
	$(if $(shell command -v docker-compose 2> /dev/null),docker-compose,$(if $(shell command -v docker compose 2> /dev/null),docker compose,))
endef


# Prepare DEVELOPMENT environment

prepare-dev-env:
	cp env-file-for-local.dev .env


# docker-compose TASKS

up:
	$(call docker_compose_cmd) --profile dev up

upd:
	docker compose --profile dev up -d

debug-up:
	$(call docker_compose_cmd) --profile debug up

debug-upd:
	$(call docker_compose_cmd) --profile debug up -d

down:
	$(call docker_compose_cmd) --profile dev down

down-v: # also removes volumes
	$(call docker_compose_cmd) --profile dev down -v

stop:
	$(call docker_compose_cmd) stop

build:
	$(call docker_compose_cmd) --profile debug build

build-no-cache:
	$(call docker_compose_cmd) --profile debug build --no-cache

logs:
	$(call docker_compose_cmd) logs -f

logs-backend:
	$(call docker_compose_cmd) logs -f backend

logs-mongo:
	$(call docker_compose_cmd) logs -f mongo

ps:
	docker ps -a



# COMBOS

upl: upd logs



# DATABASE

db-init: #simple scenario with 3 UEs, 3 Cells, 1 gNB
	./backend/app/app/db/init_simple.sh


db-reset:
	$(call docker_compose_cmd) exec db psql -h localhost -U postgres -d app -c 'TRUNCATE TABLE cell, gnb, monitoring, path, points, ue RESTART IDENTITY;'
	$(call docker_compose_cmd) exec mongo /bin/bash -c 'mongo fastapi -u $$MONGO_USER -p $$MONGO_PASSWORD --authenticationDatabase admin --eval "db.dropDatabase();"'


db-reinit: db-reset db-init


#Individual logs

logs-location:
	$(call docker_compose_cmd) logs -f backend 2>&1 | grep -E "(handovers|monitoringType|'ack')"
