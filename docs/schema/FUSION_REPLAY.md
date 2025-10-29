# JSON Schema

## Properties

- <a id="properties/event"></a>**`event`** *(string, required)*: Event type. Must be one of: "launch", "start", "stop", "input", "output", or "error".

  Examples:
  ```json
  "start"
  ```

  ```json
  "input"
  ```

  ```json
  "output"
  ```

- <a id="properties/cycle"></a>**`cycle`** *(number, required)*: Cycle number.

  Examples:
  ```json
  1
  ```

  ```json
  100
  ```

  ```json
  1000
  ```

- <a id="properties/origin"></a>**`origin`** *(string)*: Originating network or system.

  Examples:
  ```json
  "safesky"
  ```

- <a id="properties/message"></a>**`message`** *(object)*: Event message payload.
- <a id="properties/metadata"></a>**`metadata`** *(object)*: Event metadata.
