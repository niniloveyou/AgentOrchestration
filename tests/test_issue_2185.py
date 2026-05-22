from src.common.metrics import MetricsCollector

def test_metrics_timer_no_deadlock():
    collector = MetricsCollector()
    collector.start_timer("db_query")
    dur = collector.stop_timer("db_query")
    assert dur >= 0
