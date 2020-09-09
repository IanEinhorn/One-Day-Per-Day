import sys
import random
from datetime import date, timedelta
import calendar as cal
import requests, json
from PIL import Image, ImageDraw, ImageFont
from conf import API_KEY,BOT_ID,FONT
from ddate.base import DDate
TEXT_COLOR = (0,0,0)
BG_COLOR = (255,255,255)
IMAGEFILE = 'oneDay.png'
WRONGPROBABILITY = 11
GREGORIANPROBABILITY = 86


def generateDate():
    chance = random.randrange(0,101)
    if chance > WRONGPROBABILITY:
        return date.today()
    else:# chance <= WRONGPTOBABILITY
        daydelta = (chance**4)*random.choice((1,-1))-2
        return date.today() + timedelta(daydelta)


def formatCalendar(day):
    chance = random.randrange(0,101)
    if chance <= GREGORIANPROBABILITY:
        return gregorianCalendar(day)
    else:# chance > GREGORIANPROBABILITY
        return discordianCalendar(day) if chance <= 95 else march(day)


def discordianCalendar(day):
    discordianDay = DDate(day)
    dayInfo = {}
    dayInfo['DayName'] = DDate.WEEKDAYS[discordianDay.day_of_week]
    dayInfo['MonthName'] = DDate.SEASONS[discordianDay.season]
    dayInfo['DayNum'] =  str(discordianDay.day_of_season)
    dayInfo['MonthNum'] = str(discordianDay.season)
    dayInfo['YearNum'] = 'YOLD '+str(discordianDay.year)
    dayInfo['Format'] = 'Discordian'
    return dayInfo

def gregorianCalendar(day):
    dayInfo = {}
    dayInfo['DayName'] = cal.day_name[day.weekday()]
    dayInfo['MonthName'] = cal.month_name[day.month]
    dayInfo['DayNum'] =  str(day.day)
    dayInfo['MonthNum'] = str(day.month)
    dayInfo['YearNum'] = str(day.year)
    dayInfo['Format'] = 'Gregorian'
    return dayInfo


def julianDayNumber(day):
    dayInfo = {}
    D = day.day
    M = day.month
    Y = day.year
    jdn = int((1461.*(Y+4800+(M-14)/12))/4+(367*(M-2-12*((M-14)/12)))/12-(3*((Y+4900+(M-14)/12)/100))/4+D-32075)
    dayInfo['DayName'] = cal.day_name[day.weekday()]
    dayInfo['MonthName'] = ''
    dayInfo['DayNum'] =  str(jdn)
    dayInfo['MonthNum'] = str(0)
    dayInfo['YearNum'] = ''
    dayInfo['Format'] = 'Julian Day Number'
    return dayInfo


def march(day):
    print day,
    if(day < date(2020,2,29)):
        gregorianCalendar(day)
    else:
        monthYear = ((day.year-1)%12)
        if monthYear > day.month: #last Year's Month Hasnt ended, use previous year
            month = (day.year-2)%12
            startOrd = date(day.year-1, (month), 1).toordinal() - 1
        else: # The monthYear started this year
            month = (day.year-1)%12
            startOrd = date(day.year, ((day.year-1)%12), 1).toordinal() - 1
        dayInfo = {}
        dayInfo['DayName'] = cal.day_name[day.weekday()]
        dayInfo['MonthName'] = cal.month_name[month]
        dayInfo['DayNum'] =  str(day.toordinal()-startOrd)
        dayInfo['MonthNum'] = month
        dayInfo['YearNum'] = ''
        dayInfo['Format'] = 'March'
        return dayInfo


def makeSquare(calendarDay):
    '''Takes in a dict of info about a day and formats it into a calendar square image'''
    #Font definitions and Canvas setup
    FONT20 = ImageFont.truetype(font = FONT,size = 20)
    FONT40 = ImageFont.truetype(font = FONT,size = 40)
    FONT75 = ImageFont.truetype(font = FONT,size = 80)
    img = Image.new(mode = 'RGB', size=(200,200), color = BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    #Day and Month
    draw.text((20,15),calendarDay['DayName'],fill = TEXT_COLOR, font = FONT20)
    draw.text((20,35),calendarDay['MonthName'],fill = TEXT_COLOR, font = FONT20)
    
    #Day Number, corrected for font size and centered
    dayFont = FONT75 if len(calendarDay['DayNum']) < 5 else FONT40
    w,h=draw.textsize(calendarDay['DayNum'],dayFont)
    draw.text(((100-w/2),70),calendarDay['DayNum'],fill = TEXT_COLOR, font = dayFont)
    
    #Year, centered
    w,h=draw.textsize(calendarDay['YearNum'],FONT20)
    draw.text(((100-w/2),165),calendarDay['YearNum'],fill = TEXT_COLOR, font = FONT20)
    
    #Outline
    draw.rectangle([0,0,199,199],fill = None,outline = TEXT_COLOR)
    draw.rectangle([1,1,198,198],fill = None,outline = TEXT_COLOR)
    draw.rectangle([2,2,197,197],fill = None,outline = TEXT_COLOR)
    draw.rectangle([3,3,196,196],fill = None,outline = TEXT_COLOR)
    #Save output
    img.save('img.png')


def groupmePostImage():
    data = open('./img.png','rb').read()
    res = requests.post(url='https://image.groupme.com/pictures',
                        data=data,
                        headers={'Content-Type': 'image/png',
                                'X-Access-Token': API_KEY})
    print res.content
    url=res.json()[u'payload'][u'url']
    print url
    return url

def groupmePostMessage(imageURL = None,text = None):
    data = data={'Content-Type': 'application/json', 'bot_id' : BOT_ID}
    if text:
        data['text'] = text
        print text
    if imageURL:
        data['picture_url'] = imageURL
        print imageURL
    if text or imageURL:
        print 'Posting'
        res = requests.post(
            url='https://api.groupme.com/v3/bots/post',
            data=data)
        print res.content


def oneDayPerDay(Day=None):
    if Day: #if a Day is specified, ensure it is the correct format and use it
        if (tyfpe(Day) == isinstance(Day,tuple) and len(Day)==3):
            Day = date(Day[0],Day[1],Day[2])  
        else: #day is invalid
            print "Invalid Day specified, Please use '(YYYY,MM,D)'"
    else: #No Date is specified, Genterate one
            Day = generateDate()
    print Day
    calendarDay = formatCalendar(Day)
    print calendarDay['DayName'],calendarDay['MonthName'],calendarDay['DayNum'],',',calendarDay['YearNum']
    makeSquare(calendarDay)
    url = groupmePostImage()
    groupmePostMessage(url)
    print 'Done'


#Test functions
def testGenerateDate():
    for i in xrange(100):
        print generateDate()
def testFormatCalendar():
    for i in xrange(100):
        t = generateDate()
        #f = formatCalendar(t)
        f = march(t)
        print f
        #print 'Today is '+f['DayName']+', '+str(f['DayNum'])+' day of '+f['MonthName']+', '+str(f['yearNum'])

def testMarch():
    for i in xrange(100):
        t = generateDate()
        #f = formatCalendar(t)
        f = march(t)
        print f
        #print 'Today is '+f['DayName']+', '+str(f['DayNum'])+' day of '+f['MonthName']+', '+str(f['yearNum'])


def testmakeSquare():
    t = generateDate()
    f = march(t)
    #f = formatCalendar(t)
    print t
    print f
    makeSquare(f)


if __name__ == '__main__':
    if '-d' in sys.argv: #flags to only run part of the code
        #testFormatCalendar()
        #testmakeSquare()
        testMarch()
    else: #post to groupme
        oneDayPerDay()


