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

def extractSecurityIssues():
 securityFixList = []
 url = "https://rhn.redhat.com/errata/rhel-server-6.5-errata-security.html"
 text = urlopen(url).read()   
 list1 = re.findall('errata/RHSA-(\w\w\w\w-\w\w\w\w.html)',text)
 for x in list1:
  securityFixList.append("https://rhn.redhat.com/errata/RHSA-"+x)
 return securityFixList
 
def retrieveInstalledPackages():
 set1=readFile(fileList[0])
 count=0
 uniqueList=[]
 while count<len(fileList):
  #print fileList[count]
  lines=readFile(fileList[count])
  for line in lines:
   if line not in uniqueList:
    uniqueList.append(line)
  count+=1
 return uniqueList

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

#retrieveInstalledPackages():

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

 urlList=extractSecurityIssues()
 patchList=[]
 outputFile="data.txt"
 if not os.path.exists(outputFile):
  for url in urlList:
  
   errataNo=url.replace("https://rhn.redhat.com/errata/","")
   errataNo=errataNo.replace(".html","")

   print "- Extracting hotfixes from "+url
   html = urlopen(url).read()    
   list1 = re.findall('(.*).rpm',html)
   for x in list1:
    if "\t\t<td>" in x:
     filename=x.replace("\t\t<td>","")+".rpm"
     if filename not in patchList:
      patchList.append([errataNo,filename])
  f = open(outputFile, 'w')
  for patch in patchList:
   f.write(patch[0]+","+patch[1]+"\n")
  f.close()

 #resultList=[]
 #lines=readFile(outputFile)
 #for line in lines:
 # line = line.strip()
 # line1 = line1.split(",")
 # pkgName, pkgVersion = extractPkgNameAndVer(line1[1])
 # if platform in pkgVersion: 
 #  pkgName=pkgName.strip()
 #  if len(pkgName)>1:
 #   if [pkgName,pkgVersion] not in resultList:
 #    resultList.append([pkgName,pkgVersion]) 
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
     if "x86_64" in pkgVerHotfix and "x86_64" in pkgVer:
      if [pkgName,pkgVerHotfix,pkgVer] not in doneList:
       cmd = "dpkg --compare-versions "+pkgVerHotfix+" gt "+pkgVer+" && echo 'True'"
       #cmd = "dpkg --compare-versions "+pkgVerHotfix+" lt "+pkgVer+" && echo 'True'"
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

    #url = "https://rhn.redhat.com/errata/"+y[0]+".html"
    #print "Url: "+url
    #print "Outdated Package: "+packageName

    if packageName not in pkgList:
     pkgList.append(packageName)
     urlList.append(y[0])
    else:
     positionNo = pkgList.index(packageName)
     urlList[positionNo] += ", "
     urlList[positionNo] += y[0]

 count=0
 for x in urlList:
  print "Outdated Package: "+pkgList[count]
  print "ID: "+x+"\n"
  count+=1


if __name__ == '__main__':
 parser = argparse.ArgumentParser()
 parser.add_argument('-f', action='store', help='[packages file]')
 if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
    
 options = parser.parse_args()
 if options.f:
  #fileList.append(options.f)
  runTask(options.f)
