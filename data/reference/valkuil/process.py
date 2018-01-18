#!/usr/bin/env python3

#!/usr/bin/env python3
import clam.common.client
import clam.common.data
import clam.common.status
import glob
import random
import time
import sys
import os
import argparse

parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-d','--inputdir', type=str,help="Directory with input documents", action='store',required=True)
parser.add_argument('-u','--username', type=str,help="Username for LST Webservices", action='store',required=True)
parser.add_argument('-p','--password',type=str,help="Password for LST Webservices", action='store',required=True)
args = parser.parse_args()
#args.storeconst, args.dataset, args.num, args.bar
#create client, connect to server.
#the latter two arguments are required for authenticated webservices, they can be omitted otherwise
#if you use SSL (https) and SSL verification fails, you can pass a verify= parameter with the path to your certificate of certificate authority bundle

clamclient = clam.common.client.CLAMClient("https://webservices-lst.science.ru.nl/valkuil", args.username, args.password)

project = "valkuil" + str(random.getrandbits(64))

clamclient.create(project)

data = clamclient.get(project)

for inputfile in glob.glob(os.path.join(args.inputdir, '*.folia.xml')):
    print("Uploading " + os.path.basename(inputfile),file=sys.stderr)
    clamclient.addinputfile(project, data.inputtemplate("foliainput"), inputfile)

data = clamclient.start(project, sensitivity=0.75)

#Always check for parameter errors! Don't just assume everything went well! Use startsafe() instead of start
#to simply raise exceptions on parameter errors.
if data.errors:
    print("An error occured: " + data.errormsg, file=sys.stderr)
    for parametergroup, paramlist in data.parameters:
        for parameter in paramlist:
            if parameter.error:
                print("Error in parameter " + parameter.id + ": " + parameter.error, file=sys.stderr)
    clamclient.delete(project) #delete our project (remember, it was temporary, otherwise clients would leave a mess)
    sys.exit(1)



#If everything went well, the system is now running, we simply wait until it is done and retrieve the status in the meantime
while data.status != clam.common.status.DONE:
    time.sleep(5) #wait 5 seconds before polling status
    data = clamclient.get(project) #get status again
    print("\tRunning: " + str(data.completion) + '% -- ' + data.statusmessage, file=sys.stderr)

#Iterate over output files
for outputfile in data.output:
    try:
        outputfile.loadmetadata() #metadata contains information on output template
    except:
        continue

    outputtemplate = outputfile.metadata.provenance.outputtemplate_id

	#You can check this value against the following predefined output templates, and determine desired behaviour based on the output template:
	#if outputtemplate == "foliaoutput": #FoLiA Document with spelling suggestions (FoLiAXMLFormat)
    if outputtemplate == "foliaoutput": #FoLiA Document with spelling suggestions (FoLiAXMLFormat)
        #Download the remote file
        localfilename = os.path.basename(str(outputfile))
        print("Downloading " + localfilename + "...",file=sys.stderr)
        outputfile.copy(localfilename)

#delete the project (otherwise it would remain on server and clients would leave a mess)
clamclient.delete(project)


