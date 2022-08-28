from __future__ import annotations

from datetime import datetime

from p3orm import Column, ForeignKeyRelationship, ReverseRelationship, Table


class Run(Table):
    __tablename__ = "run"

    id = Column(int, pk=True, autogen=True)
    time = Column(datetime)

    statuses: list[StationStatus] = ReverseRelationship(
        self_column="id",
        foreign_column="run_id",
    )


class Station(Table):
    __tablename__ = "station"

    id = Column(int, pk=True, autogen=True)
    citibike_id = Column(str)
    site_id = Column(str)
    name = Column(str)
    latitude = Column(float)
    longitude = Column(float)
    created_at = Column(datetime, autogen=True)

    statuses: list[StationStatus] = ReverseRelationship(
        self_column="id",
        foreign_column="station_id",
    )


class StationStatus(Table):
    __tablename__ = "station_status"

    id = Column(int, pk=True, autogen=True)
    station_id = Column(int)
    bikes_available = Column(int)
    ebikes_available = Column(int)
    docks_available = Column(int)
    run_id = Column(int)

    station: Station = ForeignKeyRelationship(
        self_column="station_id",
        foreign_column="id",
    )

    run: Run = ForeignKeyRelationship(
        self_column="run_id",
        foreign_column="id",
    )
