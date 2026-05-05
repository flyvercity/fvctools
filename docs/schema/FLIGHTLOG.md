# JSON Schema

## Properties

- <a id="properties/origin"></a>**`origin`** *(string)*: Originating system.

  Examples:
  ```json
  "airlink"
  ```

  ```json
  "courageous"
  ```

  ```json
  "nmea"
  ```

- <a id="properties/time"></a>**`time`** *(object, required)*: Timestamp of the flight log entry. Cannot contain additional properties.
  - <a id="properties/time/properties/unix"></a>**`unix`** *(number, required)*: Unix timestamp in milliseconds.

    Examples:
    ```json
    1756033206882
    ```

  - <a id="properties/time/properties/rx"></a>**`rx`** *(number)*: Reception timestamp in milliseconds (when data was received by ground system).

    Examples:
    ```json
    1756033207094
    ```

  - <a id="properties/time/properties/original"></a>**`original`** *(string)*: Original timestamp string.

    Examples:
    ```json
    "2025-01-01 12:00:00"
    ```

    ```json
    "2025-01-01 12:00:00.123"
    ```

- <a id="properties/uaid"></a>**`uaid`** *(object)*: Unique aircraft identification. Cannot contain additional properties.
  - **Any of**
  - <a id="properties/uaid/properties/int"></a>**`int`** *(string)*: Source-internal identifier.

    Examples:
    ```json
    "FL001"
    ```

    ```json
    "AC-12345"
    ```

  - <a id="properties/uaid/properties/fvc"></a>**`fvc`** *(string)*: Flyvercity unique identifier.

    Examples:
    ```json
    "fvc-abc123"
    ```

    ```json
    "fvc-xyz789"
    ```

  - <a id="properties/uaid/properties/icaohex"></a>**`icaohex`** *(string)*: ICAO 24-bit address.

    Examples:
    ```json
    "ABC123"
    ```

    ```json
    "4CA123"
    ```

  - <a id="properties/uaid/properties/icaoreg"></a>**`icaoreg`** *(string)*: ICAO registration.

    Examples:
    ```json
    "N123AB"
    ```

    ```json
    "G-ABCD"
    ```

  - <a id="properties/uaid/properties/atm"></a>**`atm`** *(string)*: ATM callsign.

    Examples:
    ```json
    "UAL123"
    ```

    ```json
    "BAW456"
    ```

  - <a id="properties/uaid/properties/ip"></a>**`ip`** *(string)*: IP address.

    Examples:
    ```json
    "192.168.1.100"
    ```

    ```json
    "10.0.0.5"
    ```

  - <a id="properties/uaid/properties/imei"></a>**`imei`** *(string)*: IMEI (International Mobile Equipment Identity) number.

    Examples:
    ```json
    "123456789012345"
    ```

    ```json
    "987654321098765"
    ```

  - <a id="properties/uaid/properties/imsi"></a>**`imsi`** *(string)*: IMSI (International Mobile Subscriber Identity) number.

    Examples:
    ```json
    "310150123456789"
    ```

    ```json
    "310260987654321"
    ```

- <a id="properties/pos"></a>**`pos`** *(object, required)*: Aircraft position and attitude. Cannot contain additional properties.
  - <a id="properties/pos/properties/loc"></a>**`loc`** *(object, required)*: Geographic location of the aircraft. Cannot contain additional properties.
    - <a id="properties/pos/properties/loc/properties/lat"></a>**`lat`** *(number, required)*: Latitude in WGS-84.

      Examples:
      ```json
      55.7558
      ```

      ```json
      -74.006
      ```

    - <a id="properties/pos/properties/loc/properties/lon"></a>**`lon`** *(number, required)*: Longitude in WGS-84.

      Examples:
      ```json
      37.6176
      ```

      ```json
      40.7128
      ```

    - <a id="properties/pos/properties/loc/properties/alt"></a>**`alt`** *(number)*: Ellipsoidal altitude.

      Examples:
      ```json
      100.5
      ```

      ```json
      250.0
      ```

    - <a id="properties/pos/properties/loc/properties/amsl"></a>**`amsl`** *(number)*: Altitude above mean sea level.

      Examples:
      ```json
      95.2
      ```

      ```json
      245.8
      ```

    - <a id="properties/pos/properties/loc/properties/height"></a>**`height`** *(number)*: Local height above ground.

      Examples:
      ```json
      10.5
      ```

      ```json
      25.0
      ```

    - <a id="properties/pos/properties/loc/properties/bear"></a>**`bear`** *(number)*: Bearing angle in degrees clockwise from the true north.

      Examples:
      ```json
      45.0
      ```

      ```json
      180.0
      ```

      ```json
      270.0
      ```

    - <a id="properties/pos/properties/loc/properties/gspeed"></a>**`gspeed`** *(number)*: Ground speed in meters per second.

      Examples:
      ```json
      15.5
      ```

      ```json
      50.0
      ```

      ```json
      120.0
      ```

  - <a id="properties/pos/properties/att"></a>**`att`** *(object)*: Aircraft attitude information. Cannot contain additional properties.
    - <a id="properties/pos/properties/att/properties/roll"></a>**`roll`** *(number, required)*: Roll angle in degrees.

      Examples:
      ```json
      -30.0
      ```

      ```json
      0.0
      ```

      ```json
      15.5
      ```

    - <a id="properties/pos/properties/att/properties/pitch"></a>**`pitch`** *(number, required)*: Pitch angle in degrees.

      Examples:
      ```json
      -10.0
      ```

      ```json
      0.0
      ```

      ```json
      20.0
      ```

    - <a id="properties/pos/properties/att/properties/yaw"></a>**`yaw`** *(number, required)*: Yaw angle in degrees.

      Examples:
      ```json
      0.0
      ```

      ```json
      90.0
      ```

      ```json
      180.0
      ```

      ```json
      270.0
      ```

