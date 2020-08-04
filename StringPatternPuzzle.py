#Find when 'x' letters are seperated by 'x' numbers
#Example 1:
#'C11111AA111BB111AA111111BB111111AA111BB111111AA11D'
##OUTPUT SHOULD BE:
#positions = [6,7,11,12] [11,12,16,17] [32,33,37,38]
#Example 2:
#'C16111AA1111BB1117AA1111BB111111AA4111BB111111AA11D'
##OUTPUT SHOULD BE:
#positions = [06, 07, 12, 13, AA1111BB], [12, 13, 18, 19, BB1117AA],
#            [18, 19, 24, 25, AA1111BB], [32, 33, 38, 39, AA4111BB]

#txt = sample string
#pl = pattern length
#tl = total letters required outside
#td = number of digits seperating letters
def advanced_state_machinery(txt, pl, tl, td):

    def firstandlast(pl, tl):
        x = 0
        oc = []
  
        while x < tl:
            z = pl - (x + 1)
            oc.insert(x, z)
            x += 1

        x = 0
        for i in range(tl):
            z = x
            oc.insert(x, z)    
            x += 1

        return oc

    state = 0

    for i, ch in enumerate(txt): #i = index position & ch = character
        next_state = tl if state == tl else 0
        fn_check = str.isalpha if state in firstandlast(pl, tl) else str.isdigit
        state = state + 1 if fn_check(ch) else next_state
        if state > pl - 1:
            state = tl
            lst = 1 if tl >= 2 else tl - 1
            if tl > 1:
                yield ("Start positions: %s & %s.\nEnd positions: %s & %s\nFound at %s\n" %(i - (pl-1), i - (pl-(tl)), i - lst, i, txt[i - (pl-1):i + lst]))
            else:
                yield ("Start position: %s.\nEnd position: %s.\nFound at %s\n" %(i - (pl-1), i, txt[i - (pl-1):i + lst]))

puzzlebox = 'C16111AA111BB117AA111311BB111111AA111BB111111AA11D'
for m in advanced_state_machinery(puzzlebox, 7, 2, 3):
    print(m)

puzzlebox = 'C16111AA1111BB1117AA1111BB111111AA4111BB111111AA11D'
for m in advanced_state_machinery(puzzlebox, 8, 2, 4):
    print(m)

puzzlebox = 'C1611111A1111B11111C6A21116A1111111B11111111A411BB81111111AA1111DASDR111'
for m in advanced_state_machinery(puzzlebox, 9, 1, 5):
    print(m)
