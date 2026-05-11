import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:playground@localhost:5433/churn_prac"
)

df = pd.read_sql("select * from dbt_schema.current_customer_dataset", engine)

df.to_csv("outputs/current_customer_dataset.csv", index=False)
