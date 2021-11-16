# `font.lua`
`font.lua` returns the module `FONT`.

## Local variables

### [type?] `gc = love.graphics`

### function `set = love.graphics.setFont`

### array `fontCache`

### [type?] `currentFontSize`

## Methods
Weirdly enough, `FONT.set`, `FONT.get` and `FONT.reset` get initialized by one thing and then overwritten with another within `FONT.load`. Not sure what to make of that.

### void `FONT.set([type?] s)`

### [returnType?] `FONT.get([type?] s)`

### void `FONT.reset()`

### void `FONT.load([type?] mainFont, [type?] secFont)`
