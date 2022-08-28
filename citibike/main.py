import asyncio
from datetime import datetime

import httpx
import uvloop
from p3orm import Porm

from citibike.models.db import Station, StationStatus
from citibike.models.gql import CitiBikeResponse
from citibike.settings import Settings

request = httpx.Request(
    "POST",
    "https://account.citibikenyc.com/bikesharefe-gql",
    json={
        "query": "query {supply {stations {stationId stationName siteId bikesAvailable ebikesAvailable bikeDocksAvailable location {lat lng}}}}"
    },
)


async def run():

    async with httpx.AsyncClient() as client:
        response = await client.send(request)

    data = CitiBikeResponse.parse_obj(response.json())
    run_time = datetime.utcnow()

    for cb_station in data.data.supply.stations:
        station = await Station.fetch_first(Station.citibike_id == cb_station.station_id)

        if not station:
            station = await Station.insert_one(
                Station(
                    citibike_id=cb_station.station_id,
                    site_id=cb_station.site_id,
                    name=cb_station.station_name,
                    latitude=cb_station.location.lat,
                    longitude=cb_station.location.lng,
                )
            )

        await StationStatus.insert_one(
            StationStatus(
                station_id=station.id,
                bikes_available=cb_station.bikes_available,
                ebikes_available=cb_station.ebikes_available,
                docks_available=cb_station.bike_docks_available,
                run_time=run_time,
            )
        )


async def daemon():
    while True:
        await Porm.connect(dsn=Settings.DATABASE_URL)
        asyncio.ensure_future(run())
        await Porm.disconnect()
        await asyncio.sleep(2)


# daemonize, with ensure_future spitting out every 5 min
if __name__ == "__main__":
    uvloop.install()
    asyncio.run(daemon())