import pymysql, os

if 'RDS_HOSTNAME' in os.environ:
    pymysql.install_as_MySQLdb()