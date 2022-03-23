## Working with date times.
from datetime import datetime, timezone
## https://docs.python.org/3/library/datetime.html
import pytz
## https://pythonhosted.org/pytz/

## String to date time object
string_format = ['%Y-%m-%d %H:%M %p', '%Y-%m-%dT%H:%M:%S.%fZ']
d = ['2021-12-15 8:00 AM','2022-03-17T20:09:20.106Z']
d_o = [datetime.strptime(d[0], string_format[0]), datetime.strptime(d[1], string_format[1])]

## Date time object to string
date_object = datetime.today()
date_string = datetime.strftime(date_object, '%Y-%m-%d %H:%M %p')

## Datetime to different timezone
est = pytz.timezone('EST5EDT') ## US/Eastern Both work
utc = pytz.timezone('UTC')

## Run the below code to add timezone attribute other than UTC. UTC is easier to do.
x = d_o[0].replace(tzinfo=est)
print('EST time is', x, x.tzinfo)

## Easier way to declare UTC time.
x = pytz.utc.localize(d_o[0])
print('UTC winter time is', x, x.tzinfo)
y = pytz.utc.localize(d_o[1])
print('UTC summer time is', y, y.tzinfo)

## Convert UTC time to EST time accounting for daylight savings time.
print('EST time is', x.astimezone(est)) ## OUTPUT: 2021-12-15 03:00:00-05:00          (5 Hours behind)
print('EST time is', y.astimezone(est)) ## OUTPUT: 2022-03-17 16:09:20.106000-04:00   (4 Hours behind)

import pandas as pd

utc_dates = ['2022-03-13T11:35:39.995Z',
             '2022-03-13T12:35:50.887Z',
             '2022-03-13T12:53:46.004Z',
             '2022-03-13T15:14:58.74Z',
             '2022-03-13T16:00:09.168Z',
             '2022-03-13T17:01:22.061Z',
             '2022-03-13T19:09:14.082Z',
             '2022-03-13T19:26:42.385Z',
             '2022-03-13T19:37:10.561Z',
             '2022-03-13T19:38:12.772Z',
             '2022-03-13T19:51:37.856Z',
             '2022-03-13T20:06:32.791Z',
             '2022-03-13T20:14:45.151Z',
             '2022-12-13T20:14:45.151Z']

df = pd.DataFrame(utc_dates, columns = ['UTC_DATES'])
# print(df['UTC_DATES'].dtypes) ## OUTPUT: Object = pandas doesn't know these are dates.
df['UTC_DATES'] = pd.to_datetime(df['UTC_DATES'], format = string_format[1], errors ='raise')
# print(df['UTC_DATES'].dtypes) ## OUTPUT: datetime64[ns] Conversion to datetime successful.
# print(df['UTC_DATES'].dt.tz)  ## OUTPUT: None = no timezone is declared.
df['UTC_DATES'] = df['UTC_DATES'].dt.tz_localize(tz='UTC') ## Declare the timezone is UTC.
df['EST_TIMESTAMP'] = df['UTC_DATES'].dt.tz_convert('US/Eastern')
# print(df)

## Faster way of declaring timezone if you know it is UTC.
df1 = pd.DataFrame(utc_dates, columns = ['UTC_DATES'])
df1['UTC_DATES'] = pd.to_datetime(df1['UTC_DATES'], format = string_format[1], errors ='raise', utc=True)
print(df1['UTC_DATES'].dtypes) ## OUTPUT: datetime64[ns, UTC] Conversion to datetime successful.
print(df1['UTC_DATES'].dt.tz)  ## OUTPUT: UTC was is declared inline.
df1['EST_TIMESTAMP'] = df1['UTC_DATES'].dt.tz_convert('US/Eastern')
print(df1)
