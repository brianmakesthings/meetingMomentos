import datetime

initialDate = datetime.date(2020,11,21)
delta = datetime.timedelta(days=14)
endDate= datetime.date(2021,4,30)

f = open("dates.txt", "w")

while (initialDate < endDate):
    date = f"{initialDate}"
    #exclude newline on last date
    if (initialDate + delta < endDate):
        date += "\n"
    print(date)
    f.write(date)
    initialDate += delta

f.close()