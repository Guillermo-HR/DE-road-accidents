# Makefile for road-accidents project

# Variable with the path to the setup script
SETUP_SCRIPT = ./code/scripts/configure_directories.sh
CLEAN_SCRIPT = ./code/scripts/clean_directories.sh

up: 
	@chmod +x $(SETUP_SCRIPT)
	@$(SETUP_SCRIPT)
	docker compose up -d --build

down:
	docker compose down

clean: down
	@chmod +x $(CLEAN_SCRIPT)
	@$(CLEAN_SCRIPT)