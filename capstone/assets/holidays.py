from datetime import datetime

import dagster as dg
import pandas as pd
from dateutil.relativedelta import relativedelta

from ..partitions import dimensional_partition
from ..resources import OpenHolidaysResource


@dg.asset(
    kinds={"python"},
    partitions_def=dimensional_partition,
    metadata={"partition_expr": {"country": "isoCode", "month": "startDate"}},
)
def holidays(
    context: dg.AssetExecutionContext,
    holidays: OpenHolidaysResource,
):
    """
    Retrieves countries holidays
    """
    dimension = context.partition_key
    country, start_date = dimension.split("|")

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = start_date_obj + relativedelta(months=1)
    end_date = end_date_obj.strftime("%Y-%m-%d")

    country_holidays = holidays.holidays(
        country=country, start_date=start_date, end_date=end_date
    )
    df = pd.DataFrame()
    if len(country_holidays) > 0:
        df = pd.concat([df, pd.DataFrame(country_holidays)])
        df["isoCode"] = country
        df = df[
            "id,type,name,regionalScope,temporalScope,nationwide,isoCode,startDate,endDate".split(
                ","
            )
        ]
        context.log_event(
            dg.AssetObservation(
                asset_key=dg.AssetKey(["holidays"]),
                metadata={
                    "start": dg.MetadataValue.text(str(start_date)),
                    "end": dg.MetadataValue.text(str(end_date)),
                    "sample": dg.MetadataValue.md(df.head().to_markdown()),
                },
            )
        )
    return df
