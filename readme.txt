To create the db within your command line do the following:

NOTE: #s are second time
Also, this is being installed on your system rather than just in your project folder

brew install mysql
#brew reinstall mysql
brew link --force mysql
#brew unlink mysql && brew link mysql
brew install mysql-client
#brew reinstall mysql-client
LDFLAGS=-L/usr/local/opt/openssl/lib pip3 install flask-mysqldb

Then install the following packages for this project:

pip3 install flask -mysqldb

pip3 install flask-wtf

pip3 install passlib

[MAYBE NOT REQUIRED] pip3 install cryptography

To start sql in terminal:

mysql -uroot
exit ==> to exit form sql in terminal

Some commands i used to create users table:

SHOW DATABASES;
CREATE DATABASE mytestapp;
USE mytestapp;
CREATE TABLE users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100), register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
SHOW TABLES;
DESCRIBE users;

Some commands i used to create articles table:


create table articles (id INT(11) auto_increment primary key, title varchar(255), author varchar(100), body text, create_date timestamp default current_timestamp);

show tables;

You can do select * from <tablename> to see the data

