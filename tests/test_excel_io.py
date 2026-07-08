import pandas as pd
import pytest

from src.excel_io import MissingColumnsError, load_excel, validate_required_columns


def test_load_excel_reads_rows_and_columns(tmp_path):
    source_path = tmp_path / "orders.xlsx"
    pd.DataFrame({"order_id": ["SO-1", "SO-2"], "quantity": [10, 5]}).to_excel(
        source_path, index=False
    )

    df = load_excel(source_path)

    assert list(df.columns) == ["order_id", "quantity"]
    assert df["order_id"].tolist() == ["SO-1", "SO-2"]


def test_validate_required_columns_passes_when_all_present():
    df = pd.DataFrame({"order_id": ["SO-1"], "sku": ["MED-LENS-001"]})

    validate_required_columns(df, ["order_id", "sku"], "orders file")


def test_validate_required_columns_raises_business_readable_message():
    df = pd.DataFrame({"order_id": ["SO-1"]})

    with pytest.raises(MissingColumnsError) as excinfo:
        validate_required_columns(df, ["order_id", "sku"], "orders file")

    assert "orders file" in str(excinfo.value)
    assert "sku" in str(excinfo.value)
    assert excinfo.value.missing_columns == ["sku"]
