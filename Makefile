sync: deps up-d ## обновляем зависимости в .venv

deps: ## ставим зависимости (не мог достучаться до pypi.org)
	.venv/bin/python -m pip install --default-timeout=100 -i https://pypi.tuna.tsinghua.edu.cn/simple -e ./api

build: ## сборка образов
	docker compose build

up: ##
	docker compose up --build

up-d: ##
	docker compose up -d --build

down:
	docker compose down

stop:
	docker compose stop

restart:
	docker compose restart

ps:
	docker compose ps

exec:
	docker compose run --rm --no-deps api sh

pull:
	docker compose pull

