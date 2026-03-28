# HA Russound RIO Enhanced

Enhanced Home Assistant integration for Russound RIO systems, built to improve support for real world multizone installations such as the SMZ16 PRE and MBX PRE.

## Why this exists

This project started from a real world issue where Home Assistant exposed only 1 zone for an SMZ16 PRE even though the controller supports 16 zones.

The root cause was traced to `aiorussound`, where the model was not recognized correctly for max zone discovery. A fix was developed, tested, and proposed upstream.

This repo provides a working custom integration layer for Russound based Home Assistant setups and a place for further feature enhancements.

## Current features

### Media player
- Zone on and off
- Volume set
- Volume step up and down
- Mute and unmute
- Source selection
- Seek
- Preset playback
- Preset browsing
- Metadata including title, artist, album, cover art, duration, and position

### Number entities
- Balance
- Bass
- Treble
- Turn on volume

### Switch entities
- Loudness

## Tested hardware
- Russound SMZ16 PRE
- Russound MBX PRE
- Home Assistant Green

## Installation

### Manual install
1. Copy `custom_components/russound_rio` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from Settings > Devices & Services.
4. Enter the Russound controller IP and port.

## Project status

This is an unofficial custom integration and is not affiliated with Russound or Home Assistant.

It currently focuses on improved multizone support and additional entity exposure for Russound systems.

## Roadmap
- Additional controller level features
- Better source and streamer modeling
- Favorites and automation oriented services
- Expanded Russound source side support

## Credits
- Russound
- `aiorussound` maintainers and contributors
- Home Assistant community
