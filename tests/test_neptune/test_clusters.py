import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html


@mock_aws
def test_create_db_cluster():
    client = boto3.client("neptune", region_name="us-east-2")
    resp = client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")[
        "DBCluster"
    ]
    assert resp["DBClusterIdentifier"] == "cluster-id"
    assert "DbClusterResourceId" in resp
    assert "DBClusterArn" in resp
    assert resp["Engine"] == "neptune"
    assert "EngineVersion" in resp
    assert resp["StorageEncrypted"] is False
    assert resp["DBClusterParameterGroup"].startswith("default.neptune")
    assert "Endpoint" in resp
    assert "cluster-" in resp["DbClusterResourceId"]
    assert resp["AvailabilityZones"] == ["us-east-2a", "us-east-2b", "us-east-2c"]
    assert "ServerlessV2ScalingConfiguration" not in resp

    # Double check this cluster is not available in another region
    europe_client = boto3.client("neptune", region_name="eu-west-2")
    assert len(europe_client.describe_db_clusters()["DBClusters"]) == 0


@mock_aws
def test_create_db_cluster__with_additional_params():
    client = boto3.client("neptune", region_name="us-east-1")
    resp = client.create_db_cluster(
        DBClusterIdentifier="cluster-id",
        Engine="neptune",
        EngineVersion="1.1.0.1",
        StorageEncrypted=False,
        DBClusterParameterGroupName="myprm",
        KmsKeyId="key",
        ServerlessV2ScalingConfiguration={"MinCapacity": 1.0, "MaxCapacity": 2.0},
        DatabaseName="sth",
    )["DBCluster"]
    assert resp["StorageEncrypted"] is False
    assert resp["DBClusterParameterGroup"] == "myprm"
    assert resp["EngineVersion"] == "1.1.0.1"
    assert resp["KmsKeyId"] == "key"
    assert resp["ServerlessV2ScalingConfiguration"] == {
        "MinCapacity": 1.0,
        "MaxCapacity": 2.0,
    }
    assert resp["DatabaseName"] == "sth"


@mock_aws
def test_create_db_cluster_with_instance():
    client = boto3.client("neptune", region_name="us-east-2")
    resp = client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")[
        "DBCluster"
    ]
    client.create_db_instance(
        DBInstanceIdentifier="instance-id",
        DBClusterIdentifier="cluster-id",
        Engine="neptune",
        DBInstanceClass="db.r5.large",
    )
    resp = client.describe_db_instances(DBInstanceIdentifier="instance-id")[
        "DBInstances"
    ]
    assert resp[0]["DBInstanceIdentifier"] == "instance-id"
    assert resp[0]["DBInstanceClass"] == "db.r5.large"
    assert resp[0]["DBClusterIdentifier"] == "cluster-id"
    assert resp[0]["Engine"] == "neptune"
    assert resp[0]["EngineVersion"] == "1.3.2.1"


@mock_aws
def test_describe_db_clusters():
    client = boto3.client("neptune", region_name="ap-southeast-1")
    assert client.describe_db_clusters()["DBClusters"] == []

    client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")

    clusters = client.describe_db_clusters(DBClusterIdentifier="cluster-id")[
        "DBClusters"
    ]
    assert len(clusters) == 1
    assert clusters[0]["DBClusterIdentifier"] == "cluster-id"
    assert clusters[0]["Engine"] == "neptune"


@mock_aws
def test_delete_db_cluster():
    client = boto3.client("neptune", region_name="ap-southeast-1")

    client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")
    client.delete_db_cluster(DBClusterIdentifier="cluster-id")

    assert client.describe_db_clusters()["DBClusters"] == []


@mock_aws
def test_remove_db_instance():
    client = boto3.client("neptune", region_name="us-east-2")
    client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")[
        "DBCluster"
    ]
    client.create_db_instance(
        DBInstanceIdentifier="instance-id",
        DBClusterIdentifier="cluster-id",
        Engine="neptune",
        DBInstanceClass="db.r5.large",
    )

    cluster = client.describe_db_clusters()["DBClusters"][0]
    assert "DBClusterMembers" in cluster
    assert len(cluster["DBClusterMembers"]) == 1

    client.delete_db_instance(
        DBInstanceIdentifier="instance-id",
        SkipFinalSnapshot=True,
    )

    cluster = client.describe_db_clusters()["DBClusters"][0]
    assert "DBClusterMembers" in cluster
    assert len(cluster["DBClusterMembers"]) == 0


@mock_aws
def test_delete_unknown_db_cluster():
    client = boto3.client("neptune", region_name="ap-southeast-1")

    with pytest.raises(ClientError) as exc:
        client.delete_db_cluster(DBClusterIdentifier="unknown-id")
    err = exc.value.response["Error"]
    assert err["Code"] == "DBClusterNotFoundFault"


@mock_aws
def test_modify_db_cluster():
    client = boto3.client("neptune", region_name="us-east-1")
    client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")
    resp = client.modify_db_cluster(
        DBClusterIdentifier="cluster-id",
        EngineVersion="1.1.0.1",
        DBClusterParameterGroupName="myprm",
        PreferredBackupWindow="window",
    )["DBCluster"]
    assert resp["DBClusterParameterGroup"] == "myprm"
    assert resp["EngineVersion"] == "1.1.0.1"
    assert resp["PreferredBackupWindow"] == "window"


@mock_aws
def test_start_db_cluster():
    client = boto3.client("neptune", region_name="us-east-2")
    client.create_db_cluster(DBClusterIdentifier="cluster-id", Engine="neptune")
    client.stop_db_cluster(DBClusterIdentifier="cluster-id")
    cluster = client.start_db_cluster(DBClusterIdentifier="cluster-id")["DBCluster"]
    assert cluster["Status"] == "started"
