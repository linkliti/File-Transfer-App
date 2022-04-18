# Базовый образ
FROM ubuntu:latest

# Python
RUN apt update
RUN apt install -y python3 python3-pip \
    && cd /usr/bin \
    && ln -s python3 python

# Пакеты Python через apt (быстрая установка)

RUN apt install python3-docopt

# Копирование папкок хоста в папки /mnt/*
ADD ./dist /mnt/package
ADD ./build/sphinx/html /mnt/doc

# Установка пакета
RUN cd /mnt/package && python -m pip install FTA-1.0.0.zip

# Дисплей
ENV DISPLAY=host.docker.internal:0.0

# Запуск
CMD ["python" , "-m" , "FTA", "-t", "text"]
# Порт
#EXPOSE 80
#CMD ["python" , "-m" , "http.server", "-d", "/mnt/doc", "80"]