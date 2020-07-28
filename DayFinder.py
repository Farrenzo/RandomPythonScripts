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

    return (year, month, date)

RandomDate = GenerateRandomDate()
print("\nRandomly generated Date \n")
print("%s/%s/%s \n" %(str(RandomDate[1]), str(RandomDate[2]), str(RandomDate[0])))

def GetWrittenDate(y, m, d):
    def DetermineDay(y,m,q):
        y=y if m > 2 else y - 1
        mi=(months[m-1][2])    
        fy=int(str(y)[:2])
        ly=int(str(y)[-2:])
        h = ((q + int(float((13 * mi-1)/5)) + ly + int(float((ly/4))) + int(float((fy/4))) - int(float((2*fy)))) % 7)

        return h

    #Sunday the 12th of June, 2021.
    def ord(n):
        return str(n)+("th" if 4 <= n % 100 <= 20 else {1:"st", 2:"nd", 3:"rd"}.get(n%10, "th"))

    written = ("%s the %s of %s, %s" %(days[DetermineDay(y,m,d)], ord(d), months[m-1][0], y))
    return written

print("Written date from randomly generated Date \n")
print(GetWrittenDate(RandomDate[0], RandomDate[1], RandomDate[2]))
print(" ")

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

    return (year, month, date)

EnteredDate = GetDateFromInput()

print("Entered Date")
print("%s/%s/%s \n\n" %(str(EnteredDate[1]), str(EnteredDate[2]), str(EnteredDate[0])))
print("Written date from your input")
print(GetWrittenDate(EnteredDate[0], EnteredDate[1], EnteredDate[2]))
