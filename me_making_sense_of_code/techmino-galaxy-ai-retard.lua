-- https://github.com/26F-Studio/Techmino_Galaxy/blob/main/assets/ai/retard.lua
-- "Retard" AI, as of 2023-02-20
-- It's an actual retard based on its in-game performance, tbh

local retard={}


local function simulateDrop(field,cb,cx)
    -- I assume `cb` is like, a grid representation of the piece?
    local w=#cb[1] -- piece's width?
    local shapeBottom,fieldTop={},{}
    for x=1,w do
        local y=0
        while y+1<=#cb and not cb[y+1][x] do
            y=y+1 
        end
        shapeBottom[x]=y
        -- bottom outline of the piece?

        y=#field
        while y>0 and not field[y][cx+x-1] do
            y=y-1
        end
        fieldTop[x]=y
        -- top outline of the board??
    end
    local delta={}
    for i=1,w do
        delta[i]=fieldTop[i]-shapeBottom[i]
    end
    
    --[[
    Okay here's what I think what the delta thing is doing
    Each column's delta represents how low this column can tolerate the bottom
    of the piece to be, and the heighest toleration is where the block actually lands
    
      ()
    ()()
    ()   piece
    ----                    ()
                          ()()
      []          ()      ()[]____
      []        ()()        []
      []        ()____      []
    [][]        []          []
    [][] board  []  col 1   [] col 2
    ]]
    
    -- So, this returns the actual height the piece lands on,
    -- together with each column's toleration
    return math.max(unpack(delta))+1,delta
end

function retard.calculateFieldScore(field,cb,cy)
    local clear=0

    -- Clear filled lines
    for y=cy+#cb-1,cy,-1 do
        if field[y] then
            for x=1,10 do
                if not field[y][x] then
                    goto CONTINUE_notFull
                end
            end
            table.remove(field,y)
            clear=clear+1
            ::CONTINUE_notFull::
        end
    end

    -- Which boy can refuse PC?
    if #field==0 then
        return 1e99
        -- Seriously, aren't you supposed to return three values?
    end

    local rowB=0
    for y=1,#field do
        local cur=true
        for x=1,#field[1] do
            if cur~=field[y][x] then
                cur=field[y][x]
                rowB=rowB+1
            end
        end
        if cur==false then rowB=rowB+1 end
    end
    
    --[[
    Okay this loop above
    It seems to loop through each row, and count how many times this row's block "toggles"
    assuming phantom filled blocks outside of the matrix
    
      |                    |
    []|[][]  [][][]    [][]|[]
      |    ^ ^     ^   ^   |
    
    Effectively it counts each gap twice.
    ]]
    
    local colB=0
    for x=1,#field[1] do
        local cur=true
        for y=1,#field do
            if cur~=field[y][x] then
                cur=field[y][x]
                colB=colB+1
            end
        end
    end
    
    --[[
    Similar to the loop above, this loops thru each column
    assumes phantom filled block below the floor? Does the field array count bottom up?
    
      []
      []
        <
      []<
    -------
      []
    
    It counts each gap twice, and if the column is not the tallest on the field, also
    counts the empty space above the column once.
    ]]

    return clear,rowB,colB
end

local directions={'0','R','F','L'}
function retard.findPosition(field,shape)
    local best={
        score=-1e99,
        x=4,y=4,dir='0',
    }
    if not field[1] then
        -- TABLE.new(val, count) from Zenitha
        -- returns a new table that is `val` repeated `count` times
        field[1]=TABLE.new(false,10)
        -- Are ya sure it's a 10-wide board now?
    end
    local w=#field[1] --board width
    for d=1,4 do
        for cx=1,w-#shape[1]+1 do
            -- this loop goes through all
            
            -- TABLE.shift(org, depth) from Zenitha
            -- returns a copy of `org`, up to `depth` layers deep.
            local F=TABLE.shift(field,1)
            
            -- cy is height where piece lands,
            -- colH is array of "toleration" for each column, see comment in that function above
            local cy,colH=simulateDrop(F,shape,cx)
            local score=0
            
            -- idk what the `cy` is, but `clear` is how many rows are cleared,
            -- `rowB` is number of gaps on all rows times two,
            -- `colB` is number of gaps on all cols times two.
            -- Wonder why gaps on rows penalized so heavily.
            local clear,rowB,colB=retard.calculateFieldScore(field,shape,cy)
            -- Line worths 2 pts
            -- Horizontal gap worths 6 penalty
            -- Vertal gap worths 4 penalty, plus 2 for every column not flush with the top
            score=score+clear*2-rowB*3-colB*2
            -- The higher you place, the worse you score; 1 penalty per block from the floor
            score=score-cy
            -- When each column's "toleration" is the same, the piece fits the stack nicely
            -- Any difference and there is gap below
            -- Each gap worths 1.26 penalty
            local minH=math.min(unpack(colH))
            for i=1,#colH do
                score=score-(colH[i]-minH)*1.26
            end

            if score>best.score then
                best.x,best.y,best.dir=cx,cy,directions[d]
                best.score=score
            end
        end
        if d<4 then shape=TABLE.rotate(shape,'R') end
    end
    return best.x,best.y,best.dir
end

return retard

--[[
In summary,
Hard drop only, current piece considered only, no holding pieces.
clearing lines encouraged,
having unevenness in the stack heavily penalized,
having holes in the stack penalized,
landing the piece while creating holes or overhangs penalized.
]]
