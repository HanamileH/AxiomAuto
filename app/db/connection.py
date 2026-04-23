from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import datetime as _dt
import json as _json
import os as _os
import re as _re
import threading as _threading
import time as _time


_DB_LOG_WRITE_LOCK = _threading.Lock()


def _project_root_dir():
    return _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))


def _db_log_dir():
    try:
        from flask import current_app

        configured = current_app.config.get("DB_QUERY_LOG_DIR")
        if configured:
            return _os.path.abspath(configured)
    except Exception:
        pass

    return _os.path.join(_project_root_dir(), "logs", "db")


def _now_iso():
    return _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat()


def _today_date_str():
    return _dt.datetime.now(_dt.timezone.utc).astimezone().date().isoformat()


def _json_safe(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return value.decode("utf-8", errors="replace")
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        try:
            return value.isoformat()
        except Exception:
            return str(value)

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    return str(value)


def _get_request_actor():
    ip = ""
    account_id = ""
    role = ""

    try:
        from flask import g, has_request_context, request
    except Exception:
        return {"ip": ip, "account_id": account_id, "role": role}

    if has_request_context():
        ip = (
            getattr(g, "ip", None)
            or getattr(g, "client_ip", None)
            or getattr(g, "remote_addr", None)
            or ""
        )

        if not ip:
            xff = request.headers.get("X-Forwarded-For", "")
            if xff:
                ip = xff.split(",")[0].strip()
            else:
                ip = request.remote_addr or ""

        try:
            from flask_login import current_user

            if current_user is not None and getattr(current_user, "is_authenticated", False):
                account_id = str(getattr(current_user, "id", "") or "")
                role = str(getattr(current_user, "role", "") or "")
        except Exception:
            pass

    return {"ip": ip, "account_id": account_id, "role": role}


_SQL_LEADING_COMMENTS_RE = _re.compile(r"^\s*(?:--[^\n]*\n|\s|/\*.*?\*/\s*)*", _re.S)
_SQL_USERS_TABLE_RE = _re.compile(r"\busers\b", _re.I)
_SQL_OPERATION_RE = _re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|TRUNCATE|CREATE|ALTER|DROP|SET|CALL|DO|GRANT|REVOKE)\b",
    _re.I,
)


def _normalize_sql_text(query, cursor=None):
    if query is None:
        return ""

    try:
        if hasattr(query, "as_string") and cursor is not None:
            return query.as_string(cursor.connection)
    except Exception:
        pass

    try:
        return str(query)
    except Exception:
        return ""


def _sql_operation(sql_text):
    sql_text = (sql_text or "").strip()
    if not sql_text:
        return ""

    sql_text = _SQL_LEADING_COMMENTS_RE.sub("", sql_text).lstrip()
    if not sql_text:
        return ""

    if sql_text[:4].upper() == "WITH":
        # For CTE queries, the first keyword inside the CTE may be SELECT even if
        # the main statement is UPDATE/INSERT/DELETE. Prefer non-SELECT ops.
        for op in (
            "INSERT",
            "UPDATE",
            "DELETE",
            "TRUNCATE",
            "CREATE",
            "ALTER",
            "DROP",
            "GRANT",
            "REVOKE",
            "SET",
            "CALL",
            "DO",
            "SELECT",
        ):
            if _re.search(rf"\\b{op}\\b", sql_text, _re.I):
                return op
        return "WITH"

    return (sql_text.split(None, 1)[0] or "").upper()


def _sql_kind(operation):
    op = (operation or "").upper()
    if op == "INSERT":
        return "insert"
    if op == "UPDATE":
        return "update"
    if op == "DELETE":
        return "delete"
    if op == "TRUNCATE":
        return "truncate"
    if op in {"CREATE", "ALTER", "DROP"}:
        return "ddl"
    if op in {"GRANT", "REVOKE"}:
        return "acl"
    return "other"


def _should_hide_params(sql_text, hide_params_default):
    if hide_params_default:
        return True
    if _SQL_USERS_TABLE_RE.search(sql_text or ""):
        return True
    return False


def _write_db_log(entry):
    try:
        log_dir = _db_log_dir()
        _os.makedirs(log_dir, exist_ok=True)
        log_path = _os.path.join(log_dir, f"{_today_date_str()}.jsonl")
        line = _json.dumps(
            entry,
            ensure_ascii=False,
            separators=(",", ":"),
            default=_json_safe,
        )
        with _DB_LOG_WRITE_LOCK:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
                f.write("\n")
    except Exception:
        return


