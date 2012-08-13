from time import clock, sleep, time #for class delayCheck()

import urllib.request
import xml.etree.ElementTree as etree##for TreeGet()

import urlGet

class TreeGet():    
    def __init__(self, limit = .55, callFrequency = 1):
        self.start = time()
        self.elapsed = 0.0001
        self.requests = 0
        self.limit = limit #.55 requests/seconds 2000/hour for amazon
        self.callFrequency = callFrequency        
    def delay(self):
        self.requests += self.callFrequency
        self.elapsed = time()-self.start
        if self.elapsed == 0:
            self.elapsed = .0001
        if(self.requests/self.elapsed>self.limit):
            sleep((self.requests/self.limit)-self.elapsed)
        if self.elapsed > 600:
            self.start = time()
            self.elapsed = 0.0001
            self.requests = 0
    def getTree(self, parameters):
        errors = 0
        self.delay()
        url = urlGet.urlBuild(parameters)
        inLoop = True
        while(inLoop):
            try:
                page = urllib.request.urlopen(url)
                inLoop = False
            except:
                ###############################################
                errors += 1
                
                if errors > 100:
                    print('!!!!!!!!!!!!!!!!!!100 Errors!!!!!!!!!!!')
                    print(url)
                    sleep(60)
                ################################################
                sleep(1)              
        tree = etree.parse(page)
        page.close()
        return tree

class AsinGet():
    def __init__(self):
        self.alph = 'abcdefghijklmnopqrstuvwxyz'
        self.myTreeGet = TreeGet()
    def makeExtraction(self,letters):
        print(letters)
        parameters = {'Operation':'ItemSearch',
                      'SearchIndex': 'Books',
                      'Power': letters}
        PRESTRING = '{http://webservices.amazon.com/AWSECommerceService/2009-03-31}'
        asins = []
        tree = self.myTreeGet.getTree(parameters)
        pages = tree.findtext('//'+PRESTRING+'TotalPages')
        if int(pages) > 400:
            for letter in self.alph:
                asins.extend(self.makeExtraction(letters+letter))
        else:
            pageRange = int(pages)
            for eachPage in range(1,pageRange+1):
                asins.extend(self.getAsins(letters,eachPage))
        return asins
    def getAsins(self, letters, pageNumber):
        parameters = {'Operation':'ItemSearch',
                      'SearchIndex': 'Books',
                      'ItemPage': str(pageNumber),
                      'Power': letters}
        PRESTRING = '{http://webservices.amazon.com/AWSECommerceService/2009-03-31}'
        asins = []
        tree = self.myTreeGet.getTree(parameters)
        allItems = tree.findall('//'+PRESTRING+'Item')
        for item in allItems:
            asins.append(item.findtext(PRESTRING+'ASIN'))
        return asins

class Requester():
    def __init__(self,constParameters):
        self.prestring = '{http://webservices.amazon.com/AWSECommerceService/2009-03-31}'
        self.constParameters = constParameters
        self.treeGet = TreeGet()
    def extract(self,itemsList,metaInfo):
        returnList = []
        itemDict = {}
        asins = ''
        for item in itemsList[0:-1]:
            asins += (item+',')
        asins += itemsList[-1]
        parameters = self.constParameters
        parameters.update({'ItemId':asins})
        tree = self.treeGet.getTree(parameters)
        if tree.find('.//'+self.prestring+'Request').findtext(self.prestring+'IsValid')=='True':
            items = tree.findall('.//'+self.prestring+'Item')
## for debugging
##            errors = tree.find('.//'+PRESTRING+'Errors').findall('.//'+PRESTRING+'Error')
##            if errors:    
##                for error in errors:
##                    errorMsg = error.findtext(PRESTRING+'Message')
##                    errorCode = error.findtext(PRESTRING+'Message')
##                    pass#do something w/above
            for item in items:
                offerListings = []
                itemDict = {}
                for info in metaInfo:
                    if type(info) is list:
                        element = item
                        for child in info[0:-1]:
                            element = element.find('.//'+self.prestring+child)
                        itemDict[info[1]] = element.findtext(self.prestring+info[-1])
                    else:
                        itemDict[info] = item.findtext(self.prestring+info)
                offers = item.findall('.//'+self.prestring+'OfferListing')
                for offer in offers:
                    offerListings.append(offer.findtext('.//'+self.prestring+'Amount'))
                itemDict['offers'] = offerListings
                returnList.append(itemDict)
            return returnList
        
class Lookup():
    def __init__(self,meta=[],const={}):
        if not meta:
            self.metaInfo = ['ASIN','SalesRank',
                            ['OfferSummary','LowestNewPrice','Amount'],
                            ['OfferSummary','LowestUsedPrice','Amount'],
                            ['Offers','TotalOffers']]
        else:
            self.metaInfo = meta
        if not const:
            self.constParams = {'Operation':'ItemLookup',
                           'Condition':'All',
                           'MerchantId':'All',
                           'ResponseGroup':'SalesRank,Offers,OfferListings'}
        else:
            self.constParams = const
        self.requester = Requester(self.constParams)
    def lookup(self,asinList):
        return self.requester.extract(asinList,self.metaInfo)
