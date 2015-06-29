from bs4 import BeautifulSoup
from urllib import urlopen
import argparse
import sys
import socket
import re
import commands
import os

REMOTE_SERVER = "www.google.com"
platform = "x86_64"

def checkPlatform(filename):
 lines=[]
 with open(filename) as f:
  lines = f.read().splitlines()
 if "x86_64" in str(lines):
  platform = "x86_64"
 elif "i686" in str(lines):
  platform = "i686"
 elif "ppc" in str(lines):
  platform = "ppc"
 elif "390x" in str(lines):
  platform = "390x"
 else:
  platform = ""
 return platform
 
def extractSecurityIssues():
 securityFixList = []
 url = "https://rhn.redhat.com/errata/rhel-server-6.5-errata-security.html"
 text = urlopen(url).read()   
 list1 = re.findall('errata/RHSA-(\w\w\w\w-\w\w\w\w.html)',text)
 for x in list1:
  securityFixList.append(x.replace(".html",""))
  #securityFixList.append("https://rhn.redhat.com/errata/RHSA-"+x)
 return securityFixList
 
#def retrieveInstalledPackages():
# set1=readFile(fileList[0])
# count=0
# uniqueList=[]
# while count<len(fileList):
#  lines=readFile(fileList[count])
#  for line in lines:
#   if line not in uniqueList:
#    uniqueList.append(line)
#  count+=1
# return uniqueList

def readFile(filename):
 with open(filename) as f:
  lines = f.read().splitlines()
  return lines

def runCommand(cmd):
 ret = commands.getoutput(cmd)
 return ret

def is_connected():
 try:
  host = socket.gethostbyname(REMOTE_SERVER)
  s = socket.create_connection((host, 80), 2)
  return True
 except:
  pass
 return False

def extractPkgNameAndVer(line):
  found=False
  pkgSplit = line.split("-")
  pkgName=""
  for line1 in pkgSplit:
   if found==False:
    #Pending Fix
    if line1[0].isalpha() or "389" in line1 or "390" in line1:
      pkgName+=line1
      pkgName+="-"
    else:
     found=True
  pkgVersion=line.replace(pkgName,'')
  pkgVersion=pkgVersion.replace(".rpm","")
  pkgName=pkgName[0:-1]
  return pkgName,pkgVersion

def runTask(argFilename):
 if is_connected()==False:
  print "Internet is down"
  sys.exit()
 
 global platform
 platform = checkPlatform(argFilename)

 urlList=extractSecurityIssues()
 patchList=[]
 outputFile="data.txt"
 if os.path.exists("data.txt"):
  os.remove("data.txt")

 if not os.path.exists(outputFile):
  for errataNo in urlList:
  
   #errataNo=url.replace("https://rhn.redhat.com/errata/","")
   #errataNo=errataNo.replace(".html","")

   if not os.path.exists(os.getcwd()+"/data"):
    os.makedirs(os.getcwd()+"/data")
    
   url = "https://rhn.redhat.com/errata/RHSA-"+errataNo+".html"

   filename = os.getcwd()+"/data/RHSA-"+errataNo+".html"
   html = ""
   lines = []
   if not os.path.exists(filename):
    print "- Extracting hotfixes from "+url
    html = urlopen(url).read()    
    f = open(filename, 'w')
    f.write(html)
    f.close()
   else:
    print "- Extracting hotfixes from "+filename
    with open(filename) as f:
     #html=f.read().replace('\n', '')
     html=f.read()

   list1 = re.findall('(.*).rpm',html)  

   for x in list1:
    if "\t\t<td>" in x:
     filename1=x.replace("\t\t<td>","")+".rpm"
     if filename1 not in patchList:
      patchList.append([errataNo,filename1])
  f = open(outputFile, 'w')
  for patch in patchList:
   f.write(patch[0]+","+patch[1]+"\n")
  f.close()

 doneList=[]

 fileList=[]
 fileList.append(argFilename)

 finalList1=[]
 outputFile="data.txt"
 lines = readFile(outputFile)
 for line1 in lines:
  line1 = line1.split(",")
  line2 = line1[1]
  pkgNameHotfix, pkgVerHotfix = extractPkgNameAndVer(line2)

  for filename in fileList:
   resultList=readFile(filename)
   for x in resultList:
    pkgName, pkgVer = extractPkgNameAndVer(x)
    if pkgName==pkgNameHotfix:
     if platform!="":
      if platform in pkgVerHotfix and platform in pkgVer:
      #if "x86_64" in pkgVerHotfix and "x86_64" in pkgVer:
       if [pkgName,pkgVerHotfix,pkgVer] not in doneList:
        cmd = "dpkg --compare-versions "+pkgVerHotfix+" gt "+pkgVer+" && echo 'True'"
        results = runCommand(cmd)
        if results:
         errataNo = line1[0]
         if [errataNo,pkgName,pkgVer] not in finalList1:  
           finalList1.append([errataNo,pkgName,pkgVer])
        doneList.append([pkgName,pkgVerHotfix,pkgVer])
     else:
      if "x86_64" not in pkgVerHotfix and "i686" not in pkgVerHotFix and "ppc" not in pkgVerHotFix and "s390" not in pkgVerHotFix and "x86_64" not in pkgVer and "i686" not in pkgVer and "ppc" not in pkgVer and "s390" not in pkgVer:
       if [pkgName,pkgVerHotfix,pkgVer] not in doneList:
        cmd = "dpkg --compare-versions "+pkgVerHotfix+" gt "+pkgVer+" && echo 'True'"
        results = runCommand(cmd)
        if results:
         errataNo = line1[0]
         if [errataNo,pkgName,pkgVer] not in finalList1:  
           finalList1.append([errataNo,pkgName,pkgVer])
        doneList.append([pkgName,pkgVerHotfix,pkgVer])

 urlList=[]
 pkgList=[]

 for filename in fileList:
  dataList=readFile(filename)
  for y in finalList1:
   #print y[1]
   if y[1] in str(dataList):
    packageName = y[1]+"-"+y[2]

    url = "https://rhn.redhat.com/errata/RHSA-"+y[0]+".html"

    if packageName not in pkgList:
     pkgList.append(packageName)
     urlList.append(url)
    else:
     positionNo = pkgList.index(packageName)
     urlList[positionNo] += "\n"
     urlList[positionNo] += url

 count=0
 for x in urlList:
  print "Outdated Package: "+pkgList[count]
  print x+"\n"
  count+=1


if __name__ == '__main__':
 parser = argparse.ArgumentParser()
 parser.add_argument('-i','--input', action='store', help='[packages file]')
 if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
    
 options = parser.parse_args()
 if options.input:
  runTask(options.input)
