# `mathExtend.lua`
`mathExtend.lua` returns the module `MATH`. It contains additional math-related constants and functions.

## Variables
In addition to the following custom variables, every `math` variable can also be accessed as a property of `MATH`.

### double `MATH.tau = 2 * math.pi`

## Methods
In addition to the following custom functions, every `math` method can also be accessed as a method of `MATH`.

### int `MATH.sign(double a)`
Returns 1 if a is positive, 0 if a is 0, or -1 if a is negative.

### bool `MATH.roll(double chance)`
Returns true with a probability of `chance`, false with a probability of `1-chance`.

### [multipleReturnTypes] `MATH.coin([multipleTypes] a, [multipleTypes] b)`
a and b can be arbitrary types.

Returns a and b with equal chance (i.e. "flip a coin").
