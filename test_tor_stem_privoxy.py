# -*- coding: utf-8 -*-
import io
import pycurl

import time

from stem import Signal
from stem.control import Controller

# initialize some HTTP headers
# for later usage in URL requests
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}

# initialize some
# holding variables
oldIP = "0.0.0.0"
newIP = "0.0.0.0"

# how many IP addresses
# through which to iterate?
nbrOfIpAddresses = 300000

# seconds between
# IP address checks
secondsBetweenChecks = 1


# request a URL
def request(url):
    # communicate with TOR via a local proxy (privoxy)
    output = io.BytesIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, 9050)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.WRITEFUNCTION, output.write)
    query.setopt(pycurl.USERAGENT, user_agent)

    try:
        query.perform()
        print(url + " " + str(query.getinfo(pycurl.HTTP_CODE)))
        return output.getvalue()
    except pycurl.error as exc:
        return "Unable to reach %s (%s)" % (url, exc)


def requestWithoutTor(url):
    # communicate with TOR via a local proxy (privoxy)
    output = io.BytesIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        print(query.getinfo(pycurl.HTTP_CODE))
        return output.getvalue()
    except pycurl.error as exc:
        return "Unable to reach %s (%s)" % (url, exc)


# signal TOR for a new connection
def renew_connection():
    print ("renew")
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='my_password')
        controller.signal(Signal.NEWNYM)
        controller.close()

# cycle through
# the specified number
# of IP addresses via TOR
for i in range(0, nbrOfIpAddresses):

    # if it's the first pass
    if newIP == "0.0.0.0":
        # renew the TOR connection
        renew_connection()
        # obtain the "new" IP address
        newIP = request("http://icanhazip.com/")
    # otherwise
    else:
        # remember the
        # "new" IP address
        # as the "old" IP address
        oldIP = newIP
        # refresh the TOR connection
        renew_connection()
        # obtain the "new" IP address
        newIP = request("http://icanhazip.com/")

    # zero the
    # elapsed seconds
    seconds = 0
    # print(requestWithoutTor("http://icanhazip.com/"))
    # requestWithoutTor("https://www.amazon.com/")
    request("https://www.amazon.com/")

    # loop until the "new" IP address
    # is different than the "old" IP address,
    # as it may take the TOR network some
    # time to effect a different IP address
    while oldIP == newIP:
        # sleep this thread
        # for the specified duration
        time.sleep(secondsBetweenChecks)
        # track the elapsed seconds
        seconds += secondsBetweenChecks
        # obtain the current IP address
        newIP = request("http://icanhazip.com/")
        request("https://www.amazon.com/")
        # signal that the program is still awaiting a different IP address
        print ("%d seconds elapsed awaiting a different IP address." % seconds)
    # output the
    # new IP address
    print ("")
    print ("newIP: %s" % newIP)
