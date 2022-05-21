ifeq ($(OS),Windows_NT)
    OPEN := powershell
else
    UNAME := $(shell uname -s)
    ifeq ($(UNAME),Linux)
        OPEN := xdg-open
    endif
endif
# Сообщение по умолчанию
default:
	@echo Commands:
	@echo build, doc, reqs, pep8
	@echo install, dev, remove
	@echo run
	@echo docker_: build, run, stop, term

# Список зависимостей
reqs:
	@python -m pip list --format=freeze > requirements.txt

# Сборка пакета
build: pep8
	@python setup.py sdist --formats=zip

# Генерация документации (windows)
doc: pep8
	@powershell rm .\docs\FTA.rst
	@sphinx-apidoc -o ./docs/ ./FTA/
	@sphinx-build -b html docs docs/_build/html
	@$(OPEN) ./docs/_build/html/index.html

# Установка
install: build
	@pip install dist/FTA-1.0.1.zip

# Установка в режиме разработчика
dev:
	@pip install -e .[dev]

# Удаление
remove:
	@pip uninstall FTA

# Форматирование кода
pep8:
	@pip install autopep8
	@python -m autopep8 --in-place --recursive ./FTA
	@python -m autopep8 --in-place setup.py

# Запуск
run: pep8
	@python -m FTA $(ARG)

# Создание Docker образа
docker_build: build
	@docker build -t fta_image .

# Запуск Docker
docker_run:
#	Требуется X Server
	@docker run --rm fta_image

# Остановка Docker
docker_stop:
	@docker stop linux

# Консоль Docker образа
docker_term:
	@docker run -it fta_image bash

# Тестирование (FTA.py::test_self_deny_response)
test:
	@python -m pytest -s ./FTA/tests/test_$(ARG)