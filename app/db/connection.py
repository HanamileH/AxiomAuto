import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self):
        self.connection_pool = None

    
    def init_app(self, app):
        """Инициализация пула соединений
        Args:
            app (Flask): Flask-приложение
        """

        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            user=app.config['DB_USERNAME'],
            password=app.config['DB_PASSWORD'],
            host=app.config['DB_HOSTNAME'],
            port=app.config['DB_PORT'],
            database=app.config['DB_DATABASE']
        )


    def init_db(self):
        """Инициализация базы данных
        """

        with self.get_cursor(commit=True) as cursor:
            # Инициализируем схему бд
            with open("./app/sql/init_schema.sql", 'r') as file:
                cursor.execute(file.read())

            # Если таблицы пустые, заполняем тестовыми данными
            cursor.execute("SELECT COUNT(*) FROM model")
            count = cursor.fetchone()[0]

            if count == 0:
                with open("./app/sql/fill_tables.sql", 'r') as file:
                    cursor.execute(file.read())


    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для получения соединения из пула
        """
        connection = self.connection_pool.getconn()
        try:
            yield connection
        finally:
            self.connection_pool.putconn(connection)


    @contextmanager
    def get_cursor(self, commit=False, as_dict=False):
        """Контекстный менеджер для получения курсора
        Args:
            commit (bool, optional): флаг для коммита транзакции. По умолчанию False.
            as_dict (bool, optional): флаг для получения данных курсора в виде словаря. По умолчанию False.
        """
        connection = self.connection_pool.getconn()
        try:
            if as_dict:
                cursor = connection.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = connection.cursor()

            yield cursor
            if commit:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()


# Глобальный экземпляр базы данных
db = DatabaseConnection()