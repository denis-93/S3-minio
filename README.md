#S3Project

###Задача

Создать простой API интерфейс S3 или Swift для базовых операций с файлами на Django:
* Download
* Upload
* List files
* Необходимо подключить в докере OpenStack Swift или же S3 (например Minio)
### Инструкция по запуску
1. Склонировать репозиторий
2. Запустить проект с используя конфигурационный файл docker-compose
3. Перейти в админку Minio. По умолчанию http://localhost:9000, логин: admin, пароль: password
4. Создать корзину testbucket
5. Работать с API. Краткая документация http://localhost:8000/api/swagger


