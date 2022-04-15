# Базовый образ
FROM ubuntu:20.04
# Команда
RUN apt update \
    && apt install -y python3 git \
    && cd /usr/bin \
    && ln -s python3 python
# Копирование папки хоста в папку /mnt/files
ADD ./dist /mnt/package
# Установка пакета
RUN cd /mnt/files \
    && pip install /mnt/files \
    && python -m pip install FTA-1.0.0.tar.gz
# Запуск
CMD ["python" , "-m" , "FTA"]
