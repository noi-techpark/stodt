import asyncio
import datetime
import json
import sys
import os

from modules.saver import Saver
from modules.opendatahub import OpenDataHubCrawler
from modules.utilities import date_from, time_frames_from, today

with open('./config.json') as configfile:
    config = json.loads("".join(configfile.readlines()))
categories = config["categories"]
data_dir = config["data_dir"]
days_between_calls = config["download"]["days_between_calls"]

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        global_end = today()
        global_start = global_end - datetime.timedelta(days=10)
    else:
        global_end = date_from(config["download"]["time_to"])
        global_start = date_from(config["download"]["time_from"])

time_frames = time_frames_from(global_start, global_end, days_between_calls)

crawler = OpenDataHubCrawler()
saver = Saver(categories, data_dir)


async def main():
    for index in range(len(categories)):
        category = categories[index]["category"]
        allowed_data_types = categories[index]["allowed_data_types"]

        stations = await crawler.stations_for(category)
        for station in stations:
            data_types = await crawler.data_types_for(category, station, allowed_data_types)

            for data_type_id in data_types:

                for time_frame_index in range(len(time_frames) - 1):
                    start = time_frames[time_frame_index]
                    end = time_frames[time_frame_index + 1]
                    records = await crawler.records_for(category, station, data_type_id, start, end)

                    saver.write(category, data_type_id, records)

                    print("obtained %i records for %s %s %s (%s -> %s)" % (
                        len(records), category, station["id"], data_type_id, start.strftime('%Y-%m-%d'),
                        end.strftime('%Y-%m-%d')))

    saver.save()


asyncio.run(main())
