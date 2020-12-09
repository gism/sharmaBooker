# -*- coding: utf-8 -*-
import sys 
import time
import datetime
# from datetime import datetime
# from datetime import date
import urllib.request
from http.cookiejar import CookieJar
import json
import re

from sharmaBooker_config import *


url = 'https://www.sharmaclimbingbcn.com/mi-cuenta/'
loginUrl = 'https://sharmaclimbingbarcelona.syltek.com/customer/login'
reservationsUrl = 'https://sharmaclimbingbarcelona.syltek.com/customerzone/reservations'
doReservationUrl = 'https://sharmaclimbingbarcelona.syltek.com/booking/index'
summitReservationUrl = 'https://sharmaclimbingbarcelona.syltek.com/customerZone/newReservationPost'
rootUrl = 'https://sharmaclimbingbarcelona.syltek.com'
urlGetTimePeriod = 'https://sharmaclimbingbarcelona.syltek.com/booking/getTimePeriod' 


def printD(t):
    if(DEBUG):
        print(t)

def printCurrentReservations():

    # Check current reservations:
    
    response = opener.open(reservationsUrl)
    mystr = response.read().decode(response.info().get_param('charset') or 'utf-8')
    
    # Uncomment for debuging
    # text_file = open("check_pre_booking.txt", "w")
    # text_file.write(mystr)
    # text_file.close()
    
    pastDaysRegEx = re.finditer('<div class=\"dateHeader c-card__day\">[\s\n\r]*([\w,\d\s]+)<\/div>[\s\n\r]*<div class=\"c-card__hour c-card__text\">[\s\n\r]*([\d:]+),[\n\r\w\/\s]+BOOKING (\d+)', mystr, re.MULTILINE)
    for match in pastDaysRegEx:
        day_r = match.group(1).strip()
        hour_r = match.group(2).strip()
        booking_r = match.group(3).strip()
        print("past: " + day_r + " at " + hour_r + " Booking ID: " + booking_r)
    
    print("")
    
    nextDaysRegEx = re.finditer('<div class=\"dateHeader c-card__day fecha\">[\s\n\r]*([\w,\d\s]+)<\/div>[\s\n\r]*<div class=\"c-card__hour c-card__text\">[\s\n\r]*([\d:]+),[\n\r\w\/\s]+RESERVA (\d+)', mystr, re.MULTILINE)
    for match in nextDaysRegEx:
        day_r = match.group(1).strip()
        hour_r = match.group(2).strip()
        booking_r = match.group(3).strip()
        print("next: " + day_r + " at " + hour_r + " Booking ID: " + booking_r)


