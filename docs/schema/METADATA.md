# JSON Schema

## Properties

- <a id="properties/content"></a>**`content`**: Content type or array of content types.
  - **One of**
    - <a id="properties/content/oneOf/0"></a>*string*: Current file content descriptor. Must be one of: "flightlog", "radarlog", "fusion.replay", or "capture.message".
    - <a id="properties/content/oneOf/1"></a>*array*
      - <a id="properties/content/oneOf/1/items"></a>**Items** *(string)*: Current file content descriptor. Must be one of: "flightlog", "radarlog", "fusion.replay", or "capture.message".
- <a id="properties/source"></a>**`source`** *(string)*: Original data format. Must be one of: "airlink", "courageous", "csgroup", "nmea", "senhive", "robinradar", "safirmqtt", "fusion.replay", "artlog", "datcon", "agentfly", "gnettrack", "mqtt", "ulog", "fvcgen", or "capture.android".

  Examples:
  ```json
  "nmea"
  ```

  ```json
  "safirmqtt"
  ```

  ```json
  "fusion.replay"
  ```

- <a id="properties/origin"></a>**`origin`** *(string)*: Original file name or originating system.

  Examples:
  ```json
  "flight_data_20231201.log"
  ```

  ```json
  "radar_system_alpha"
  ```

- <a id="properties/polar_sensor"></a>**`polar_sensor`** *(object)*: Polar sensor configuration. Cannot contain additional properties.
  - <a id="properties/polar_sensor/properties/source"></a>**`source`** *(string)*: Source of the polar sensor. Must be one of: "nmea".

    Examples:
    ```json
    "nmea"
    ```

  - <a id="properties/polar_sensor/properties/origin"></a>**`origin`** *(string)*: Original file name or originating system.

    Examples:
    ```json
    "flight_data_20231201.log"
    ```

    ```json
    "radar_system_alpha"
    ```

  - <a id="properties/polar_sensor/properties/loc"></a>**`loc`** *(object, required)*: Geographic location of the polar sensor. Cannot contain additional properties.
    - <a id="properties/polar_sensor/properties/loc/properties/lat"></a>**`lat`** *(number, required)*: Latitude in WGS-84.

      Examples:
      ```json
      55.7558
      ```

      ```json
      -74.006
      ```

    - <a id="properties/polar_sensor/properties/loc/properties/lon"></a>**`lon`** *(number, required)*: Longitude in WGS-84.

      Examples:
      ```json
      37.6176
      ```

      ```json
      40.7128
      ```

    - <a id="properties/polar_sensor/properties/loc/properties/alt"></a>**`alt`** *(number)*: Ellipsoidal altitude.

      Examples:
      ```json
      100.5
      ```

      ```json
      250.0
      ```

    - <a id="properties/polar_sensor/properties/loc/properties/amsl"></a>**`amsl`** *(number)*: Altitude above mean sea level.

      Examples:
      ```json
      95.2
      ```

      ```json
      245.8
      ```

    - <a id="properties/polar_sensor/properties/loc/properties/height"></a>**`height`** *(number)*: Local height above ground.

      Examples:
      ```json
      10.5
      ```

      ```json
      25.0
      ```

    - <a id="properties/polar_sensor/properties/loc/properties/bear"></a>**`bear`** *(number)*: Bearing angle in degrees clockwise from the true north.

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

    - <a id="properties/polar_sensor/properties/loc/properties/gspeed"></a>**`gspeed`** *(number)*: Ground speed in meters per second.

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

- <a id="properties/cycle_length"></a>**`cycle_length`** *(number)*: Cycle length in milliseconds.

  Examples:
  ```json
  1000
  ```

