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

Runs on **push to `main`** or **pull request** when **`dbt_churn/**`** changes, and on **`workflow_dispatch`**. Same **`AWS_ROLE_ARN`** as above (needs Athena + Glue + S3 on your bucket prefixes).

| Secret | Description |
|--------|-------------|
| **`ATHENA_DATABASE`** | Usually `awsdatacatalog`. |
| **`ATHENA_SCHEMA`** | Glue / dbt build schema (e.g. `dbt_churn_ci`). |
| **`ATHENA_S3_STAGING_DIR`** | Athena query results `s3://.../` (see Terraform `churn_prac_athena_staging_s3_uri`). |
| **`ATHENA_S3_DATA_DIR`** | dbt CTAS warehouse `s3://.../` (see `churn_prac_dbt_athena_s3_data_uri`). |
| **`ATHENA_WORK_GROUP`** | e.g. `churn_prac`. |
| **`ATHENA_ML_EXPORT_CHURN_TRAINING_PREFIX`** | `s3://…/` prefix for **`churn_training_dataset`** Parquet CTAS (must exist; e.g. fight_churn bucket `ml/exports/train/…/`). |
| **`ATHENA_ML_EXPORT_CURRENT_CUSTOMER_PREFIX`** | `s3://…/` prefix for **`current_customer_dataset`** Parquet CTAS (e.g. `ml/exports/infer/…/`). |

If these two are missing from the workflow **`env`**, dbt falls back to placeholder `s3://must-set-…/` and Athena returns **`NoSuchBucket`**.

### dbt CI — `dbt-ci.yml`

No cloud secrets: uses dummy Postgres env for **dbt parse** and SQLFluff only.

### SageMaker workflow notes

- **Training** expects `train.csv`, `valid.csv`, `feature_columns.json` under the **`training`** channel prefix (see `churn_ml.train` defaults under `/opt/ml/input/data/training/`).
- **Preprocess** mounts marts as `churn_training_dataset.csv` and `current_customer_dataset.csv` under the input prefixes (CSV or layout compatible with `churn_ml.preprocess`).
- **Infer** expects `current.csv` under the current-features prefix and `xgboost_churn_model.joblib` + `feature_columns.json` under the model prefix (aligned with preprocess output + training).

Apply **`aws-terraform-infra`** so `churn_github_actions_repository_extra` includes **`alxhosse/churn-prac`** before OIDC from this repo will succeed.
