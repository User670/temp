# `bgm.lua`
`bgm.lua` returns the module `BGM`.

## Local variables

### (table) `Sources={}`

### double `volume=1`

## Local functions

### async bool `task_fadeOut([type?] src)`
fade out audio over 0.67 seconds, then pause the audio, then return `true`.

### async bool `task_fadeIn([type?] src)`
fade in audio over 0.67 seconds, then return `true`.

### bool `check_curFadeOut([type?] task, [type?] code, [type?] src)`

## Attributes

### (multipleTypes?) `BGM.default`

### (type?) `BGM.play`

### (type?) `BGM.stop`

## Methods

### (returnType?) `BGM.getList()`

### int `BGM.getCount()`

### void `BGM.setDefault([type?] bgm)`
set `BGM.default` to parameter `bgm`.

### void `BGM.setChange(function func)`
set `BGM.onChange` to `func`.

### void `BGM.setVol(double v)`
set `volume` to v.

v should be between 0 and 1 (inclusive), or the program throws an assert error.

### void `BGM.init([type?] init)`
