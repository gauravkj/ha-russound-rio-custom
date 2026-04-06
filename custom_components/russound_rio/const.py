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

MBX_SOURCE_MODE_DEVICES: list[dict[str, object]] = [
    {
        "name": "House Streamer 2",
        "host": "192.168.86.58",  # replace with actual MBX-PRE IP
        "port": 9621,  # confirm this is the correct RIO SE port
        "source_id": 3,  # replace with the actual controller source number
    },
]
