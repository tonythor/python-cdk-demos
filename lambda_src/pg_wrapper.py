import psycopg2
import logging
import pandas as pd

class PGWrapper:
    """ A postgres wrapper that takes in a SecretValue dictionary from secrets manager.
    You can use it like a psycopg2 connection, but it has built in support for returning
    a pandas dataframe with the result set. 
    """
    
    connection: psycopg2._psycopg.connection = None
    cursor:psycopg2._psycopg.cursor = None
    
    def __init__(self, secret: dict, **kwargs):
        self.secret = secret
        try:
            _connection = psycopg2.connect(
                user=secret.get('username'),
                password=secret.get('password'),
                database=secret.get('database'), 
                host=secret.get('host'),
                port=secret.get('port'),     
                **kwargs)
            self.connection = _connection
            self.cursor = _connection.cursor()
        except ConnectionError:
            logging.error("could not connect postgres database")

    def disconnect(self):
        self.connection.close()
        pass

    def raw_sql(self, query:str, **kwargs) -> str:
        result = ""
        result += (f'starting execution of: {query[0:150]}...\n')
        self.cursor.execute(query) 
        self.connection.commit()   
        result += ('\n Raw SQL Query Complete')
        return result

    def get_results_as_list(self, query: str, **kwargs) -> list:
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_results_as_pandas(self, query: str, **kwargs) -> pd.DataFrame:
        # parsed = json.loads(query_results.to_json(orient="index"))
        # this is in json, return(json.dumps(parsed))  
        return pd.read_sql(query, con=self.connection, **kwargs)

