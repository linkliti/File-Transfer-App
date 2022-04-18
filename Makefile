# Сообщение по умолчанию
default:
	@echo Commands:
	@echo build, doc, reqs, venv, pep8
	@echo install, dev, remove
	@echo run
	@echo docker_: build, run, stop, term

# Список зависимостей
reqs: remove venv
	@python -m pip list --format=freeze > requirements.txt

# Сборка пакета
build: pep8
	@python setup.py sdist --formats=zip

# Генерация документации
doc:
	@python setup.py build_sphinx

# Установка
install: build
	@pip install dist\FTA-1.0.0.zip

# Установка в режиме разработчика
dev: pep8
	@pip install -e .

# Удаление
remove:
	@pip uninstall FTA

# Настройка среды Python для разработки
venv:
	@pip install --upgrade setuptools autopep8 sphinx pyside6 docopt

# Форматирование кода
pep8:
	@python -m autopep8 --in-place --recursive ./FTA
	@python -m autopep8 --in-place setup.py

# Запуск
run: pep8
	@python -m FTA

# Создание Docker образа
docker_build: build doc
	@docker build -t fta_image .

# Запуск Docker
docker_run:
#	@echo Docs: http://localhost:8099
	@docker run -e DISPLAY=unix$DISPLAY -d --rm -p8099:80 fta_image

# Остановка Docker
docker_stop:
	@docker stop linux

# Консоль Docker образа
docker_term:
	@docker run -it fta_image bash