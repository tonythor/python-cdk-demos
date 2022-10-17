from pg_wrapper import PGWrapper
from secrets_wrapper import SecretsWrapper
import os
import json
from pathlib import Path

secret = os.environ["DB_SECRET_LOCATION"]

def handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    secret_dict = SecretsWrapper(account=aws_account_id).get_rds_secret(secret=secret)
    pg = PGWrapper(secret=secret_dict)
    
    # insert the titanic dataset into the database.
    # will go into dbname = username, table_name=titanic_data
    query = Path('./sql/titanic.sql').read_text()
    return_val = pg.raw_sql(query)
    
    # After you get this database ran, you should be able to use the 
    # lambda code editor and run query like this. (comment out the insert above)

    # query = "select * from titanic_data limit 5"
    # data = pg.get_results_as_pandas(query)
    # parsed = json.loads(data.to_json(orient="index"))
    # return_val = json.dumps(parsed) 
   
    pg.disconnect() 
    
    return(return_val)  

