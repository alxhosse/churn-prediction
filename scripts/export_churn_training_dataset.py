import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:playground@localhost:5433/churn_prac"
)

df = pd.read_sql("select * from dbt_schema.churn_training_dataset", engine)

df.to_csv("outputs/churn_training_dataset.csv", index=False)

print(f"Saved {len(df)} rows to outputs/churn_training_dataset.csv")
