from src.common.metrics import MetricsCollector

def test_metrics_collector_reset():
    collector = MetricsCollector()
    collector.increment("hits")
    collector.gauge("temp", 36.5)
    
    snap = collector.snapshot()
    assert snap["counters"]["hits"] == 1
    assert snap["gauges"]["temp"] == 36.5
    
    collector.reset()
    snap_after = collector.snapshot()
    assert "hits" not in snap_after["counters"]
    assert "temp" not in snap_after["gauges"]
