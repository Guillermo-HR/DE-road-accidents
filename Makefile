# Makefile for road-accidents project

# Variable with the path to the setup script
SETUP_SCRIPT = ./code/scripts/setup_directories.sh
CLEAN_SCRIPT = ./code/scripts/clean_directories.sh

# Default command if you just type 'make'
all: up

# Task to create directories
dirs:
	@chmod +x $(SETUP_SCRIPT)
	@$(SETUP_SCRIPT)

# Task to bring up the project (depends on 'dirs')
up: dirs
	docker compose up -d

# Task to bring down the project
down:
	docker compose down

# Task to clean directories
clean: down
	@chmod +x $(CLEAN_SCRIPT)
	@$(CLEAN_SCRIPT)