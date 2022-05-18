# Базовый образ
FROM ubuntu:20.04

# Игнорирование настройки таймзоны
ARG DEBIAN_FRONTEND=noninteractive

# Python
RUN apt update
RUN apt install -y python3-pip \
    && cd /usr/bin \
    && ln -s python3 python

# Пакеты Python через apt (быстрая установка)
RUN apt install -y python3-pyqt5 python3-docopt \
python3-pyftpdlib python3-tabulate \
python3-psutil python3-netifaces

# Пользователь
RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

# fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

# Копирование папкок хоста в папки /mnt/*
ADD ./dist /mnt/package
ADD ./build/sphinx/html /mnt/doc

# Установка пакета
RUN cd /mnt/package && python -m pip install FTA-1.0.1.zip

# Дисплей и пользователь
ENV DISPLAY=host.docker.internal:0.0
USER qtuser
EXPOSE 2121

# Запуск
CMD ["python" , "-m" , "FTA"]