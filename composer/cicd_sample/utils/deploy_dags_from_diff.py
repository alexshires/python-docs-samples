# Copyright 2023 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START composer_cicd_deploy_dags_from_diff_utility]

import argparse
import glob
import os
import git
from pathlib import Path
from shutil import copytree, ignore_patterns
import tempfile
from typing import List, Tuple

# Imports the Google Cloud client library
from google.cloud import storage


def create_dags_list_from_git_diff(dag_dir: str, repo_root: str, main_branch_name: str) -> Tuple[str, List[Path]]:
    """
    get the list of files within the DAG dir that have changed in the latest git commits against the specified branch
    :param dag_dir:
    :param repo_root:
    :param main_branch_name:
    :return:
    """
    repo = git.Repo(repo_root)
    diff_results = repo.git.diff(main_branch_name)
    p = Path(repo_root)
    changed_file_list = list()
    for diff_result_line in diff_results.split("\n"):
        # test if changed
        if "+++ b" in diff_result_line and dag_dir in diff_result_line:
            changed_path = p / Path(diff_result_line[6:])
            changed_file_list.append(changed_path)
            # print(changed_path.resolve())
    return dag_dir, changed_file_list


def upload_changed_dags_to_composer(dag_list: List[Path], bucket_name: str) -> None:
    """
    list of DAGs to upload to Commposer
    :param dag_list:
    :return:
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for dag_path in dag_list:
        blob = bucket.blob(dag_path.name)
        blob.upload_from_filename(str(dag_path))
        print(f"File {dag_path.name} uploaded to {bucket_name}/{dag_path.name}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dags_directory",
        help="Relative path to the source directory containing your DAGs",
    )
    parser.add_argument(
        "--dags_bucket",
        help="Name of the DAGs bucket of your Composer environment without the gs:// prefix",
    )
    parser.add_argument(
        "--dag_repo",
        required=False,
        help="Relative path to the root of the git repo containing the DAGs",
    )
    parser.add_argument(
        "--repo_main",
        required=False,
        help="Main branch of the DAG git repo to compare changes against",
    )

    args = parser.parse_args()

    dag_list = create_dags_list_from_git_diff(args.dags_directory, args.repo_root, args.repo_main)

    if len(dag_list)==0:
        print("No DAGs to upload")
    else:
        upload_changed_dags_to_composer(dag_list=dag_list, bucket_name=args.dags_bucket)
# [END composer_cicd_deploy_dags_from_diff_utility]