-- 26F-Studio/Techmino:main/Zframework/sfx.lua

function SFX.playSample(pack,...)--vol-2, sampSet1, vol-3, sampSet2, vol-1
    if ... then
        local arg={...}
        local vol
        if type(arg[#arg])=='number'then vol=rem(arg)end
        for i=1,#arg do
            if type(arg[i])=='number'then
                vol=arg[i]
            else
                local tune=arg[i]
                tune=_getTuneHeight(tune)-packSetting[pack].base
                SFX.play(pack..tune,vol)
            end
        end
    end
end