- <a id="properties/cellsig"></a>**`cellsig`** *(object)*: Cellular signal information. Cannot contain additional properties.
  - <a id="properties/cellsig/properties/radio"></a>**`radio`** *(string)*: Radio technology type. Must be one of: "Unknown", "2G3G", "4GLTE", "5GNSA", or "5GNR".

    Examples:
    ```json
    "4GLTE"
    ```

  - <a id="properties/cellsig/properties/rsrp"></a>**`rsrp`** *(number)*: Reference Signal Received Power (dBm).

    Examples:
    ```json
    -80
    ```

  - <a id="properties/cellsig/properties/rsrq"></a>**`rsrq`** *(number)*: Reference Signal Received Quality (dB).

    Examples:
    ```json
    -10
    ```

  - <a id="properties/cellsig/properties/rssi"></a>**`rssi`** *(number)*: Received Signal Strength Indicator (dBm).

    Examples:
    ```json
    -70
    ```

  - <a id="properties/cellsig/properties/sinr"></a>**`sinr`** *(number)*: Signal-to-Interference-plus-Noise Ratio (dB).

    Examples:
    ```json
    10
    ```

    ```json
    15
    ```

    ```json
    20
    ```

  - <a id="properties/cellsig/properties/csi-rsrp"></a>**`csi-rsrp`** *(number)*: CSI Reference Signal Received Power (dBm).

    Examples:
    ```json
    -85
    ```

    ```json
    -105
    ```

    ```json
    -125
    ```

  - <a id="properties/cellsig/properties/csi-rsrq"></a>**`csi-rsrq`** *(number)*: CSI Reference Signal Received Quality (dB).

    Examples:
    ```json
    -12
    ```

    ```json
    -17
    ```

    ```json
    -22
    ```

  - <a id="properties/cellsig/properties/csi-rssi"></a>**`csi-rssi`** *(number)*: CSI Received Signal Strength Indicator (dBm).

    Examples:
    ```json
    -75
    ```

    ```json
    -95
    ```

    ```json
    -115
    ```

  - <a id="properties/cellsig/properties/csi-sinr"></a>**`csi-sinr`** *(number)*: CSI Signal-to-Interference-plus-Noise Ratio (dB).

    Examples:
    ```json
    8
    ```

    ```json
    13
    ```

    ```json
    18
    ```

  - <a id="properties/cellsig/properties/ss-rsrp"></a>**`ss-rsrp`** *(number)*: Synchronization Signal Reference Signal Received Power (dBm).

    Examples:
    ```json
    -82
    ```

    ```json
    -102
    ```

    ```json
    -122
    ```

  - <a id="properties/cellsig/properties/ss-rsrq"></a>**`ss-rsrq`** *(number)*: Synchronization Signal Reference Signal Received Quality (dB).

    Examples:
    ```json
    -11
    ```

    ```json
    -16
    ```

    ```json
    -21
    ```

  - <a id="properties/cellsig/properties/ss-rssi"></a>**`ss-rssi`** *(number)*: Synchronization Signal Received Signal Strength Indicator (dBm).

    Examples:
    ```json
    -72
    ```

    ```json
    -92
    ```

    ```json
    -112
    ```

  - <a id="properties/cellsig/properties/ss-sinr"></a>**`ss-sinr`** *(number)*: Synchronization Signal Signal-to-Interference-plus-Noise Ratio (dB).

    Examples:
    ```json
    9
    ```

    ```json
    14
    ```

    ```json
    19
    ```

  - <a id="properties/cellsig/properties/arfcn"></a>**`arfcn`** *(number)*: Absolute Radio Frequency Channel Number.

    Examples:
    ```json
    100
    ```

    ```json
    500
    ```

    ```json
    1000
    ```

  - <a id="properties/cellsig/properties/band"></a>**`band`** *(string)*: Frequency band identifier.

    Examples:
    ```json
    "B1"
    ```

    ```json
    "B3"
    ```

    ```json
    "B7"
    ```

    ```json
    "n78"
    ```

  - <a id="properties/cellsig/properties/cgi"></a>**`cgi`** *(string)*: Cell Global Identity.

    Examples:
    ```json
    "310-150-123456-789"
    ```

    ```json
    "310-260-987654-321"
    ```

  - <a id="properties/cellsig/properties/plmnid"></a>**`plmnid`** *(string)*: Public Land Mobile Network Identifier.

    Examples:
    ```json
    "310-150"
    ```

    ```json
    "310-260"
    ```

  - <a id="properties/cellsig/properties/plmnname"></a>**`plmnname`** *(string)*: Public Land Mobile Network Name.

    Examples:
    ```json
    "Verizon"
    ```

    ```json
    "AT&T"
    ```

    ```json
    "T-Mobile"
    ```

