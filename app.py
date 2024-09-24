from contextlib import asynccontextmanager

import redis
import requests
from fastapi import FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from records import Station

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
REDIS_PREFIX = "bysykkel_station"


def _redis_key(key: str) -> str:
    return f"{REDIS_PREFIX}:{key}"


def fetch_station_data() -> dict[int, Station]:
    url = "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    stations: dict[int, Station] = {}
    for station in data["data"]["stations"]:
        station_id = station["station_id"]
        stations[station_id] = Station(
            id=station_id,
            name=station["name"],
            address=station["address"]
        )

    return stations


def fetch_availability_data(station_data: dict[int, Station]) -> dict[int, Station]:
    url = "https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    for station_availability in data["data"]["stations"]:
        station_id = station_availability["station_id"]
        if station_id in station_data:
            station_data[station_id].num_bikes_available = station_availability["num_bikes_available"]

    return station_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On boot, fetch station and availability data from the Bysykkel APIs
    and store it in redis.
    """

    station_data = fetch_station_data()
    availability_data = fetch_availability_data(station_data)
    for station_id, station_data in availability_data.items():
        r.hset(_redis_key(str(station_id)), mapping=station_data.model_dump())

    yield

    # Clear redis cache
    for key in r.scan_iter(f"{REDIS_PREFIX}:*"):
        r.delete(key)


app = FastAPI(lifespan=lifespan)


@app.get("/api/stations/available")
async def stations_with_bikes():
    """
    Returns all stations with available bikes.
    """
    stations = []
    for key in r.scan_iter(f"{REDIS_PREFIX}:*"):
        station_data = r.hgetall(key)
        if station_data and int(station_data["num_bikes_available"]) > 0:  # type: ignore
            stations.append(station_data)

    if stations:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(stations),
        )
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stations/{station_id}")
async def station_details(station_id: int) -> JSONResponse:
    """
    Returns the station with ID {station_id}, if any.
    """
    station_data = r.hgetall(_redis_key(str(station_id)))
    if station_data:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(station_data),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"No data found for station with ID {station_id}"
        )
