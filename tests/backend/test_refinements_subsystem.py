import pytest

from backend.app.config.secrets import SecretsManager
from backend.app.events.bus import EventBus
from backend.app.events.types import SnapshotCreatedEvent
from backend.app.ml.canary import CanaryDeploymentManager
from backend.app.models.lineage import DataLineage
from backend.app.scheduler.runner import PlatformScheduler
from backend.app.storage.provider import LocalStorageProvider, S3StorageProvider
from backend.app.tasks.queue import TaskQueue


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    received_events = []

    def handle_snapshot(evt: SnapshotCreatedEvent):
        received_events.append(evt)

    bus.subscribe(SnapshotCreatedEvent, handle_snapshot)

    event = SnapshotCreatedEvent(event_id="evt_101", full_name="facebook/react", stars_count=220000)
    await bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].full_name == "facebook/react"
    assert received_events[0].stars_count == 220000


@pytest.mark.asyncio
async def test_platform_scheduler_job_execution():
    scheduler = PlatformScheduler()
    counter = {"runs": 0}

    def sample_job():
        counter["runs"] += 1

    scheduler.add_job("job_daily", "Daily Collection", 86400, sample_job)
    await scheduler.run_job_once("job_daily")

    assert counter["runs"] == 1
    jobs = scheduler.get_registered_jobs()
    assert len(jobs) == 1
    assert jobs[0]["run_count"] == 1


def test_artifact_storage_providers(tmp_path):
    # Local Storage Provider
    local_provider = LocalStorageProvider(base_dir=tmp_path)
    data = b"model_binary_content_v1"
    uri = local_provider.save_artifact("models/v1/model.ubj", data)
    assert uri.startswith("file://")
    assert local_provider.artifact_exists("models/v1/model.ubj")
    loaded = local_provider.load_artifact("models/v1/model.ubj")
    assert loaded == data

    # S3 Storage Provider
    s3_provider = S3StorageProvider(bucket_name="rip-model-bucket")
    s3_uri = s3_provider.save_artifact("models/v1/model.ubj", data)
    assert s3_uri == "s3://rip-model-bucket/models/v1/model.ubj"
    assert s3_provider.artifact_exists("models/v1/model.ubj")
    assert s3_provider.load_artifact("models/v1/model.ubj") == data


def test_secrets_manager_resolution():
    secrets = SecretsManager()
    val = secrets.get_secret("NON_EXISTENT_KEY", default="default_fallback")
    assert val == "default_fallback"

    token = secrets.get_secret("GITHUB_TOKEN")
    assert token != ""


@pytest.mark.asyncio
async def test_task_queue_async_execution():
    queue = TaskQueue()

    async def mock_handler(payload: dict):
        return {"processed_repo": payload["repo"]}

    queue.register_handler("compute_features", mock_handler)
    task_id = await queue.enqueue("compute_features", {"repo": "facebook/react"})

    processed = await queue.process_next()
    assert processed is True

    status = queue.get_task_status(task_id)
    assert status is not None
    assert status.status == "completed"
    assert status.result == {"processed_repo": "facebook/react"}


def test_canary_deployment_routing():
    canary = CanaryDeploymentManager(challenger_traffic_pct=0.20)
    routed = [canary.route_request("v1.0", "v2.0-candidate")[1] for _ in range(100)]

    assert "champion" in routed
    metrics = canary.get_traffic_metrics()
    assert metrics["total_requests_routed"] == 100


def test_data_lineage_trace_integrity():
    lineage = DataLineage(model_version="v1.0", dataset_version="v1.0")
    assert lineage.prediction_id != ""
    assert lineage.model_version == "v1.0"
    assert lineage.git_commit != ""
