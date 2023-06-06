# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio

import requests
from urllib.parse import urlencode

from modules.utilities import valid_location, valid_data_types, unique_ids


class OpenDataHubCrawler:
    async def stations_for(self, category):
        return await asyncio.create_task(self._stations_for(category))

    async def data_types_for(self, category, station, allowed_data_types):
        return await asyncio.create_task(self._data_types_for(category, station, allowed_data_types))

    async def records_for(self, category, station, data_type_id, start, end):
        return await asyncio.create_task(self._records_for(category, station, data_type_id, start, end))

    async def _stations_for(self, category):
        url = self._url_for(category, "get-station-details")
        stations = self._get(url)
        return list(filter(lambda it: valid_location(it), stations))

    async def _data_types_for(self, category, station, allowed_data_types):
        url = self._url_for(category, "get-data-types", urlencode({'station': station["id"]}))
        data_type_ids = unique_ids(self._get(url))
        return valid_data_types(data_type_ids, allowed_data_types)

    async def _records_for(self, category, station, data_type_id, start, end):
        query_string = urlencode({
            "station": station["id"],
            "name": data_type_id, "from": int(start.timestamp()) * 1000,
            "to": int(end.timestamp()) * 1000
        })
        url = self._url_for(category, "get-records-in-timeframe", query_string)
        return self._get(url)

    def _get(self, url):
        try:
            resp = requests.get(url=url)
            data = resp.json()
        except:
            print("An exception occurred") 
            data = []
        return data

    def _url_for(self, category, operation, query_string=None):
        if query_string is None:
            query_string = ""
        else:
            query_string = "?%s" % query_string
        return "http://ipchannels.integreen-life.bz.it/" + category + "/rest/" + operation + query_string
