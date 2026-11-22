"""Every node cloudflow launches carries the tag the terminating function's role requires (spec 003, FR-008).

``csis-sandbox-terraform``'s ``reaper/`` lets its terminating function stop only
instances tagged ``csis:launched-by = cloudflow``. This test launches a cluster
with every AWS call replaced, and reads the tags of the launch request.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

from cloudflow.cluster.AWSCluster import AWSCluster

aws_cluster_module = importlib.import_module("cloudflow.cluster.AWSCluster")

DESCRIPTION = {
    "platform": "AWS",
    "region": "us-east-2",
    "nodeType": "c5.xlarge",
    "nodeCount": 2,
    "tags": [{"Key": "Name", "Value": "launch-tag-test"}, {"Key": "Project", "Value": "Test"}],
    "image_id": "ami-00000000000000000",
    "key_name": "test-key",
    "sg_ids": ["sg-00000000000000000"],
    "subnet_id": "subnet-00000000000000000",
    "placement_group": "test-group",
    "table_name": "test-nodes",
}


class FakeDynamoDB:
    def describe_table(self, **_: Any) -> dict[str, Any]:
        return {"Table": {}}


class FakeEC2:
    def __init__(self) -> None:
        self.launches: list[dict[str, Any]] = []

    def create_instances(self, **request: Any) -> list[Any]:
        self.launches.append(request)
        return []


@pytest.fixture
def ec2(monkeypatch: pytest.MonkeyPatch) -> FakeEC2:
    fake = FakeEC2()
    monkeypatch.setattr(aws_cluster_module.boto3, "client", lambda *_, **__: FakeDynamoDB())
    monkeypatch.setattr(aws_cluster_module.boto3, "resource", lambda *_, **__: fake)
    helper = aws_cluster_module.AWSHelper
    monkeypatch.setattr(helper, "getPPN", lambda *_: 2)
    monkeypatch.setattr(helper, "maxNetworkCards", lambda *_: 1)
    monkeypatch.setattr(helper, "supportsThreadsPerCoreOption", lambda *_: False)
    monkeypatch.setattr(helper, "supportsEFA", lambda *_: False)
    return fake


def test_a_launch_request_carries_the_launch_tag(ec2: FakeEC2, tmp_path: Path) -> None:
    description = tmp_path / "test.cluster"
    description.write_text(json.dumps(DESCRIPTION))
    AWSCluster(str(description)).create_instances()
    (request,) = ec2.launches
    (spec,) = request["TagSpecifications"]
    assert spec["ResourceType"] == "instance"
    tags = spec["Tags"]
    assert {"Key": "csis:launched-by", "Value": "cloudflow"} in tags
    keys = [tag["Key"] for tag in tags]
    assert keys.index("csis:launched-by") > keys.index("ApprovedSubnet")
    assert {"Key": "Project", "Value": "Test"} in tags


def test_the_tag_is_one_constant() -> None:
    assert aws_cluster_module.LAUNCH_TAG == {"Key": "csis:launched-by", "Value": "cloudflow"}
