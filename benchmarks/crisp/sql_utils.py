# %%
import time
import numpy as np
import random
import string

letters = string.ascii_lowercase

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event

try:
    engine = create_engine('mysql://pierrefg:0000@localhost/testg3', echo=False)
    TABLE_NAME = ''.join(random.choice(letters) for i in range(10))
    JOIN_CHAR = ', '

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        ellapsed = time.time() - conn.info['query_start_time'].pop(-1)
        conn.info['last_query_time'] = ellapsed
    
    sql_available = True
except:
    sql_available = False

def generate_request(X,Y):
    X = [f"`{attr}`" for attr in X]
    Y = [f"`{attr}`" for attr in Y]
    return f'''
WITH v1 AS (
    WITH v0 AS (
        SELECT {JOIN_CHAR.join(X)}, COUNT(*) AS y_count
        FROM {TABLE_NAME}
        GROUP BY {JOIN_CHAR.join(X+Y)}
    )
    SELECT MAX(y_count) AS count_mf_element, SUM(y_count) AS ec_size
    FROM v0
    GROUP BY {JOIN_CHAR.join(X)}
)
SELECT 1-SUM(count_mf_element)/CAST(SUM(ec_size) AS float)
FROM v1;
'''

def g3_sql(df, X, Y):
    df.to_sql(TABLE_NAME, con=engine, if_exists='replace')
    request = generate_request(X,Y)
    res = engine.execute(request).fetchall()
    engine.execute(f'DROP TABLE {TABLE_NAME};')
    return res[0][0]
    

def g3_sql_bench(df, X, Y, n_repeats=1):
    df.to_sql(TABLE_NAME, con=engine, if_exists='replace')
    request = generate_request(X,Y)

    ellapsed_arr = []
    with engine.connect() as connection:
        for _ in range(n_repeats):
            connection.execute(request).fetchall()
            ellapsed_arr.append(connection.info["last_query_time"])
    engine.execute(f'DROP TABLE {TABLE_NAME};')
    return np.mean(ellapsed_arr)

# %%
