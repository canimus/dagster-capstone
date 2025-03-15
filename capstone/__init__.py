from dagster_duckdb import DuckDBResource

from dagster import Definitions, load_assets_from_modules

from .assets import holidays
from .resources import OpenHolidaysResource

holidays_assets = load_assets_from_modules([holidays])
defs = Definitions(
    assets=[*holidays_assets],
    resources={
        "database": DuckDBResource(database="data/bronze/db.duckdb"),
        "holidays": OpenHolidaysResource(),
        # "io_manager": DuckDBPandasIOManager(database="data/bronze/db.duckdb"),
    },
)
