import dagster as dg
from dagster_duckdb import DuckDBResource

from ..resources import OpenHolidaysResource


@dg.asset
def locations(
    context: dg.AssetExecutionContext,
    holidays: OpenHolidaysResource,
    database: DuckDBResource,
):
    return holidays.langugages()
