import dagster as dg
import pandas as pd

from ..resources import OpenHolidaysResource


@dg.asset(kinds={"python"})
def locations(
    context: dg.AssetExecutionContext,
    holidays: OpenHolidaysResource,
):
    """
    Retrieves countries available for holidays
    """
    countries = holidays.langugages()
    df = pd.DataFrame()
    if len(countries) > 0:
        df = pd.concat([df, pd.DataFrame(countries)])
        context.log_event(
            dg.AssetObservation(
                asset_key=dg.AssetKey(["locations"]),
                metadata={
                    "sample": dg.MetadataValue.md(df.isoCode.head().to_markdown())
                },
            )
        )
    return dg.Output(value=df, metadata={"dagster/row_count": len(countries)})
