from bs4 import BeautifulSoup as soup
import requests
import os
import lxml
import csv
import sys
from lxml.html import fromstring
import time
import io
import random
import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')

#mydb = myclient["webcrawler"]
#mycol = mydb["amazonin1"]

#mydict = {"path":}
#mycol.insert_one(mydict)

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
#x=x.translate(non_bmp_map)
mainurl = "https://www.amazon.in"
glist=[]

user_agent_list = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    # Firefox
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
]


def getProxies():
    url = "https://free-proxy-list.net/"
    user_agent = random.choice(user_agent_list)
    headers = {"User-Agent": user_agent}  # Set the headers
    response = requests.get(url, headers=headers)
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr')[:20]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    return proxies


def getSoup(my_url):
    while True:
        try:
            proxies = []
            proxies = getProxies()
            proxy = random.choice(proxies)
            user_agent = random.choice(user_agent_list)
            headers = {'User-Agent': user_agent}
            r=requests.get(my_url,headers=headers,proxies={"https":proxy})
            #print proxy, " ", headers
            #print "sucess"
            break
        except:
            time.sleep(1)
    page_html = r.text
    rtsp=soup(page_html, "lxml")
    return rtsp

def myprinter():
    global glist
    print "------ In printer  ----------"
    #with io.open("restore.csv", "a",encoding=".unicode") as csvfile:
    #    filewriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for itt in glist:
        mydict = {"path":itt}
        mycol.insert_one(mydict)
    #for itt in glist:
    #    mydict = {"path": itt[:-1], "leafurl": itt[-1]}
    #    mycol.insert_one(mydict)
        #filewriter.writerow([str(it.translate(non_bmp_map).encode("utf-8")) for it in itt])
        #print itt
    glist=[]
    print "------ Out printer  ----------"
    #del glist[0,len(glist)]

def isChild(pg_soup,mainc):
    #pg_soup = getSoup(url)
    #print "in isChild : ",url
    pg_soup1 = pg_soup.find("div",{"id":"leftNav"})
    if (pg_soup1 != None):
        #return(pg_soup1,3)
        #pass
        pghead=pg_soup1.find("h4",{"class":"a-size-small a-color-base a-text-bold"})
        if (pghead != None):
            #return(pg_soup1,3)
            p=pghead.parent
            p=p.parent
            nextul = p.find_next_sibling("ul")
            #print nextul
            if(nextul.find("li") != None):
                #return nextul,2
                #print "Hello Yaswa"
                #last_li = None
               # for last_li in ul.find_all('li'): pass
                #content = last_li.text
                for i in nextul.find_all('li'):
                    llink = str(i.span.a["href"])
                    if (llink[0] == "/"):
                        llink=mainurl+llink
                    myrec(llink,mainc)
                return nextul,3
            else:
                # a leaf can be first level type-2
                #print "Got a leaf nodee "
                retsp = p.parent.find_all("li", {"class": "s-ref-indent-neg-micro"})
                #print len(retsp)
                return (retsp, 1)

        else:
            pghead = pg_soup1.find("h3", {"class": "a-size-medium a-spacing-base a-spacing-top-small a-color-tertiary a-text-normal"})
            if (pghead !=None):
                #print " Got the url... "
                grandp=pghead.next_sibling.find("li")
                #print grandp
                par=grandp.find("div",{"class":"a-row a-expander-container a-expander-extend-container"}).find_all("li")
                #print len(par)
                for item in range(0,len(par),2):
                    it=par[item].find("a",{"class":"a-link-normal s-ref-text-link"})
                    #print it.find("span").text
                    llink = it["href"]
                    if(llink!=None):
                        if (llink[0] == '/'):
                            llink=mainurl+llink
                            # print llink
                            #print "Got yu "
                        myrec(llink,mainc)
                grandp=grandp.find_next_siblings("li",{"class":""})
                for itt in grandp:
                    par = itt.find("div",{"class": "a-row a-expander-container a-expander-extend-container"}).find_all("li")
                    #print len(par)
                    for item in range(0, len(par), 2):
                        it = par[item].find("a", {"class": "a-link-normal s-ref-text-link"})
                        #print it.find("span").text
                        llink=it["href"]
                        if(llink != None):
                            if (llink[0] == '/'):
                                llink=mainurl+llink
                                #print llink
                                #print "Got yu "
                            myrec(llink,mainc)

                #return pg_soup1,123
            else:
                return (pg_soup1,0)    # first level leaf  type-1
    else:
        return (pg_soup,0)    # first level leaf      type-1


def myrec(urll,mainc):
    pg_sp = getSoup(urll)
    #print mainc
    #print urll
    (soup1,flag)=isChild(pg_sp,mainc)
    #print soup1
    #print flag
    if flag==3:
        return;
    if flag==2:
        for it in soup1:
            itt = it.find("a")
            turl = itt.get("href")
            if turl[0] == '/':
                turl = mainurl + turl
            #print "from url : ",urll
            #print "in myrec next url", turl
            #pg_soup6 = itt.find("span")
            myrec(turl, mainc)
    elif flag==1:
        global glist
        locall=[]
        locall.append(mainc)
        for its in soup1:
            j=its.find("a").find("span").text.strip()
            j=j.translate(non_bmp_map)
            locall.append(j)
        tlast=pg_sp.find("h4",{"class": "a-size-small a-color-base a-text-bold"}).text.strip()
        tlast=tlast.translate(non_bmp_map)          # this is a cause of error
        locall.append(tlast)
        locall.append(urll)
        print "In List : ",locall
        #mydict = {"path":locall}
        #mycol.insert_one(mydict)
        glist.append(locall)
        #del locall[0:len(locall)]
        #return
    elif flag==0:
        #print "Found First Level Leaf going to print in main"
        return 1


