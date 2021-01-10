import math, datetime
from datetime import datetime, timedelta

# I made the below tuples because datetime python starts it's ID's with a zero.
# I do not want any ID to begin with a zero as my database logic uses zero as a
# null function. You may not need them if you do have zero as the first unique index.
wDays = [
            [('Monday',   '01')],
            [('Tuesday',  '02')],
            [('Wednesday','03')],
            [('Thursday', '04')],
            [('Friday',   '05')],
            [('Saturday', '06')],
            [('Sunday',   '07')],
        ]

tIntervals = [
                ['00:00:00', '01', '01'],['00:15:00', '01', '01'],['00:30:00', '01', '02'],['00:45:00', '01', '02'],
                ['01:00:00', '02', '03'],['01:15:00', '02', '03'],['01:30:00', '02', '04'],['01:45:00', '02', '04'],
                ['02:00:00', '03', '05'],['02:15:00', '03', '05'],['02:30:00', '03', '06'],['02:45:00', '03', '06'],
                ['03:00:00', '04', '07'],['03:15:00', '04', '07'],['03:30:00', '04', '08'],['03:45:00', '04', '08'],
                ['04:00:00', '05', '09'],['04:15:00', '05', '09'],['04:30:00', '05', '10'],['04:45:00', '05', '10'],
                ['05:00:00', '06', '11'],['05:15:00', '06', '11'],['05:30:00', '06', '12'],['05:45:00', '06', '12'],
                ['06:00:00', '07', '13'],['06:15:00', '07', '13'],['06:30:00', '07', '14'],['06:45:00', '07', '14'],
                ['07:00:00', '08', '15'],['07:15:00', '08', '15'],['07:30:00', '08', '16'],['07:45:00', '08', '16'],
                ['08:00:00', '09', '17'],['08:15:00', '09', '17'],['08:30:00', '09', '18'],['08:45:00', '09', '18'],
                ['09:00:00', '10', '19'],['09:15:00', '10', '19'],['09:30:00', '10', '20'],['09:45:00', '10', '20'],
                ['10:00:00', '11', '21'],['10:15:00', '11', '21'],['10:30:00', '11', '22'],['10:45:00', '11', '22'],
                ['11:00:00', '12', '23'],['11:15:00', '12', '23'],['11:30:00', '12', '24'],['11:45:00', '12', '24'],
                ['12:00:00', '13', '25'],['12:15:00', '13', '25'],['12:30:00', '13', '26'],['12:45:00', '13', '26'],
                ['13:00:00', '14', '27'],['13:15:00', '14', '27'],['13:30:00', '14', '28'],['13:45:00', '14', '28'],
                ['14:00:00', '15', '29'],['14:15:00', '15', '29'],['14:30:00', '15', '30'],['14:45:00', '15', '30'],
                ['15:00:00', '16', '31'],['15:15:00', '16', '31'],['15:30:00', '16', '32'],['15:45:00', '16', '32'],
                ['16:00:00', '17', '33'],['16:15:00', '17', '33'],['16:30:00', '17', '34'],['16:45:00', '17', '34'],
                ['17:00:00', '18', '35'],['17:15:00', '18', '35'],['17:30:00', '18', '36'],['17:45:00', '18', '36'],
                ['18:00:00', '19', '37'],['18:15:00', '19', '37'],['18:30:00', '19', '38'],['18:45:00', '19', '38'],
                ['19:00:00', '20', '39'],['19:15:00', '20', '39'],['19:30:00', '20', '40'],['19:45:00', '20', '40'],
                ['20:00:00', '21', '41'],['20:15:00', '21', '41'],['20:30:00', '21', '42'],['20:45:00', '21', '42'],
                ['21:00:00', '22', '43'],['21:15:00', '22', '43'],['21:30:00', '22', '44'],['21:45:00', '22', '44'],
                ['22:00:00', '23', '45'],['22:15:00', '23', '45'],['22:30:00', '23', '46'],['22:45:00', '23', '46'],
                ['23:00:00', '24', '47'],['23:15:00', '24', '47'],['23:30:00', '24', '48'],['23:45:00', '24', '48']
             ]
wd = dict(map(lambda ds:ds[0], wDays))
def csvCreator(r):
    TheCSVFilePath = 'X:/cal.csv'
    with open(TheCSVFilePath, 'a', newline='', ) as TheCSV:
        TheCSV.write("%s\n" % r)

h = 'CalDate_ID,Date_ID,Day_ID,Interval_ID,Week_Num,Date,Day,Interval,Interval_60,Interval_30,oID'
csvCreator(h)
# Start date
sDate = datetime.strptime('2020-01-01', '%Y-%m-%d')
# End date
eDate = datetime.strptime('2020-03-31', '%Y-%m-%d')

# Total days x 96 = total number of rows to expect. 96 = 15 min increments in one day.
iDate = sDate
tDays = (eDate - sDate)
tRows = (tDays.days * 96) + 1
dID = 1
n = 1

while n < tRows:

    r = []    
    CalDate_ID = n
    Date_ID = math.floor(n/96) + 1
    Day_ID = int(wd[datetime.strftime(iDate, '%A')])
    iID = [x for x,y in enumerate(tIntervals) if y[0] == datetime.strftime(iDate, '%H:%M:%S')]
    Interval_ID = int(iID[0]) + 1
    Week_Num = int(datetime.strftime(iDate, '%W')) + 1
    Date = datetime.strftime(iDate, '%Y-%m-%d')
    Day = datetime.strftime(iDate, '%A')
    Interval = datetime.strftime(iDate, '%H:%M:%S')
    i60 = str([i for i in tIntervals if i[0] == datetime.strftime(iDate, '%H:%M:%S')])
    Interval_60 = int(i60[16:17])
    Interval_30 = int(i60[22:23])
    oID = 0 #Always going to be zero, you change it according to your occasion table data.
    r = [CalDate_ID, Date_ID, Day_ID, Interval_ID, Week_Num, Date, Day, Interval, Interval_60, Interval_30, oID]
    rs = ('%d,%d,%d,%d,%d,%s,%s,%s,%d,%d,%d' %(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))
    csvCreator(rs)
    iDate = iDate + timedelta(minutes=15)
    n += 1
