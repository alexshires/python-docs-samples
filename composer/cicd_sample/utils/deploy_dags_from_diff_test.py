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


import os
import pathlib
from shutil import copytree
import tempfile
import uuid
import git

from google.cloud import storage
import pytest

import deploy_dags_from_diff # noqa: I100 - lint is incorrectly saying this is out of order

# DAGS_DIR = "cicd_sample/dags"  # this needs to be relative to the REPO roo
DAGS_DIR = pathlib.Path(__file__).parent.parent / "dags/"
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
REPO_MAIN = "main"
TEST_DAG_FILENAME = "example2_dag.py"


def test_create_dags_list_with_changes() -> None:
    """
    this test checks for
    :return:
    """
    full_dag_dir_str = "cicd_sample/dags" # str(DAGS_DIR) # .resolve())
    full_repo_root_str = str(REPO_ROOT.resolve())
    print(full_dag_dir_str, full_repo_root_str)
    repo = git.Repo(REPO_ROOT)
    repo.create_head("test-branch")
    repo.git.checkout("test-branch")
    with open(f"{DAGS_DIR.resolve()}/{TEST_DAG_FILENAME}", 'a') as f:
        # create minor change
        f.write("# appended line\n")

    repo.git.commit("-am", "appended line to file")
    dag_list = deploy_dags_from_diff.create_dags_list_from_git_diff(
        full_dag_dir_str, full_repo_root_str, REPO_MAIN)
    print(dag_list)
    assert len(dag_list) > 0
    assert "example2_dag.py" in dag_list[0]
    # cleanup - uncomment once test dev is done
    # repo.git.checkout(REPO_MAIN)


def test_create_dags_list_no_changes() -> None:
    """
    this test checks for an empty list based on no changes in git
    :return:
    """
    dag_list = deploy_dags_from_diff.create_dags_list_from_git_diff(DAGS_DIR, REPO_ROOT, REPO_MAIN)
    assert len(dag_list) == 0

