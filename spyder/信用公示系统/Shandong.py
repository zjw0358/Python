#coding=utf-8
__author__ = 'Chen'

#如果程序异常，手动更换cookie
####################################################
#修改：李龚
#兼容2.*和3.*两个版本，同时处理字符串的编码问题
#####################################################
try:
    from urllib.request import Request
    from urllib.parse import urlencode
except:
    from urllib2 import Request
    from urllib import urlencode
    
import  re
from datetime import *
from YCParser import YCParser
import json

class GetYCParser(YCParser):

    def getpagepostdata(self,pageNos):
        postdata= urlencode({
            'page':'%d'% pageNos
        }).encode('utf-8')
        return postdata

    def getinfopostdata(self,encrpripid):
        postdata= urlencode({
            'encrpripid':encrpripid
        }).encode('utf-8')
        return postdata

    def setdate(self,date_json):
        if not date_json:return ""
        day=date_json['date']
        month=date_json['month']+1
        year=date_json['year']+1900
        return date(year,month,day)

    def getentlist(self,startdate,enddate):
        pageNos=0
        #根据Cookie获取token
        #self.cookie=' JSESSIONID=GSzG3Iev4t6IQ3oqyU1X3eFh.undefined'
        req=Request(
            url='http://218.57.139.24/pub/abnormalrecordindex',
            headers={'Cookie':self.gen_cookie()}
        )
        result=self.gethtml(req)
        self.token=result.find('meta',attrs={'name':'_csrf'}).get('content')
        while True:
            try:
                pageNos+=1
                if pageNos>19023:break
                req=Request(
                    url='http://218.57.139.24/pub/jyyc',
                    data=self.getpagepostdata(pageNos),
                    headers={'X-CSRF-TOKEN':self.token,
                             'Cookie':self.gen_cookie(),
                            'Accept': 'application/json, text/javascript, */*; q=0.01'}
                )
                result=self.gethtml(req)
                jsonlist=json.loads(str(result))
            except Exception:
                self.printpageerror(pageNos)
                continue
            else:
                print('Page %d Reading' % pageNos)
                br=0
                for jsonre in jsonlist:
                    try:
                        cdate=self.setdate(jsonre['abntime'])
                        if cdate<startdate:
                            br=1
                            break
                        else:
                            if cdate<=enddate:
                                Name=jsonre['entname'].replace('\n','').strip()
                                if self.checkname(Name)==False:continue
                                entdict=dict(Name=Name,pri=jsonre['pripid'],reg=jsonre['regno'],type=jsonre['enttype'])
                                self.PrintInfo(entdict,self.f)
                    except Exception:
                        self.printitemerror(pageNos,jsonre)
                        continue
            if br==1:break

    def PrintInfo(self,ent,f):
        req= Request(
            url='http://218.57.139.24/pub/jyyc/'+ent.get('type'),
            data=self.getinfopostdata(ent.get('pri')),
            headers={'User-Agent':'Magic Browser',
                     'X-CSRF-TOKEN':self.token,
                     'Cookie':self.gen_cookie()}
        )
        inforesult=str(self.gethtml(req))
        infolist=json.loads(inforesult)
        l=len(infolist)
        for i in range(l):
            f.write(self.to_utf8(ent.get('Name'))+'|')
            f.write(self.to_utf8(ent.get('reg'))+'|')
            f.write(str(i+1)+'|')
            f.write(self.to_utf8(infolist[i]['specause'])+'|')
            f.write(str(self.setdate(infolist[i]['abntime']))+'|')
            f.write(self.to_utf8(infolist[i]['remexcpres'])+'|')
            f.write(str(self.setdate(infolist[i]['remdate']))+'|')
            f.write(self.to_utf8(infolist[i]['decorg'])+'|')
            f.write('\n')

if __name__=='__main__':
    location='山东'
    YCParser=GetYCParser()
    YCParser.GetYC(location,startdate=date(2013,11,1),enddate=date.today())