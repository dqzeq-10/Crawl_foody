FROM mysql:8.0

# Set MySQL configuration
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=db_crawl
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=password

# Copy initialization SQL script
COPY ./init_db/init.sql /docker-entrypoint-initdb.d/

# Set character set and collation defaults
# Use ENTRYPOINT instead of overriding CMD
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]
