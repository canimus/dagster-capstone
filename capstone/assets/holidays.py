import dagster as dg
import pandas as pd

from ..partitions import country_partition
from ..resources import OpenHolidaysResource


@dg.asset(
    kinds={"python"},
    partitions_def=country_partition,
    metadata={"partition_expr": "isoCode"},
)
def holidays(
    context: dg.AssetExecutionContext,
    holidays: OpenHolidaysResource,
):
    """
    Retrieves countries available for holidays
    """
    country = context.partition_key
    country_holidays = holidays.holidays(
        country=country, start_date="2024-01-01", end_date="2025-01-01"
    )
    df = pd.DataFrame()
    if len(country_holidays) > 0:
        df = pd.concat([df, pd.DataFrame(country_holidays)])
        df["isoCode"] = country
        context.log_event(
            dg.AssetObservation(
                asset_key=dg.AssetKey(["holidays"]),
                partition=country,
                metadata={"sample": dg.MetadataValue.md(df.head().to_markdown())},
            )
        )
    return dg.Output(value=df, metadata={"dagster/row_count": len(country_holidays)})
