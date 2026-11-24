"""AirQualitySnapshot model caching normalized environmental readings."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AirQualitySnapshot(Base):
    __tablename__ = "air_quality_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), default="Open-Meteo", nullable=False
    )
    index_standard: Mapped[str] = mapped_column(
        String(20), default="US_AQI", nullable=False
    )
    aqi_value: Mapped[int] = mapped_column(Integer, nullable=False)
    aqi_category: Mapped[str] = mapped_column(String(50), nullable=False)
    pollutant_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_air_quality_coords", "latitude", "longitude"),)
