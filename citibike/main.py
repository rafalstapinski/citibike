import asyncio
from datetime import datetime, timedelta

import httpx
import uvloop
from p3orm import Porm

from citibike.models.db import Run, Station, StationStatus
from citibike.models.gql import CitiBikeResponse
from citibike.settings import Settings

request = httpx.Request(
    "POST",
    "https://account.citibikenyc.com/bikesharefe-gql",
    json={
        "query": "query {supply {stations {stationId stationName siteId bikesAvailable ebikesAvailable bikeDocksAvailable location {lat lng}}}}"
    },
)

run_count = 1


async def run():

    global run_count
    run_time = datetime.utcnow()
    print(f"""starting run {run_count} @ {(run_time - timedelta(hours=4)).strftime("%c")}""")

    await Porm.connect(dsn=Settings.DATABASE_URL)

    run = await Run.insert_one(Run(time=run_time))

    async with httpx.AsyncClient() as client:
        response = await client.send(request)

    data = CitiBikeResponse.parse_obj(response.json())

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
                run_id=run.id,
            )
        )

    await Porm.disconnect()


async def daemon():
    global run_count
    while True:
        asyncio.ensure_future(run())
        await asyncio.sleep(5 * 60)
        run_count += 1


# daemonize, with ensure_future spitting out every 5 min
if __name__ == "__main__":
    uvloop.install()
    asyncio.run(daemon())
