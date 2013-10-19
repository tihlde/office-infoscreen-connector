DROP TABLE stats;

CREATE TABLE stats (
    server_host VARCHAR(30) PRIMARY KEY,
    server_ping FLOAT,
    timestamp DATETIME,
    server_ipv4 VARCHAR(30),
    server_ipv6 VARCHAR(30),
    boot_time DATETIME
) 
