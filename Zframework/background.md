# `background.lua`
`background.lua` returns the mudule `BG`.

## Local variables

### function `gc_clear=love.graphics.clear`

### dictionary `BGs`

### array `BGlist`

## Attributes

### string `BG.cur`

### string `BG.default`

### bool `BG.init`

### bool `BG.resize`

### (type?) `BG.update`
(`update` was initialized with NULL.)

### function `BG.draw`
(`draw` was initialized with the following function, using the reference `BGs.none.draw`:
```lua
function()
    gc_clear(0.08, 0.08, 0.084)
end
```
)

### function `BG.event`
Proxied by `BG.send`. Should use an expression that evaluates to `false` in an `if` statement if this is not used.

### (type?) `BG.discard`
(`discard` was initialized with NULL.)

## Methods

### void `BG.add([type?] name, [type?] bg)`

### (returnType?) `BG.getList()`

### void `BG.send(...)`
Proxy to `BG.event`, sending all arguments to that function if it exists.

### void `BG.setDefault(object bg)`

### (multipleReturnTypes) `BG.set(object background=BG.default)`
