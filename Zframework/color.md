# `color.lua`
`color.lua` returns the module `COLOR`. It provides color values, as well as functions that generate random or dynamic colors.

## Local variables

### function `abs = math.abs`

## Local functions

### double, double, double, double `hsv(double h, double s, double v, double a)`
Converts HSVA to RGBA.

Each parameter is a decimal between 0 and 1, inclusive.

***Returns 4 numbers, not a 4-element array.***

## Attributes

### Colors
`COLOR.[color name]` is a 4-element array in RGBA format.

## Methods

### double, double, double, double `COLOR.hsv(double h, double s, double v, double a)`
The same as the local function `hsv`.

### array `COLOR.random_norm()`
returns a random 4-number array (RGBA) from a list of normal colors.

### array `COLOR.random_bright()`
returns a random 4-number array (RGBA) from a list of bright colors.

### array `COLOR.random_dark()`
returns a random 4-number array (RGBA) from a list of dark colors.

### array `COLOR.rainbow(double phase, double a)`
returns ***4 numbers (not a 4-number array)*** (RGBA) based on the phase.

Phase is a number passed into a `sin` function, thus 2\*pi is one cycle.

### array `COLOR.rainbow_light(double phase, double a)`
returns ***4 numbers (not a 4-number array)*** (RGBA) based on the phase.

Phase is a number passed into a `sin` function, thus 2\*pi is one cycle.

### array `COLOR.rainbow_dark(double phase, double a)`
returns a ***4 numbers (not a 4-number array)*** (RGBA) based on the phase.

Phase is a number passed into a `sin` function, thus 2\*pi is one cycle.

### array `COLOR.rainbow_gray(double phase, double a)`
returns a 4-number array (RGBA) based on the phase.

Phase is a number passed into a `sin` function, thus 2\*pi is one cycle.
