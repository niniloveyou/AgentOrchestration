from src.common.metrics import MetricsCollector

def test_snapshot_active_timers():
    collector = MetricsCollector()
    assert collector.snapshot()["active_timers"] == 0
    collector.start_timer("job_run")
    assert collector.snapshot()["active_timers"] == 1
    collector.stop_timer("job_run")
    assert collector.snapshot()["active_timers"] == 0
