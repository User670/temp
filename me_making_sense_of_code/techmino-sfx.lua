-- 26F-Studio/Techmino:main/Zframework/sfx.lua

local type,rem=type,table.remove

local sfxList={}
local packSetting={}
local Sources={}
local volume=1
local stereo=1

local noteName={
    C=1,c=1,
    D=3,d=3,
    E=5,e=5,
    F=6,f=6,
    G=8,g=8,
    A=10,a=10,
    B=12,b=12,
}
local function _getTuneHeight(tune)
    -- seems like it expects a string that
    --   - has octave at the last char as number...
    --   - has note letter (case insensitive) at the 1st char...
    --   - optionally, "s"/"#" for sharp, "f"/"b" for flat, at 2nd char
    -- returns... midi pitch minus 24. curious
    local octave=tonumber(tune:sub(-1,-1))
    if octave then
        local tuneHeight=noteName[tune:sub(1,1)]
        if tuneHeight then
            tuneHeight=tuneHeight+(octave-1)*12
            -- C4 will return 3*12=36, which is 24 lower than midi?
            local s=tune:sub(2,2)
            if s=='s'or s=='#'then
                tuneHeight=tuneHeight+1
            elseif s=='f'or s=='b'then
                tuneHeight=tuneHeight-1
            end
            return tuneHeight
        end
    end
end
-- A few thoughts with it
-- 1. position of the #/b. C# would be natural in reading order, but #C is probably also something
--    one may write (sheet music order where sharps and flats go before a note, or Chinese reading
--    order).
-- 2. lack of support of double sharp (x) and double flat (bb). If you read off a weird sheet music
--    you might run into those double sharps and double flats.
-- 3. return value.
--
-- By the way, if #/b is implemented to ignore position, then note name will have to consider case,
-- because "f"/"b" for flat are both lowercase note names.

local SFX={}

function SFX.init(list)
    assert(type(list)=='table',"Initialize SFX lib with a list of filenames!")
    for i=1,#list do table.insert(sfxList,list[i])end
end
function SFX.load(path)
    local c=0
    for i=1,#sfxList do
        local fullPath=path..sfxList[i]..'.ogg'
        if love.filesystem.getInfo(fullPath)then
            Sources[sfxList[i]]={love.audio.newSource(fullPath,'static')}
            c=c+1
        else
            LOG("No SFX: "..sfxList[i]..'.ogg',.1)
        end
    end
    LOG(c.."/"..#sfxList.." SFX files loaded")
end
function SFX.loadSample(pack)
    assert(type(pack)=='table',"Usage: SFX.loadsample([table])")
    assert(pack.name,"No field: name")
    assert(pack.path,"No field: path")
    packSetting[pack.name]={
        base=(_getTuneHeight(pack.base)or 37)-1,
    }
    local num=1
    while love.filesystem.getInfo(pack.path..'/'..num..'.ogg')do
        Sources[pack.name..num]={love.audio.newSource(pack.path..'/'..num..'.ogg','static')}
        num=num+1
    end
    LOG((num-1).." "..pack.name.." samples loaded")
end

function SFX.getCount()
    return #sfxList
end
function SFX.setVol(v)
    assert(type(v)=='number'and v>=0 and v<=1)
    volume=v
end
function SFX.setStereo(v)
    assert(type(v)=='number'and v>=0 and v<=1)
    stereo=v
end

function SFX.playSample(pack,...)--vol-2, sampSet1, vol-3, sampSet2, vol-1
    if ... then
        local arg={...}
        -- arg:list
        local vol
        -- vol:null
        if type(arg[#arg])=='number' then
            vol=rem(arg)
            -- arg's last element, which is a number, removed
            -- vol:number
        end
        for i=1,#arg do
            if type(arg[i])=='number' then
                -- I think there is a bug here?? Or at least unintuitive implementation
                vol=arg[i]
            else
                local tune=arg[i]
                tune=_getTuneHeight(tune)-packSetting[pack].base
                SFX.play(pack..tune,vol)
            end
        end
    end
end
