import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dateutil.relativedelta import relativedelta

import dagster as dg

from ..partitions import country_partition, dimensional_partition
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
    schema = "id,type,name,regionalScope,temporalScope,nationwide,isoCode,startDate,endDate".split(
        ","
    )
    df = pd.DataFrame([], columns=schema)
    if len(country_holidays) > 0:
        df = pd.concat([df, pd.DataFrame(country_holidays)])
        df["isoCode"] = country
        df = df[schema]
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


@dg.asset(
    partitions_def=country_partition,
    deps=[
        dg.AssetDep(
            asset=holidays,
            partition_mapping=dg.MultiToSingleDimensionPartitionMapping("country"),
        )
    ],
    kinds={"pandas"},
)
def yearly_stats(context: dg.AssetExecutionContext, holidays):
    """
    Estimate yearly holidays
    """
    holidays_partitions = holidays.values()
    df = pd.concat(list(holidays_partitions))
    df["year"] = pd.to_datetime(df["startDate"]).dt.year
    total = df.groupby(["isoCode", "year"]).size().unstack().fillna(0)
    context.log_event(
        dg.AssetObservation(
            asset_key=dg.AssetKey(["yearly_stats"]),
            metadata={"sample": dg.MetadataValue.md(total.to_markdown())},
        )
    )

    return total


@dg.asset(deps=[yearly_stats], kinds={"pandas"})
def summary(context: dg.AssetExecutionContext, yearly_stats):
    """Identify holiday paradise"""
    context.log.info(str(type(yearly_stats)))
    countries = yearly_stats.values()
    df = pd.concat(list(countries))
    context.log_event(
        dg.AssetObservation(
            asset_key=dg.AssetKey(["summary"]),
            metadata={"sample": dg.MetadataValue.md(df.to_markdown())},
        )
    )
    return df


@dg.asset(
    deps=[summary],
    kinds={"matplotlib"},
)
def heatmap(context: dg.AssetExecutionContext, summary):
    """Heatmap of holidays by country"""

    context.log.info(str(type(summary)))

    data = summary
    plt.figure(figsize=(10, 14))
    ax = sns.heatmap(data.sort_index(), annot=True, fmt="d", cmap="viridis")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha="right")

    # Save to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")

    buf.seek(0)

    # Encode the image to base64
    image_data = base64.b64encode(buf.getvalue()).decode()

    # Create Markdown content
    md_content = f"![img](data:image/png;base64,{image_data})"

    # Attach the Markdown content as metadata
    plt.close()

    return dg.Output(value=data, metadata={"plot": dg.MetadataValue.md(md_content)})
