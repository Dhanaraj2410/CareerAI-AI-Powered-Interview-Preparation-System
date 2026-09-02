# CareerAI Django Package Initialization
# Configures PyMySQL driver for MySQL connection compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
