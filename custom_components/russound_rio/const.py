"""Constants used for Russound RIO."""

import asyncio

from aiorussound import CommandError

DOMAIN = "russound_rio"

RUSSOUND_MEDIA_TYPE_PRESET = "preset"

SELECT_SOURCE_DELAY = 0.5

RUSSOUND_RIO_EXCEPTIONS = (
    CommandError,
    ConnectionRefusedError,
    TimeoutError,
    asyncio.CancelledError,
)
DOMAIN = "russound_rio"

MBX_SOURCE_MODE_DEVICES: list[dict[str, object]] = [
    {
        "name": "House Streamer 2",
        "host": "192.168.86.XXX",
        "port": 9621,  # replace if your MBX uses a different RIO SE TCP port
        "source_id": 3,  # replace with the actual source number configured on your controller
    },
]
