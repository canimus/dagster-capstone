from typing import List

import requests
from furl import furl

from dagster import ConfigurableResource


class OpenHolidaysResource(ConfigurableResource):
    url: str = "https://openholidaysapi.org/"

    def holidays(self, country: str, start_date: str, end_date: str) -> List[str]:
        params = {
            "countryIsoCode": country,
            "languageIsoCode": "EN",
            "validFrom": start_date,
            "validTo": end_date,
        }
        return requests.get(furl(self.url) / "PublicHolidays", params=params).json()
