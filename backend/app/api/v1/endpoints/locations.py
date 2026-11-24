from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_or_create_session
from app.models.location import SavedLocation
from app.models.session import UserSession
from app.providers.geocoding.open_meteo import OpenMeteoGeocodingProvider
from app.schemas.geocoding import LocationSearchResult
from app.schemas.location import LocationCreate, SavedLocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])
geocoding_provider = OpenMeteoGeocodingProvider()


@router.get("/search", response_model=list[LocationSearchResult])
async def search_cities(q: str = Query(min_length=2, max_length=100)):
    """Debounced city lookup resolving coordinates and country metadata."""
    return await geocoding_provider.search_locations(q)


@router.post("", response_model=SavedLocationResponse, status_code=status.HTTP_201_CREATED)
async def save_location(
    loc_in: LocationCreate,
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save a user-configured location."""
    new_loc = SavedLocation(
        id=uuid.uuid4(),
        session_id=session.id,
        city=loc_in.city,
        region=loc_in.region,
        country=loc_in.country,
        latitude=loc_in.latitude,
        longitude=loc_in.longitude,
        is_primary=loc_in.is_primary,
    )
    db.add(new_loc)
    await db.commit()
    await db.refresh(new_loc)
    return new_loc


@router.get("", response_model=list[SavedLocationResponse])
async def list_saved_locations(
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve all locations saved in the current session."""
    stmt = select(SavedLocation).where(SavedLocation.session_id == session.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_location(
    location_id: uuid.UUID,
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a saved location."""
    stmt = delete(SavedLocation).where(
        SavedLocation.id == location_id,
        SavedLocation.session_id == session.id,
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    await db.commit()
