# Conexion para evitar la conectividad directa con mysql
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # Si PyMySQL no está instalado, se asume que se está usando el conector nativo (mysqlclient).
    pass