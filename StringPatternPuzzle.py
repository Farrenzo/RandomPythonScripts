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
            yield (i - (pl-1), i - (pl-(tl)), i - 1, i, txt[i - (pl-1):i + 1])

puzzlebox = 'C16111AA111BB117AA111311BB111111AA111BB111111AA11D'
for a,b,c,d,e in advanced_state_machinery(puzzlebox, 7, 2, 3):
    print(a,b,c,d,e)

print('\n')

puzzlebox2 = 'C16111AA1111BB1117AA1111BB111111AA4111BB111111AA11D'
for a,b,c,d,e in advanced_state_machinery(puzzlebox2, 8, 2, 4):
    print(a,b,c,d,e)