- <a id="properties/datalink"></a>**`datalink`** *(object)*: Data link performance metrics. Cannot contain additional properties.
  - <a id="properties/datalink/properties/rtt"></a>**`rtt`** *(number)*: Round-trip time in milliseconds.

    Examples:
    ```json
    50
    ```

    ```json
    100
    ```

    ```json
    200
    ```

  - <a id="properties/datalink/properties/loss"></a>**`loss`** *(boolean)*: Packet loss flag.

    Examples:
    ```json
    true
    ```

    ```json
    false
    ```

- <a id="properties/gnss"></a>**`gnss`** *(object)*: GNSS constellation satellite counts. Cannot contain additional properties.
  - <a id="properties/gnss/properties/gps"></a>**`gps`** *(object)*: GPS constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/gps/properties/in_view"></a>**`in_view`** *(number)*: Number of GPS satellites in view.
    - <a id="properties/gnss/properties/gps/properties/used"></a>**`used`** *(number)*: Number of GPS satellites used in position fix.
  - <a id="properties/gnss/properties/glonass"></a>**`glonass`** *(object)*: GLONASS constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/glonass/properties/in_view"></a>**`in_view`** *(number)*: Number of GLONASS satellites in view.
    - <a id="properties/gnss/properties/glonass/properties/used"></a>**`used`** *(number)*: Number of GLONASS satellites used in position fix.
  - <a id="properties/gnss/properties/galileo"></a>**`galileo`** *(object)*: Galileo constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/galileo/properties/in_view"></a>**`in_view`** *(number)*: Number of Galileo satellites in view.
    - <a id="properties/gnss/properties/galileo/properties/used"></a>**`used`** *(number)*: Number of Galileo satellites used in position fix.
  - <a id="properties/gnss/properties/beidou"></a>**`beidou`** *(object)*: BeiDou constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/beidou/properties/in_view"></a>**`in_view`** *(number)*: Number of BeiDou satellites in view.
    - <a id="properties/gnss/properties/beidou/properties/used"></a>**`used`** *(number)*: Number of BeiDou satellites used in position fix.
  - <a id="properties/gnss/properties/qzss"></a>**`qzss`** *(object)*: QZSS constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/qzss/properties/in_view"></a>**`in_view`** *(number)*: Number of QZSS satellites in view.
    - <a id="properties/gnss/properties/qzss/properties/used"></a>**`used`** *(number)*: Number of QZSS satellites used in position fix.
  - <a id="properties/gnss/properties/irnss"></a>**`irnss`** *(object)*: IRNSS/NavIC constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/irnss/properties/in_view"></a>**`in_view`** *(number)*: Number of IRNSS/NavIC satellites in view.
    - <a id="properties/gnss/properties/irnss/properties/used"></a>**`used`** *(number)*: Number of IRNSS/NavIC satellites used in position fix.
  - <a id="properties/gnss/properties/sbas"></a>**`sbas`** *(object)*: SBAS constellation satellite counts. Cannot contain additional properties.
    - <a id="properties/gnss/properties/sbas/properties/in_view"></a>**`in_view`** *(number)*: Number of SBAS satellites in view.
    - <a id="properties/gnss/properties/sbas/properties/used"></a>**`used`** *(number)*: Number of SBAS satellites used in position fix.
- <a id="properties/metadata"></a>**`metadata`** *(object)*: Additional metadata.
