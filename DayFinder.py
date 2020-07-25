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
    
OrdinalSuffixes = [('st'),('nd'),('rd'),('th')]

month = 6
date = 3
year = 1967

def DetermineDay(m=(months[month-1][2]), q=date, y=year if month > 2 else year - 1):
    fy=int(str(y)[:2])
    ly=int(str(y)[-2:])
    h = ((q + int(float((13 * m-1)/5)) + ly + int(float((ly/4))) + int(float((fy/4))) - int(float((2*fy)))) % 7)

    return h

print(days[DetermineDay()])

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

    randomDate = ("%s/%s/%s" %(str(month), str(date), str(year)))
    return randomDate

print(GenerateRandomDate())

def GetWrittenDate(m=month-1, d=date, y=year):
    #Sunday the 12th of June, 2021.
    def ord(n):
        return str(n)+("th" if 4 <= n % 100 <= 20 else {1:"st", 2:"nd", 3:"rd"}.get(n%10, "th"))

    written = ("%s the %s of %s, %s" %(days[DetermineDay()], ord(d), months[m][0], y))
    
    return written

print(GetWrittenDate())