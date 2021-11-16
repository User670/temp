# `gcExtend.lua`
`gcExtend.lua` returns the module `GC`, which provides additional simple graphics-drawing functions.

## Local variables

### [type?] `gc = love.graphics`

### function `setColor = love.graphics.setColor`

### function `printf = love.graphics.printf`

### function `draw = love.graphics.draw`

## Methods

### void `GC.mStr([type?] obj, [type?] x, [type?] y)`
MrZ: "Printf a string with 'center'"

### void `GC.simpX([type?] obj, [type?] x, [type?] y)`
MrZ: "Simply draw an obj with x=obj:getWidth()/2"

### void `GC.simpY([type?] obj, [type?] x, [type?] y)`
MrZ: "Simply draw an obj with y=obj:getWidth()/2" (*[sic]*, should be getHeight)

### void `GC.X([type?] obj, [type?] x, [type?] y, [type?] a, [type?] k)`
MrZ: "Draw an obj with x=obj:getWidth()/2"

### void `GC.Y([type?] obj, [type?] x, [type?] y, [type?] a, [type?] k)`
MrZ: "Draw an obj with y=obj:getWidth()/2" (*[sic]*, should be getHeight)

### void `GC.draw([type?] obj, [type?] x, [type?] y, [type?] a, [type?] k)`
MrZ: "Draw an obj with both middle X & Y"

### void `GC.outDraw([type?] obj, [type?] div, [type?] x, [type?] y, [type?] a, [type?] k)`

### void `GC.shadedPrint(string str, [type?] x, [type?] y, string mode, [type?] d, [type?] clr1, [type?] clr2)`

### void `GC.regularPolygon([type?] mode, [type?] x, [type?] y, [type?] R, [type?] segments, [type?] r, [type?] phase)`

### [returnType?] `GC.DO([type?] L)`