def doReservation(dateBooking, hour):
    
    # Generar el timestamp per el form POST
    dt_obj = datetime.datetime.now()
    millisec = dt_obj.timestamp() * 1000
    milsFrom1970 = int(millisec)
    
    
    postGetTimePeriod = {'sDate' : dateBooking,
                         'type' : '58',
                         'checktype' : 'false'}
    
    
    postGetTimePeriod["_sclDisableCache"] = milsFrom1970
    # printD("PAYLOAD:")
    # printD(postGetTimePeriod)
    
    postData = urllib.parse.urlencode(postGetTimePeriod)
    postData = postData.encode('utf-8')
    
    response = opener.open(urlGetTimePeriod, postData)
    
    mystr = response.read().decode(response.info().get_param('charset') or 'utf-8')
    corr_str = re.sub(r'new\sDate\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)', r'"\1-\2-\3 \4h\5m\6s"', mystr)
    
    
    myJson = json.loads(corr_str)
    bookingBlocks = myJson["bookingPeriods"]
    
    days = []
    daysCount = {}
    for block in bookingBlocks:
        days.append(block["start"]['DateTime'])
        if(daysCount.get(block["start"]['DateTime']) == None):
            daysCount[block["start"]['DateTime']] = 1
        else:
            daysCount[block["start"]['DateTime']] = daysCount.get(block["start"]['DateTime']) + 1
    
    
    days = list(dict.fromkeys(days))
    printD("\nAvailable hours for " + str(dateBooking) + ":")
    for d in days:
        printD(d)
    
    
    printD("\n:::::::::::::::::::::::::::::::::::::::::::::::::::")
    printD("")
    
    postBooking = {'date': dateBooking,
                   'type': '58',
                   'hour': hour,
                   'duration': '120'}
    
    printD("Booking POST payload:")
    printD(postBooking)
    
    postData = urllib.parse.urlencode(postBooking)
    postData = postData.encode('utf-8')
    response = opener.open(doReservationUrl, postData)
    
    mystr = response.read().decode(response.info().get_param('charset') or 'utf-8')
    
    
    
    date_p = re.search('<input type=\"hidden\" name=\"date\" value=\"([\d\s\/:]+)\" \/>', mystr)
    if (not date_p):
        print("\nERROR: Not posible to book for: " + str(dateBooking) + " at " + hour + "\n")
        return
    date_p = date_p.group(1)
    # print("DATE: " + date_p)
    
    idResource = re.search('<input type=\"hidden\" name=\"idResource\" value=\"([\d]+)\" />', mystr)
    idResource = idResource.group(1)
    # print("idResource: " + idResource)
    
    idReservation = re.search('<input type=\"hidden\" name=\"idReservation\" value=\"([\d]+)\" />', mystr)
    idReservation = idReservation.group(1)
    # print("idReservation: " + idReservation)
    
    duration = re.search('<input type=\"hidden\" name=\"duration\" value=\"([\d]+)\" />', mystr)
    duration = duration.group(1)
    # print("Duration: " + duration)
    
    freeSpots = re.search("Hay ([\d]+) Reservas Escalada disponibles", mystr)
    printD("There are: " + freeSpots.group(1) + " available bookings")
    
    
    # date: 06/07/2020 17:15:00
    # idResource: 1513
    # idReservation: 18478
    # paymentPending: 
    # duration: 120
    
    dateBooking = "07/07/2020 17:15:00"
    
    postSummitBooking = {'date': dateBooking,
                         'idResource': idResource,
                         'idReservation': idReservation,
                         'paymentPending' : '',
                         'duration': duration}
    
    postData = urllib.parse.urlencode(postSummitBooking)
    postData = postData.encode('utf-8')
    response = opener.open(summitReservationUrl, postData)
    
    mystr = response.read().decode(response.info().get_param('charset') or 'utf-8')
    
    # text_file = open("Output_summit.txt", "w")
    # text_file.write(mystr)
    # text_file.close()
    
    
    
    sItems = re.search('<input type=\"hidden\" id=\"sItems\" name=\"sItems\" value=\"([\w\d]+)\"\/>', mystr)
    sItems = sItems.group(1)
    # print("sItems: " + sItems)
    
    callback = re.search('<input type=\"hidden\" id=\"callback\" name=\"callback\" value=\"([\w\d=\/\?]+)\"\/>', mystr)
    callback = callback.group(1)
    # print("callback: " + callback)
    
    idPaymentMethod = re.search('onclick=\"customerTpv\.pay\(([\d]+), [\w]+\)\">Bono Prepago', mystr)
    idPaymentMethod = idPaymentMethod.group(1)
    # print("idPaymentMethod: " + idPaymentMethod)
    
    # print("Current URL: " + response.geturl() )
    
    postSummitPayment = {'sItems': sItems,
                         'callback': callback,
                         'idPaymentMethod': idPaymentMethod}
    
    postData = urllib.parse.urlencode(postSummitPayment)
    postData = postData.encode('utf-8')
    response = opener.open(response.geturl(), postData)
    
    mystr = response.read().decode(response.info().get_param('charset') or 'utf-8')
    
    # Uncomment for debugging
    # text_file = open("Output_summit_payment.txt", "w")
    # text_file.write(mystr)
    # text_file.close()


cookie_jar = CookieJar()
opener =  urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36')]
urllib.request.install_opener(opener)

# Do login:
postLogin = {'email' : mail,
          'password' : passw,
          'safari' : '',
          'url':'/customerzone/index'}

postData = urllib.parse.urlencode(postLogin)
postData = postData.encode('utf-8')

response = opener.open(loginUrl, postData)    

printCurrentReservations()

# sys.exit()
print("\n:::::::::::::::::::::::::::::::::::::::::::::::::::")


for x in range(BOOKING_DAYS):
  targetDate = datetime.date.today() + datetime.timedelta(days=x)
  if targetDate.weekday() in BOOKING_WEEK_DAYS:
    doReservation(targetDate, HOUR)

print("\n:::::::::::::::::::::::::::::::::::::::::::::::::::")
printCurrentReservations()

print("end")