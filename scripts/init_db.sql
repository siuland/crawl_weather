ALTER USER 'weather_user'@'%' IDENTIFIED WITH mysql_native_password BY 'Weather@123';
GRANT ALL PRIVILEGES ON weather_db.* TO 'weather_user'@'%';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    date VARCHAR(20) NOT NULL,
    weather VARCHAR(50) NOT NULL,
    temp VARCHAR(20) NOT NULL,
    high_temp INT,
    low_temp INT,
    crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);