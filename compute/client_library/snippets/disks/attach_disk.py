#  Copyright 2023 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# flake8: noqa


# This file is automatically generated. Please do not modify it directly.
# Find the relevant recipe file in the samples/recipes or samples/ingredients
# directory and apply your changes there.


# [START compute_regional_disk_attach]
# [START compute_disk_attach]
import sys
from typing import Any, Literal

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    """
    This method will wait for the extended (long-running) operation to
    complete. If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
    result = operation.result(timeout=timeout)

    if operation.error_code:
        print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr,
            flush=True,
        )
        print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True)

    return result


def attach_disk(
    project_id: str,
    zone: str,
    instance_name: str,
    disk_link: str,
    mode: Literal["READ_ONLY", "READ_WRITE"],
) -> None:
    """
    Attaches a non-boot persistent disk to a specified compute instance. The disk might be zonal or regional.

    You need following permissions to execute this action:
    https://cloud.google.com/compute/docs/disks/regional-persistent-disk#expandable-1

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone:name of the zone in which the instance you want to use resides.
        instance_name: name of the compute instance you want to attach a disk to.
        disk_link: full or partial URL to a persistent disk that you want to attach. This can be either
            regional or zonal disk.
            Expected formats:
                * https://www.googleapis.com/compute/v1/projects/[project]/zones/[zone]/disks/[disk_name]
                * /projects/[project]/zones/[zone]/disks/[disk_name]
                * /projects/[project]/regions/[region]/disks/[disk_name]
        mode: Specifies in what mode the disk will be attached to the instance. Available options are `READ_ONLY`
            and `READ_WRITE`. Disk in `READ_ONLY` mode can be attached to multiple instances at once.
    """
    instances_client = compute_v1.InstancesClient()

    request = compute_v1.AttachDiskInstanceRequest()
    request.project = project_id
    request.zone = zone
    request.instance = instance_name
    request.attached_disk_resource = compute_v1.AttachedDisk()
    request.attached_disk_resource.source = disk_link
    request.attached_disk_resource.mode = mode

    operation = instances_client.attach_disk(request)

    wait_for_extended_operation(operation, "disk attachement")


# [END compute_disk_attach]
# [END compute_regional_disk_attach]