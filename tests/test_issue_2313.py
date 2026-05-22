import pytest
import json
from src.common.config import Config

def test_config_root_object_validation(tmp_path):
    config_file = tmp_path / "config.json"
    
    # Valid dict config
    config_file.write_text(json.dumps({"port": 8080}))
    cfg = Config(str(config_file))
    assert cfg.get("port") == 8080
    
    # Invalid list config
    config_file.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(TypeError, match="Config root must be an object"):
        Config(str(config_file))