class LoggedCursor:
    def __init__(self, cursor, hide_params=False):
        self._cursor = cursor
        self._hide_params_default = bool(hide_params)

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def execute(self, query, vars=None):
        sql_text = _normalize_sql_text(query, cursor=self._cursor)
        operation = _sql_operation(sql_text)

        started = _time.perf_counter()
        try:
            result = self._cursor.execute(query, vars)
            status = getattr(self._cursor, "statusmessage", "") or ""
            if status:
                operation = status.split(None, 1)[0].upper()
            ok = True
            err = ""
            return result
        except Exception as exc:
            ok = False
            err = str(exc)
            raise
        finally:
            duration_ms = int((_time.perf_counter() - started) * 1000)

            if operation != "SELECT":
                hide_params = _should_hide_params(sql_text, self._hide_params_default)
                actor = _get_request_actor()

                entry = {
                    "ts": _now_iso(),
                    "ip": actor["ip"],
                    "account_id": actor["account_id"],
                    "role": actor["role"],
                    "operation": operation,
                    "kind": _sql_kind(operation),
                    "duration_ms": duration_ms,
                    "success": ok,
                    "error": err,
                    "sql": sql_text,
                    "params_hidden": hide_params,
                    "params": None if hide_params else _json_safe(vars),
                    "rowcount": getattr(self._cursor, "rowcount", None),
                }
                _write_db_log(entry)

    def executemany(self, query, vars_list):
        sql_text = _normalize_sql_text(query, cursor=self._cursor)
        operation = _sql_operation(sql_text)

        started = _time.perf_counter()
        try:
            result = self._cursor.executemany(query, vars_list)
            status = getattr(self._cursor, "statusmessage", "") or ""
            if status:
                operation = status.split(None, 1)[0].upper()
            ok = True
            err = ""
            return result
        except Exception as exc:
            ok = False
            err = str(exc)
            raise
        finally:
            duration_ms = int((_time.perf_counter() - started) * 1000)

            if operation != "SELECT":
                hide_params = _should_hide_params(sql_text, self._hide_params_default)
                actor = _get_request_actor()

                entry = {
                    "ts": _now_iso(),
                    "ip": actor["ip"],
                    "account_id": actor["account_id"],
                    "role": actor["role"],
                    "operation": operation,
                    "kind": _sql_kind(operation),
                    "duration_ms": duration_ms,
                    "success": ok,
                    "error": err,
                    "sql": sql_text,
                    "params_hidden": hide_params,
                    "params": None if hide_params else _json_safe(vars_list),
                    "rowcount": getattr(self._cursor, "rowcount", None),
                }
                _write_db_log(entry)


class DatabaseConnection:
    def __init__(self):
        self.connection_pool = None

    def init_app(self, app):
        """Инициализация пула соединений
        Args:
            app (Flask): Flask-приложение
        """

        self.connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            user=app.config["DB_USERNAME"],
            password=app.config["DB_PASSWORD"],
            host=app.config["DB_HOSTNAME"],
            port=app.config["DB_PORT"],
            database=app.config["DB_DATABASE"],
        )

        # Переключаемся на нужную схему
        with self.get_cursor(commit=True) as cursor:
            cursor.execute(f"SET search_path TO {app.config['DB_SCHEMA']}")

    def init_db(self):
        """Инициализация базы данных"""

        pass

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для получения соединения из пула"""
        connection = self.connection_pool.getconn()
        try:
            yield connection
        finally:
            self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, commit=False, as_dict=False, hide_params=False):
        """Контекстный менеджер для получения курсора
        Args:
            commit (bool, optional): флаг для коммита транзакции. По умолчанию False.
            as_dict (bool, optional): флаг для получения данных курсора в виде словаря. По умолчанию False.
            hide_params (bool, optional): флаг для скрытия параметров в логах. По умолчанию False.
        """
        # Используем существующий метод get_connection для управления пулом
        with self.get_connection() as connection:
            cursor = None
            try:
                if as_dict:
                    cursor = LoggedCursor(
                        connection.cursor(cursor_factory=RealDictCursor),
                        hide_params=hide_params,
                    )
                else:
                    cursor = LoggedCursor(connection.cursor(), hide_params=hide_params)

                yield cursor
                if commit:
                    connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                if cursor is not None:
                    cursor.close()


# Глобальный экземпляр базы данных
db = DatabaseConnection()
