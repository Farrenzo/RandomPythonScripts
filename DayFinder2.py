#####
# This file uses Zeller's Rule/congruence for calculating the day
# of the week on a given date.
# https://en.wikipedia.org/wiki/Zeller%27s_congruence
# h = (q+ [13(m+1)/5] + K + [K/4] + [J/4] - 2J) mod 7
#
# h = Day of week   q = Date    m = Month
# K = Last 2 digits of year i.e. 1995 = 95 | (year mod 100)
# J = First 2 digits of year i.e. 1995 = 19 | (year/100)

from random import randint

months = [('January', 31, 11), ('February', 28, 12), ('March', 31, 1),
          ('April', 30, 2), ('May', 31, 3), ('June', 30, 4),
          ('July', 30, 5), ('August', 31, 6), ('September', 30, 7),
          ('October', 31, 8), ('November', 30, 9), ('December', 31, 10)]
    
days = [('Sunday'), ('Monday'), ('Tuesday'),
        ('Wednesday'), ('Thursday'), ('Friday'), ('Saturday')]

def GetDateFromInput():
    ValidYear = False
    while not ValidYear:
        try:
            year = int(input('Enter the year, four digits:'))
            if ((year < 1000) or (year > 9999)):
                print("You have entered %s which is an invalid year." %str(year))
            elif(year % 4 == 0):
                ValidYear = True
                print("You have entered %s which was a leap year." %str(year))
            else:
                ValidYear = True
                print("You have entered %s." %str(year))
        except ValueError:
            print("That's not a number.")

    ValidMonth = False
    while not ValidMonth:
        try:
            month = int(input('Enter the month number, either two digits or one:'))
            if month > len(months):
                print("You have entered %s which is an invalid month." %str(month))
            else:
                ValidMonth = True
                print("You have entered %s." %str(month))
        except ValueError:
            print("That's not a number.")

    LeapDate = False
    if((year % 4 == 0) and (month == 2)):
        LeapDate = True

    ValidDate = False
    while not ValidDate:
        try:
            date = int(input('Enter the date number, either two digits or one:'))
            if((LeapDate == True) and (date <= 29)):
                ValidDate = True
                print("You have entered %s." %str(int(date)))
            elif((LeapDate == False) and (date <= months[month-1][1])):
                ValidDate = True
                print("You have entered %s." %str(int(date)))
            elif((LeapDate == True) and (date >= 29)):
                print(r'%s of %s was a leap year and had %s days max.' %(months[month-1][0], str(year), 29))
            elif((LeapDate == False) and (date >= months[month-1][1])):
                print(r'%s of %s had %s days max.' %(months[month-1][0], str(year), months[month-1][1]))
        except ValueError:
            print("That's not a number.")

    EnteredDate = (month, date, year)
    return EnteredDate

EnteredDateM = GetDateFromInput()[0]
EnteredDateD = GetDateFromInput()[1]
EnteredDateY = GetDateFromInput()[2]

def GenerateRandomDate():
    month = randint(1, 12)
    year = randint(1700, 2016)

    #Don't give just any date to any month,
    #e.g. 31st of November doesn't exist.
    if((year % 4 == 0) and (month == 2)):
        date = randint(1, 29)
    elif((year % 4 != 0) and (month == 2)):
        date = randint(1, 28)
    else:
        date = randint(1, months[month-1][1])

    randomDate = (month, date, year)
    return randomDate

RandomDateM = GenerateRandomDate()[0]
RandomDateD = GenerateRandomDate()[1]
RandomDateY = GenerateRandomDate()[2]

def DetermineDay(q, m, y):
    y1=y if m > 2 else y - 1
    J=int(str(y1)[:2])
    K=int(str(y1)[-2:])
    h= ((q + int(float((13 * m-1)/5)) + K + int(float((K/4))) + int(float((J/4))) - int(float((2*J)))) % 7)

    return h

def GetWrittenDate(d, m, y):
    #Sunday the 12th of June, 2021.
    def ord(n):
        return str(n)+("th" if 4 <= n % 100 <= 20 else {1:"st", 2:"nd", 3:"rd"}.get(n%10, "th"))

    written = ("%s the %s of %s, %s" %(days[DetermineDay(d,m,y)], ord(d), months[m][0], y))
    
    return written

def run():
    print("Entered Date")
    print("%s/%s/%s \n\n" %(str(EnteredDateM), str(EnteredDateD), str(EnteredDateY)))
    print("Written date from your input")
    print(GetWrittenDate(EnteredDateD, EnteredDateM, EnteredDateY))
    print(" ")
    print("Randomly generated Date")
    print("%s/%s/%s" %(str(RandomDateM), str(RandomDateD), str(RandomDateY)))
    print("Written date from randomly generated Date")
    print(GetWrittenDate(RandomDateD, RandomDateM, RandomDateY))
    print(" ")

run()