"""Global pytest fixtures for BreatheSmart test suite."""

import httpx
import pytest
from app.api.v1.endpoints.air_quality import aq_provider as ep_aq_provider
from app.api.v1.endpoints.assistant import aq_provider as ep_asst_aq_provider
from app.api.v1.endpoints.locations import geocoding_provider as ep_geo_provider
from app.api.v1.endpoints.recommendations import service as ep_rec_service
from app.db.session import engine


@pytest.fixture(autouse=True)
async def cleanup_connections():
    """Ensure all pooled DB connections and HTTP provider clients are cleanly closed between tests."""
    yield
    await engine.dispose()

    # Close and reset HTTP provider clients so they don't attach to closed event loops
    for provider in [
        ep_aq_provider,
        ep_rec_service.aq_provider,
        ep_asst_aq_provider,
        ep_geo_provider,
    ]:
        if hasattr(provider, "_client") and not provider._client.is_closed:
            await provider._client.aclose()
        provider._client = httpx.AsyncClient(timeout=10.0)
