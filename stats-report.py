#!/usr/bin/python
# Reports back to TIHLDE stats server database
# with information about the server
import MySQLdb
import socket
import ping
import logging
from datetime import datetime

# Making log available for all methods
logger = logging.getLogger('update-stats')
hostname = socket.gethostname()
current_time = datetime.now()
ipv4 = socket.gethostbyname(socket.gethostname())
# Returns ping in seconds * 1000 for ms
ping = ping.do_one('www.google.com', 2000, 64) * 1000


# Making connection to database
def dbConnector(credentials):
    try:
        database = MySQLdb.connect(
            host=credentials[0],
            user=credentials[1],
            passwd=credentials[2],
            db=credentials[3])
        return database
    except MySQLdb.Error, e:
        logger.error(e)


# Database cleanup
def dbCleanUp(database):
    try:
        database.close()
    except MySQLdb.Error, e:
        logger.error(e)


# Add new table with server. Only runs the first script runs on a new server.
def firstAdd(cur):
    cur.execute("""
        INSERT INTO stats(server_host, timestamp, server_ipv4, server_ping)
        VALUES(%s, %s, %s, %s)
        """, (hostname, current_time, ipv4, ping))


# Update fields in database
def update(database):
    cur = database.cursor()
    cur.execute("""
        UPDATE stats SET timestamp = %s, server_ping = %.5s, server_ipv4 = %s
        WHERE server_host = %s
        """, (current_time, ping, ipv4, hostname))
    cur.close()


# Check if server allready exist in database
def checkExist(database):
    cur = database.cursor()
    stmt = "SELECT COUNT(1) FROM stats WHERE server_host = '%s'" % (hostname)
    try:
        cur.execute(stmt)

        if cur.fetchone()[0] > 0:
            return True
            cur.close()
        else:
            return False
            cur.close()
    except MySQLdb.Error, e:
        logger.error(e)


# Load password file
def loadPassword(filename):
    passwd_file = open(filename, "r")
    credentials = []
    for line in passwd_file:
        if not line.startswith("#"):
            credentials.append(line.rstrip())
    passwd_file.close()
    return credentials


# Set logger
def setLogger():
    log_handler = logging.FileHandler('/var/log/update-stats.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.WARNING)


# Main method
def main():
    setLogger()
    database = dbConnector(loadPassword("stats-mysql.pw"))
    if not checkExist(database):
        firstAdd(database)
    else:
        update(database)

    try:
        database.commit()
        dbCleanUp(database)
    except MySQLdb.Error, e:
        logger.error(e)


# Check if script is running as module or main
if __name__ == "__main__":
    main()
