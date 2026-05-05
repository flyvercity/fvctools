# JSON Schema

*Messages captured from MQTT topics (other sources may be added in the future)*

## Properties

- <a id="properties/mqtt"></a>**`mqtt`** *(object, required)*: MQTT Metadata. Cannot contain additional properties.
  - <a id="properties/mqtt/properties/time"></a>**`time`** *(object, required)*: MQTT message timestamp. Cannot contain additional properties.
    - <a id="properties/mqtt/properties/time/properties/unix"></a>**`unix`** *(number, required)*: Unix timestamp in milliseconds.

      Examples:
      ```json
      1756033206882
      ```

    - <a id="properties/mqtt/properties/time/properties/rx"></a>**`rx`** *(number)*: Reception timestamp in milliseconds (when data was received by ground system).

      Examples:
      ```json
      1756033207094
      ```

    - <a id="properties/mqtt/properties/time/properties/original"></a>**`original`** *(string)*: Original timestamp string.

      Examples:
      ```json
      "2025-01-01 12:00:00"
      ```

      ```json
      "2025-01-01 12:00:00.123"
      ```

  - <a id="properties/mqtt/properties/topic"></a>**`topic`** *(string, required)*: MQTT topic.

    Examples:
    ```json
    "/aircraft/position"
    ```

    ```json
    "/radar/track"
    ```

    ```json
    "/system/status"
    ```

