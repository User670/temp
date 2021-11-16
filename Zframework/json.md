# `json.lua`
`json.lua` returns module `json`.

`json.lua` is originally by rxi, and was edited by MrZ.

# the `JSON` module
`init.lua` imports `json` as `JSON`, and overwrites the `encode` and `decode` methods to add error-handling.

## Methods

### string `JSON.encode([multipleTypes] val)`
Encode an object into JSON.

### [multipleReturnTypes] `JSON.decode(string str)`
Decode a JSON string into an object.
