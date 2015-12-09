#!/usr/bin/env python
#
# Author: Rahul Anand <et@eternal-thinker.com>
#         2014-02-21, stardate [-28]9946.35
#
# Description:
#   Convert date formats to Stardates
#   Uses Stardate versions in Star Trek FAQ, as adopted by Google Calender
#
# Python version: 2.7
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#####################################################################################
#
# Based on the following work:
#
# stardate: convert between date formats
# by Andrew Main <zefram@fysh.org>
# 1997-12-26, stardate [-30]0458.96
#
# Copyright (c) 1996, 1997 Andrew Main.  All rights reserved.
#
# Stardate code is based on version 1 of the Stardates in Star Trek FAQ.
#####################################################################################

import sys
import datetime
import re

dayseconds = 86400
sdreg = re.compile(r"^\[(-{0,1}\d+)\](\d+)\.{1}(\d+)$")
datetimereg = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$") 

# The epoch for stardates, 2162-01-04, is 789294 (0xc0b2e) days after
# the internal epoch.  This is 789294*86400 (0xc0b2e*0x15180) ==
# 68195001600 (0xfe0bd2500) seconds.
ufpepoch = 0xfe0bd2500

# The epoch for TNG-style stardates, 2323-01-01, is 848094 (0xcf0de)
# days after the internal epoch.  This is 73275321600 (0x110f8cad00)
# seconds.
tngepoch = 0x110f8cad00

