from unittest.mock import MagicMock

from sycamore.query.schema import OpenSearchSchemaFetcher


def test_opensearch_schema():
    mock_client = MagicMock()
    mock_client.get_field_mapping.return_value = {
        "test_index": {
            "mappings": {
                "properties.entity.day": {"full_name": "properties.entity.day", "mapping": {"day": {"type": "date"}}},
                "properties.entity.aircraft": {
                    "full_name": "properties.entity.aircraft",
                    "mapping": {
                        "aircraft": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}
                    },
                },
                "properties.entity.location": {
                    "full_name": "properties.entity.location",
                    "mapping": {
                        "location": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}
                    },
                },
                "properties.entity.weather": {
                    "full_name": "properties.entity.weather",
                    "mapping": {
                        "weather": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}
                    },
                },
            }
        }
    }

    mock_query_executor = MagicMock()
    # Note that there are no values for 'location' here.
    mock_query_executor.query.return_value = {
        "result": {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "properties": {
                                "entity": {
                                    "day": "2021-01-01",
                                    "aircraft": "Boeing 747",
                                }
                            }
                        }
                    },
                    {
                        "_source": {
                            "properties": {
                                "entity": {"day": "2021-01-02", "aircraft": "Airbus A380", "weather": "Sunny"}
                            }
                        }
                    },
                ]
            }
        }
    }

    fetcher = OpenSearchSchemaFetcher(mock_client, "test_index", mock_query_executor)
    got = fetcher.get_schema()
    assert "text_representation" in got
    assert got["text_representation"] == ("<class 'str'>", {"Can be assumed to have all other details"})
    assert "properties.entity.day" in got
    assert got["properties.entity.day"] == ("<class 'str'>", {"2021-01-01", "2021-01-02"})
    assert "properties.entity.aircraft" in got
    assert got["properties.entity.aircraft"] == ("<class 'str'>", {"Boeing 747", "Airbus A380"})
    assert "properties.entity.weather" in got
    assert got["properties.entity.weather"] == ("<class 'str'>", {"Sunny"})
    assert "properties.entity.location" not in got