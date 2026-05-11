# churn-prac

## GitHub Actions — required secrets

Configure under **Settings → Secrets and variables → Actions** (and optional **Variables**).

### ML (ECR + SageMaker) — workflows `ml-cd-ecr.yml`, `ml-sagemaker-dispatch.yml`

| Secret | Description |
|--------|-------------|
| **`AWS_ROLE_ARN`** | IAM role ARN from Terraform output `github_actions_churn_role_arn` (OIDC; repo must be trusted, e.g. `alxhosse/churn-prac`). |
| **`SAGEMAKER_EXECUTION_ROLE_ARN`** | SageMaker execution role ARN from Terraform `sagemaker_churn_execution_role_arn`. |

Optional **Variables**: `AWS_REGION` (default `us-east-1`), `ML_INSTANCE_TYPE` (default `ml.m5.large`).

### dbt on Athena — workflow `dbt-cd.yml`

Same **`AWS_ROLE_ARN`** as above (needs Athena + Glue + S3 on your bucket prefixes).

| Secret | Description |
|--------|-------------|
| **`ATHENA_DATABASE`** | Usually `awsdatacatalog`. |
| **`ATHENA_SCHEMA`** | Glue / dbt build schema (e.g. `dbt_churn_ci`). |
| **`ATHENA_S3_STAGING_DIR`** | Athena query results `s3://.../` (see Terraform `churn_prac_athena_staging_s3_uri`). |
| **`ATHENA_S3_DATA_DIR`** | dbt CTAS warehouse `s3://.../` (see `churn_prac_dbt_athena_s3_data_uri`). |
| **`ATHENA_WORK_GROUP`** | e.g. `churn_prac`. |

### dbt CI — `dbt-ci.yml`

No cloud secrets: uses dummy Postgres env for **dbt parse** and SQLFluff only.

### SageMaker workflow notes

- **Training** expects `train.csv`, `valid.csv`, `feature_columns.json` under the **`training`** channel prefix (see `churn_ml.train` defaults under `/opt/ml/input/data/training/`).
- **Preprocess** mounts marts as `churn_training_dataset.csv` and `current_customer_dataset.csv` under the input prefixes (CSV or layout compatible with `churn_ml.preprocess`).
- **Infer** expects `current.csv` under the current-features prefix and `xgboost_churn_model.joblib` + `feature_columns.json` under the model prefix (aligned with preprocess output + training).

Apply **`aws-terraform-infra`** so `churn_github_actions_repository_extra` includes **`alxhosse/churn-prac`** before OIDC from this repo will succeed.
