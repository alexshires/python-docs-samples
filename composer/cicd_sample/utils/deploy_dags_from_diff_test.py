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

DAGS_DIR = pathlib.Path(__file__).parent.parent / "dags/"
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
REPO_MAIN = "main"


def test_create_dags_list_with_changes() -> None:
    """
    this test checks for
    :return:
    """
    repo = git.Repo(REPO_ROOT)

    with open(DAGS_DIR+"/example2_dag.py", 'w') as f:
        # create minor

    dag_list = deploy_dags_from_diff.create_dags_list_from_git_diff(DAGS_DIR, REPO_ROOT, REPO_MAIN)
    assert len(dag_list) > 0
    assert




def test_create_dags_list_no_changes() -> None:
    """
    this test checks for an empty list based on no changes in git
    :return:
    """
    dag_list = deploy_dags_from_diff.create_dags_list_from_git_diff(DAGS_DIR, REPO_ROOT, REPO_MAIN)
    assert len(dag_list) == 0