# Testing urlls
#myrec("https://www.amazon.in/b/ref=sd_allcat_shopall_catpage?ie=UTF8&node=14156834031","SAi")
#myrec("https://www.amazon.in/s/ref=lp_14095180031_nr_scat_10946311031_ln/259-6646625-8662547?srs=14095180031&rh=n%3A10946311031&ie=UTF8&qid=1549515592&scn=10946311031&h=710edc4106e349d586b8778956f52b5b205bfc89", "Sai");
#print myrec("https://www.amazon.in/alexa-skills/b/ref=sd_allcat_shopall_a2s_help?ie=UTF8&node=11928183031","Alexa Skills -- SAI")

myurl = mainurl + "/gp/site-directory/ref=nav_shopall_sbc_fullstore"
#print "Start time : ",time.ctime()
#cwd = os.getcwd()
#print(os.getcwd())
#full_path = os.path.realpath(__file__)
#path, filename = os.path.split(full_path)
#print "Here : ",os.path.exists("restore.txt")
#print os.stat("restore.txt").st_size
#print os.path.exists("restore.txt")
#if(my_file.is_file()):
#if(os.path.exists("/home/mys/PycharmProjects/amazonin6/restore.txt")==True):
#if (os.path.isfile("restore.txt") == True):

if(os.path.isfile("restore.txt")==True and os.stat("restore.txt").st_size !=0 ):
    flag=0
    print "exists"
    f = open("restore.txt","r")
    breakpoint=str(f.read())
    f.close()
    breakpoint= breakpoint.strip()
    print "This is in the file : ",breakpoint
    while True:
        #fflag=0
        pg_soup = getSoup(myurl)
        for ii in pg_soup.find("table", {"id": "shopAllLinks"}).find_all("td"):  # 4
            pg_soup1 = ii.find_all("div", {"class": "popover-grouping"})
            for jj in pg_soup1:  # ii.find_all("div", {"class": "popover-grouping"}):
                #print '-------------- **** ----------------'
                mainc = jj.find("h2").text.strip()
                # mainc = ''.join(mainc).decode("utf-8")
                mainc = str(mainc.translate(non_bmp_map))
                print mainc
                '''
                if(mainc!="Movies, Music & Video Games" and fflag==0):
                    continue
                else:
                    fflag=1
                '''
                pg_soup3 = jj.find("ul").find_all("li")
                for kk in pg_soup3:
                    pg_soup4 = kk.find("a")  # , {"class": "nav_a"})
                    namee = pg_soup4.text.strip()
                    # namee = ''.join(namee).decode("utf-8")
                    namee = (namee.translate(non_bmp_map))
                    print namee
                    if namee == breakpoint:
                        flag = 1
                    elif flag == 1:
                        urll = pg_soup4["href"]
                        if urll[0] == '/':
                            urll = mainurl + urll
                        #print urll
                        ret = myrec(urll, mainc)
                        if ret == 1:
                            llocal = []
                            llocal.append(mainc)
                            llocal.append(namee)
                            llocal.append(urll)
                            glist.append(llocal)
                            #mydict = {"path": llocal}
                            #mycol.insert_one(mydict)
                            #print "In Main : ", llocal
                            print "In Main : ",llocal
                        #print "This is namee in file : ", namee
                    if flag==1 and namee!=breakpoint:
                        #print "This is namee : ",namee
                        myprinter()
                        f = open("restore.txt","w")
                        namee = ''.join(namee).encode("utf-8").strip()
                        f.write(namee)  # decode('utf-8'))
                        f.close()
                        #print "File closed"
                     # print ' after myrpinter '
                 # for xyz in glist:
                 #    print xyz
                 # break
             # break
        break
else:
    print "doesn't exists"
    #mycol.drop()           If backup text file doesn't exists then corresponding collection in mongodb is dropped
    while True:
        pg_soup = getSoup(myurl)
        for ii in pg_soup.find("table", {"id": "shopAllLinks"}).find_all("td"):  # 4
            pg_soup1 = ii.find_all("div", {"class": "popover-grouping"})
            for jj in pg_soup1:  # ii.find_all("div", {"class": "popover-grouping"}):
                print '-------------- **** ----------------'
                mainc = jj.find("h2").text.strip()
                #mainc = ''.join(mainc).decode("utf-8")
                mainc=str(mainc.translate(non_bmp_map))
               # print mainc
                pg_soup3 = jj.find("ul").find_all("li")
                for kk in pg_soup3:
                    pg_soup4 = kk.find("a")#, {"class": "nav_a"})
                    urll = pg_soup4["href"]
                    namee = pg_soup4.text.strip()
                    #namee = ''.join(namee).decode("utf-8")
                    namee=str(namee.translate(non_bmp_map))
                    #print namee
                    if urll[0] == '/':
                        urll = mainurl + urll
                    #print urll
                    ret=myrec(urll, mainc)
                    if ret==1:
                        llocal=[]
                        llocal.append(mainc)
                        llocal.append(namee)
                        llocal.append(urll)
                        glist.append(llocal)
                        print "In Main : ",llocal
                        #mydict = {"path": llocal}
                        #mycol.insert_one(mydict)
                    myprinter()
                    f = open("restore.txt", "w")
                    namee = ''.join(namee).encode("utf-8").strip()
                    f.write(namee)  # decode('utf-8'))
                    f.close()
                    #print "File closed"
                #print ' after myrpinter '
                #for xyz in glist:
                #    print xyz
                #break
            #break
        break
print "End time : ",time.ctime()
