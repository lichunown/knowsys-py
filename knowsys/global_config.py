import os


configs = {
    'SQL_ENV': os.environ.get('SQL_ENV', 'test'),
    'KNOWSYS_LOAD_FROM_SQL': bool(int(os.environ.get('KNOWSYS_LOAD_FROM_SQL', '0'))),
}