class Stardate():    
    # Definitions to help with leap years.
    nrmdays = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
    lyrdays = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
    
    def gleapyear(self, y):
        return (not y % 4) and (y % 100 or not y % 400)
    
    def gdays(self, y):
        return self.lyrdays if self.gleapyear(y) else self.nrmdays

    def __init__(self):
        pass

    def toStardate(self, date=None):
        S, F = 0, 0
        if not date:
            date = self.getcurdate()
        date = list(re.findall(datetimereg, date)[0])
        date = [int(i) for i in date]
        S = self.gregin(date)

        isneg = True
        nissue, integer, frac = 0, 0, 0

        if S >= tngepoch:
            return self.toTngStardate(S, F)

        if S < ufpepoch:
            # negative stardate
            diff = ufpepoch - S
            nsecs = 2000*dayseconds - 1 - (diff % (2000 * dayseconds))
            isneg = True
            nissue = 1 + ((diff / (2000 * dayseconds)) & 0xffffffff)
            integer = nsecs / (dayseconds/5)
            frac = ( ((nsecs % (dayseconds/5)) << 32) | F ) * 50
        elif S < tngepoch:
            # positive stardate
            diff = S - ufpepoch
            nsecs = diff % (2000 * dayseconds)
            isneg = False
            nissue = (diff / (2000 * dayseconds)) & 0xffffffff

            if nissue < 19 or ( nissue == 19 and nsecs < (7340*(dayseconds/5)) ) :
                # TOS era
                integer = nsecs / (dayseconds/5)
                frac = ( ((nsecs % (dayseconds/5)) << 32) | F ) * 50
            else:
                # film era
                nsecs += (nissue - 19) * 2000 * dayseconds
                nissue = 19
                nsecs -= 7340 * (dayseconds/5)
                if nsecs >= 5000*dayseconds:
                    # late film era
                    nsecs -= 5000 * dayseconds
                    integer = 7840 + nsecs / (dayseconds*2)
                    if integer >= 10000:
                        integer -= 10000
                        nissue += 1
                    frac = ( ((nsecs % (dayseconds*2)) << 32) | F ) * 5
                else:
                    # early film era
                    integer = 7340 + nsecs / (dayseconds*10)
                    frac = ( ((nsecs % (dayseconds*10)) << 32) | F )

        ret = "[" + ("-" if isneg else "")  + str(nissue) + "]" + str(integer).zfill(4)
        frac = ( ( ((frac * 125) / 108) >> 32 ) & 0xffffffff ) # round
        ret += "." + str(frac)
        return ret

    def toTngStardate(self, S=0, F=0):
        diff = S - tngepoch
        # 1 issue is 86400*146097/4 seconds long, which just fits in 32 bits.
        nissue = 21 + diff/((dayseconds/4)*146097)
        nsecs = diff % ((dayseconds/4)*146097)
        # 1 unit is (86400*146097/4)/100000 seconds, which isn't even.
        # It cancels to 27*146097/125.  For a six-figure fraction,
        # divide that by 1000000.
        h = nsecs * 125000000
        l = F * 125000000
        h = h + ((l >> 32) & 0xffffffff)
        h = h / (27*146097)
        ret = "[%d]%05d" % ( nissue, ((h/1000000) & 0xffffffff) )
        ret += ".%06d" % (h % 1000000)
        return ret;

    def getcurdate(self):
       return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gregin(self, date=None):
        y, m, d, H, M, S = date

        cycle = y % 400

        low = (y == 0)
        if low:
            y = 399
        else:
            y = y - 1

        t = y * 365
        t = t - y/100
        t = t + y/400
        t = t + y/4

        n = 2 + d - 1
        m -= 1
        while m > 0:
            n += self.gdays(cycle)[m]
            m -= 1

        t = t + n
        if low:
            t = t - 146097
        t = t * dayseconds

        retS = t + H*3600 + M*60 + S

        return retS


    def fromStardate(self, stardate):
        nineteen = 19
        twenty = 20
        S, F = 0, 0  

        sd = re.findall(sdreg, stardate)
        if not len(sd):
            print "Invalid stardate format"
            return
        sd = sd[0]
        nissue = int(sd[0])
        isneg = nissue < 0
        nissue = abs(nissue)
        integer = int(sd[1])
        frac = int( sd[2] + '0'*(6 - len(sd[2])) )

        if (integer > 99999) or \
           (not isneg and nissue == twenty and integer > 5005) or \
           ((isneg or nissue < twenty) and integer > 9999):
            print "Integer part is out of range"
            return
        
        if isneg or nissue <= twenty:
            # Pre-TNG stardate
            if not isneg:
                # There are two changes in stardate rate to handle:
                #      up to [19]7340      0.2 days/unit
                # [19]7340 to [19]7840     10   days/unit
                # [19]7840 to [20]5006      2   days/unit
                # we scale to the first of these.

                fiddle = False
                if nissue == twenty:
                    nissue = nineteen
                    integer += 10000
                    fiddle = True
                elif nissue == nineteen and integer >= 7340:
                    fiddle = True

                if fiddle:
                    # We have a stardate in the range [19]7340 to [19]15006.  First
                    # we scale it to match the prior rate, so this range changes to
                    # 7340 to 390640.
                    integer = 7340 + ((integer - 7340) * 50) + frac / (1000000/50)
                    frac = (frac * 50) % 1000000

                    # Next, if the stardate is greater than what was originally
                    # [19]7840 (now represented as 32340), it is in the 2 days/unit
                    # range, so scale it back again.  The range affected, 32340 to
                    # 390640, changes to 32340 to 104000.
                    if integer >= 32340:
                        frac = frac/5 + (integer%5) * (1000000/5)
                        integer = 32340 + (integer - 32340) / 5

                S = ufpepoch + nissue * 2000 * dayseconds

            else:
                # Negative stardate.  In order to avoid underflow in some cases, we
                # actually calculate a date one issue (2000 days) too late, and
                # then subtract that much as the last stage.
                S = ufpepoch - (nissue - 1) * 2000 * dayseconds

            S = S + (dayseconds/5) * integer

            # frac is scaled such that it is in the range 0-999999, and a value
            # of 1000000 would represent 86400/5 seconds.  We want to put frac
            # in the top half of a uint64, multiply by 86400/5 and divide by
            # 1000000, in order to leave the uint64 containing (top half) a
            # number of seconds and (bottom half) a fraction.  In order to
            # avoid overflow, this scaling is cancelled down to a multiply by
            #  54 and a divide by 3125.
            f = (frac << 32) * 54
            f = (f + 3124) / 3125
            S = S + ((f >> 32) & 0xffffffff)
            F = f & 0xffffffff

            if isneg:
                # Subtract off the issue that was added above.
                S = S - 2000*dayseconds

        else:
            # TNG stardate
            nissue = nissue - 21

            # Each issue is 86400*146097/4 seconds long.
            S = tngepoch + nissue * (dayseconds/4)*146097

            # 1 unit is (86400*146097/4)/100000 seconds, which isn't even.
            # It cancels to 27146097/125.
            t = integer * 1000000
            t = t + frac
            t = t * 27 * 146097
            S = S + t / 125000000

            t = (t % 125000000) << 32
            t = (t + 124999999) / 125000000
            F = t & 0xffffffff

        return self.calout(S, F)


    def calout(self, S=0, F=0):
        tod = S % dayseconds
        days = S / dayseconds

        # We need the days number to be days since an xx01.01.01 to get the
        # leap year cycle right.  For the Julian calendar, it is already
        # so (0001=01=01).  But for the Gregorian calendar, the epoch is
        # 0000-12-30, so we must add on 400 years minus 2 days.  The year
        # number gets corrected below.
        days = days + 146095

        # Approximate the year number, underestimating but only by a limited
        # amount.  days/366 is a first approximation, but it goes out by 1
        # day every non-leap year, and so will be a full year out after 366
        # non-leap years.  In the Julian calendar, we get 366 non-leap years
        # every 488 years, so adding (days/366)/487 corrects for this.  In
        # the Gregorian calendar, it is not so simple: we get 400 years
        # every 146097 days, and then add on days/366 within that set of 400
        # years.
        year = (days/146097)*400 + (days % 146097)/366

        # We then adjust the number of days remaining to match this
        # approximation of the year.  Note that this approximation
        # will never be more than two years off the correct date,
        # so the number of days left no longer needs to be stored
        # in a uint64.
        days = (days + year/100) - (year/400)
        days = days - (year*365 + year/4)

        # Now correct the year to an actual year number (see notes above).
        year = year - 399

        return self.docalout(year%400, year, days&0xffffffff, tod)


    def docalout(self, cycle, year, ndays, tod):
        nmonth = 0
        # Walk through the months, fixing the year, and as a side effect
        # calculating the month number and day of the month.
        while ndays >= self.gdays(cycle)[nmonth]:
            ndays -= self.gdays(cycle)[nmonth]
            nmonth += 1
            if nmonth == 12:
                nmonth = 0
                year += 1
                cycle += 1

        ndays += 1
        nmonth += 1
        # Now sort out the time of day.
        hr = tod / 3600
        tod %= 3600
        minut = tod / 60
        sec = tod % 60

        return "%d-%02d-%02d %d:%d:%d" % (year, nmonth, ndays, hr, minut, sec)


if __name__ == "__main__":
    sd = Stardate()

    if len(sys.argv) > 1:
        if sys.argv[1].startswith('['):
            print sd.fromStardate(sys.argv[1])
        else:
            dt = sys.argv[1]
            if len(sys.argv) > 2:
                dt += " " + sys.argv[2]
            else:
                dt += " 0:0:0"
            date = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") # Validating date ranges            
            print sd.toStardate(dt)
    else:
        print sd.toStardate()

    # import time
    # while True:
    #     print sd.toStardate()
    #     time.sleep(1)

