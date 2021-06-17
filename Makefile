IMAGE := zendesk-bot

build:
	@echo "Building image"
	@docker build -t ${IMAGE} .

run:
	@echo "Run the zendesk bot..."
	@docker-compose run app

# Dev-related
lint:
	@echo "Linting the repo..."
	@black zendesk/

test:
	@echo "Testing the repo..."
	@pytest -W ignore -vv

pylint:
	@echo "Running pylint..."
	@pylint zendesk/ --disable=C --disable=W1203 --disable=W1202 --reports=y

radon:
	@echo "Run Radon to compute complexity..."
	@radon cc . --total-average -nb

xenon:
	@echo "Running Xenon..."
	@xenon --max-absolute B --max-modules A --max-average A .