# `file.lua`
`file.lua` returns the module `FILE`.

## Local variables

### [type?] `fs = love.filesystem`

## Methods

### [multipleReturnTypes] `FILE.load(string name, string mode)`
Load a file from the file system.

string `name` is passed into `love.filesystem.newFile`.

string `mode` is optional, and it will automatically decide which mode when omitted. Possible `mode` values are:

| mode | behavior | auto select condition |
|------|----------|-----------------------|
| `luaon` | Load the file using `loadstring` function, then return the loaded object. Note that this might enable arbitrary code execution if an untrusted file is somehow injected into the file system. | file begins with `return{` |
| `json` | Parse the file as JSON, then return the object. | file begins and ends with a pair of `[ ]` or `{ }` |
| `string` | Returns the content of the file as a single string. | above checks failed |

### [multipleReturnTypes] `FILE.save([multipleTypes] data, string name, string mode)`
Save some data to a file on the file system.

`data` can be a table or any other type that can be used in `tostring`.

string `name` is the file name passed into `love.filesystem.newFile`.

string `mode` contains flags controlling the behavior of the function. Each flag is represented by presence or absence of a letter in the string; the order doesn't matter, and other characters are ignored.

- `l`: If the data is a table, use `TABLE.dump()` to convert the data to string. If the flag is absent, JSON will be used instead. Has no effect if the data is not table.
- `d`: Prevent overwriting a file with an existing identical file name. If the flag is absent, the existing file will be overwritten.

Returns true if saving success, or nothing if fail.

### void `FILE.clear(string path)`
Deletes a file.

### void `FILE.clear_s(string path)`
Recursively delete a directory.
