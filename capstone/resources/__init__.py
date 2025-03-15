import requests
from dagster import ConfigurableResource
from typing import List
from furl import furl

class OpenHolidaysResource(ConfigurableResource):
    url: str = "https://openholidaysapi.org/"

    def langugages(self) -> List[str]:
        return requests.get(furl(self.url) / "Languages").json()