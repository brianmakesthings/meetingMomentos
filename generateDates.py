import datetime

initialDate = datetime.date(2020,11,21)
delta = datetime.timedelta(days=14)
endDate= datetime.date(2021,3,31)

while (initialDate < endDate):
    print(initialDate)
    initialDate += delta