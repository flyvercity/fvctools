# JSON Schema

## Properties

- <a id="properties/origin"></a>**`origin`** *(string)*: Originating system.

  Examples:
  ```json
  "robinradar"
  ```

  ```json
  "csgroup"
  ```

  ```json
  "senhive"
  ```

- <a id="properties/time"></a>**`time`** *(object, required)*: Timestamp of the radar log entry. Cannot contain additional properties.
  - <a id="properties/time/properties/unix"></a>**`unix`** *(number, required)*: Unix timestamp in milliseconds.

    Examples:
    ```json
    1756033206882
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

  - <a id="properties/uaid/properties/IP"></a>**`IP`** *(string)*: IP address.

    Examples:
    ```json
    "192.168.1.100"
    ```

    ```json
    "10.0.0.5"
    ```

  - <a id="properties/uaid/properties/IMEI"></a>**`IMEI`** *(string)*: IMEI (International Mobile Equipment Identity) number.

    Examples:
    ```json
    "123456789012345"
    ```

    ```json
    "987654321098765"
    ```

  - <a id="properties/uaid/properties/IMSI"></a>**`IMSI`** *(string)*: IMSI (International Mobile Subscriber Identity) number.

    Examples:
    ```json
    "310150123456789"
    ```

    ```json
    "310260987654321"
    ```

- <a id="properties/pos"></a>**`pos`** *(object, required)*: Radar position information. Cannot contain additional properties.
  - <a id="properties/pos/properties/loc"></a>**`loc`** *(object, required)*: Polar coordinates for radar position. Cannot contain additional properties.
    - <a id="properties/pos/properties/loc/properties/bear"></a>**`bear`** *(number)*: Bearing angle in degrees clockwise from the true north.

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

    - <a id="properties/pos/properties/loc/properties/elev"></a>**`elev`** *(number)*: Elevation angle in degrees above horizon.

      Examples:
      ```json
      0.0
      ```

      ```json
      15.0
      ```

      ```json
      45.0
      ```

      ```json
      90.0
      ```

