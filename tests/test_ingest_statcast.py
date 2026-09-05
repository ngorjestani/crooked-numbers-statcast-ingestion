from datetime import date
from unittest.mock import Mock, call

import pandas as pd
import pytest

from crooked_numbers_ingest import ingest_statcast
from crooked_numbers_ingest.settings import Settings
from crooked_numbers_ingest.storage import build_blob_path


@pytest.mark.parametrize("has_following_data", [False, True])
def test_empty_response_skips_write_and_continues(
    monkeypatch, caplog, has_following_data
):
    dates = [date(2026, 7, 13), date(2026, 7, 14)]
    empty = pd.DataFrame(columns=["game_pk", "at_bat_number", "pitch_number"])
    populated = pd.DataFrame([{"game_pk": 1, "at_bat_number": 2, "pitch_number": 3}])
    fetch = Mock(side_effect=[empty, populated if has_following_data else empty])
    convert = Mock(return_value=b"parquet")
    sink = Mock()
    monkeypatch.setattr("sys.argv", ["ingest_statcast"])
    monkeypatch.setattr(ingest_statcast.Settings, "from_env", Mock(return_value=Settings()))
    monkeypatch.setattr(ingest_statcast, "target_dates", Mock(return_value=dates))
    monkeypatch.setattr(ingest_statcast, "fetch_statcast_for_date", fetch)
    monkeypatch.setattr(ingest_statcast, "statcast_dataframe_to_parquet_bytes", convert)
    monkeypatch.setattr(ingest_statcast, "create_parquet_sink", Mock(return_value=sink))
    caplog.set_level("INFO")

    ingest_statcast.run()

    assert fetch.call_args_list == [call(day) for day in dates]
    assert "No rows returned for 2026-07-13; skipping conversion and upload" in caplog.text
    assert convert.call_count == int(has_following_data)
    assert sink.write_parquet.call_count == int(has_following_data)
    if has_following_data:
        assert convert.call_args.args[0] is populated
        assert sink.write_parquet.call_args.args == (build_blob_path(dates[1]), b"parquet")
