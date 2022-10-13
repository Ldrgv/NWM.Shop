# Описание

Телеграм бот, разработанный для сообщества New Wave Muslim.

# Установка

## PostgreSQL

	# Установка PostgreSQL
	sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
	sudo apt-get update
	sudo apt-get -y install postgresql
	
	# Создание юзера postgres
	sudo -i -u postgres
	
	# Создание базы данных
	postgres@server:~$ createdb <имя вашей базы данных>
	
	# Установка пароля
	postgres@server:~$ psql
	postgres=# \password

## Redis

	sudo apt update
	sudo apt install redis-server
