"""Render churn-prac Athena + dbt + SageMaker flow (diagrams)."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import Athena, GlueDataCatalog
from diagrams.aws.ml import Sagemaker
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.onprem.analytics import Dbt
from diagrams.onprem.ci import GithubActions


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def render(*, outfile_base: Path, direction: str) -> Path:
    base = outfile_base
    if base.suffix.lower() == ".png":
        base = base.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)

    stem = base.relative_to(_repo_root()).as_posix()

    graph_attrs = {
        "size": "16,10",
        "dpi": "300",
        "pad": "0.3",
        "nodesep": "0.9",
        "ranksep": "1.2",
        "splines": "ortho",
        "compound": "true",
        "newrank": "true",
        "concentrate": "false",
        "fontname": "Sans-Serif",
    }

    node_attrs = {
        "fontsize": "12",
        "fontname": "Sans-Serif",
    }

    edge_attrs = {
        "fontsize": "11",
        "fontname": "Sans-Serif",
        "penwidth": "1.2",
    }

    chain_e = {
        "fontsize": "10",
        "fontname": "Sans-Serif",
        "minlen": "2",
        "penwidth": "1.2",
    }

    with Diagram(
        name="Architecture Diagram",
        filename=stem,
        show=False,
        direction=direction,
        graph_attr=graph_attrs,
        node_attr=node_attrs,
        edge_attr=edge_attrs,
    ):
        cicd = GithubActions("GitHub Actions")
        dbt_p = Dbt("dbt_churn")

        with Cluster("AWS"):
            catalog = GlueDataCatalog("Glue Catalog")
            athena = Athena("Athena")
            s3_ml = SimpleStorageServiceS3("ML Parquet")

            sm_pre = Sagemaker("Preprocessing")
            sm_train = Sagemaker("Training")
            sm_infer = Sagemaker("Inference")

        cicd >> Edge(label="OIDC") >> dbt_p
        dbt_p >> Edge(label="dbt Athena") >> athena
        catalog >> Edge(style="dashed", label="Metadata") >> athena

        athena >> Edge(label="CTAS Marts", **chain_e) >> s3_ml
        s3_ml >> Edge(label="Datasets", **chain_e) >> sm_pre
        sm_pre >> Edge(label="Train/Valid/Current", **chain_e) >> sm_train
        sm_train >> Edge(label="Model Artifacts", **chain_e) >> sm_infer

    return base.with_suffix(".png")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Athena / dbt / SageMaker diagram.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_repo_root() / "diagrams" / "athena_dbt_churn_ci",
        help="Output path without extension",
    )

    parser.add_argument(
        "--direction",
        choices=("TB", "LR"),
        default="LR",
        help="LR = horizontal, TB = vertical",
    )

    args = parser.parse_args()

    root = _repo_root()
    out = args.output if args.output.is_absolute() else (root / args.output).resolve()

    prev = Path.cwd()
    try:
        os.chdir(root)
        png = render(outfile_base=out, direction=args.direction)
    finally:
        os.chdir(prev)

    print(f"Wrote {png}")


if __name__ == "__main__":
    main()