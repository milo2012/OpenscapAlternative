# OpenscapAlternative
OpenSCAP verifies the presence of patches by using content produced by the Red Hat Security Response Team (SRT), checks system security configuration settings and examines systems for signs of compromise by using rules based on standards/specifications.  
  
There are situations where the systems aren't installed with OpenSCAP and you need to check for packages that are missing important security patches.  
  
To list the list of installed appliactions on the RHEL system.  
$ yum list installed > packages.txt  
  
To run the script  
$ python checkPatches.py -i packages.txt  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-1035.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-1031.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-0782.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-0284.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-0254.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-0255.html  
- Extracting hotfixes from https://rhn.redhat.com/errata/RHSA-2015-0113.html  

