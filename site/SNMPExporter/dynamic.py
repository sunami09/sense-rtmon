import yaml
import sys
import subprocess
import os

print("Parsing config file...")
# Load yaml config file as dict
owd = os.getcwd()
os.chdir("..")
os.chdir("..")
config_path = str(os.path.abspath(os.curdir)) +"/config"
infpth = config_path + "/config.yml"
os.chdir(owd)
data = {}

# argument given
if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
    file_path = config_path + "/" + file_name
    print(f"\n Config file {file_path}\n")
    with open(file_path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"\n Config file {file_path} could not be found in the config directory\n")
else: # default config file
    with open(infpth, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"\n Config file {infpth} could not be found in the config directory\n")

print("Collecting SNMP generator template...")
print("Reading SNMP OIDs/Interfaces/Scrape Duration/Scrape Time from config file...")

# SNMP scraps 1 switche
if(data['switchNum']) == 1:
    with open('./templates/generatorTemplate.yml') as inGen, open('generator.yml', 'w') as outGen:
        for line in inGen:
            outGen.write(line)
    oids = set(data['snmpMetrics']['oids'])
    # read all oids in first then add to generator file
    snip = ""
    for oid in oids:
        snip = snip + "      - " + str(oid) + "\n"

    with open('generator.yml', 'r') as gen:
        text = gen.readlines()
    text[3] = snip
    with open('generator.yml', 'w') as genOut:
        genOut.writelines(text)
        
    replacements = {'RETRY': str(data['snmpMetrics']['retries']),
                    'TIMEOUT': str(data['snmpMetrics']['scrapeTimeout']),
                    'COMMUNITYREADSTRING': str(data['snmpMetrics']['communityString'])}
    
    # Read in the file
    with open('generator.yml', 'r') as file:
        filedata = file.read()
    # Replace the target string
    for k,v in replacements.items():
        filedata = filedata.replace(k, v)
    # Write the file out again
    with open('generator.yml', 'w') as file:
        file.write(filedata)
    dir = str(os.getcwd())
    genLoc = dir + "/src/github.com/prometheus/snmp_exporter/generator"
    genCmd = "yes | cp -rfa generator.yml " + genLoc
    subprocess.run(genCmd, shell=True)
    print("Generating dynamic SNMP config file...")
    subprocess.run("./generator generate", shell=True, cwd=genLoc)
    subprocess.run("yes | cp -rfa snmp.yml ../../../../../", shell=True, cwd=genLoc)
    print("Success! Configured custom SNMP Exporter container")
    
# SNMP scraps 2 switches
elif(data['switchNum']) == 2:
    # first switch generate snmp.yml file
    with open('./templates/generatorTemplate.yml') as inGen, open('generator.yml', 'w') as outGen:
        for line in inGen:
            outGen.write(line)
    oidsA = set(data['snmpMetricsA']['oids'])
    oidsB = set(data['snmpMetricsB']['oids'])
    # read all oids in first then add to generator file
    snipA = ""
    snipB = ""
    
    for oid in oidsA:
        snipA = snipA + "      - " + str(oid) + "\n"
    for oid in oidsB:
        snipB = snipB + "      - " + str(oid) + "\n"

    with open('generator.yml', 'r') as gen:
        text = gen.readlines()
    text[3] = snipA
    with open('generator.yml', 'w') as genOut:
        genOut.writelines(text)
        
    replacements = {'RETRY': str(data['snmpMetricsA']['retries']),
                    'TIMEOUT': str(data['snmpMetricsA']['scrapeTimeout']),
                    'COMMUNITYREADSTRING': str(data['snmpMetricsA']['communityString'])}

    print("create first snmp.yml file")
    with open('generator.yml', 'r') as file:
        filedata = file.read()
    for k,v in replacements.items():
        filedata = filedata.replace(k, v)
    with open('generator.yml', 'w') as file:
        file.write(filedata)        
    dir = str(os.getcwd())
    genLoc = dir + "/src/github.com/prometheus/snmp_exporter/generator"
    genCmd = "yes | cp -rfa generator.yml " + genLoc
    subprocess.run(genCmd, shell=True)
    print("Generating dynamic SNMP config file...")
    subprocess.run("./generator generate", shell=True, cwd=genLoc)
    subprocess.run("yes | cp -rfa snmp.yml ../../../../../", shell=True, cwd=genLoc)
    
    # Second switch generate snmp.yml file
    print("create second snmp.yml file")
    with open('./templates/generatorTemplate.yml') as inGen, open('generator.yml', 'w') as outGen:
        for line in inGen:
            outGen.write(line)
    with open('generator.yml', 'r') as gen:
        text = gen.readlines()
    text[3] = snipA
    with open('generator.yml', 'w') as genOut:
        genOut.writelines(text)
        
    replacements = {'RETRY': str(data['snmpMetricsB']['retries']),
                    'TIMEOUT': str(data['snmpMetricsB']['scrapeTimeout']),
                    'COMMUNITYREADSTRING': str(data['snmpMetricsB']['communityString'])}
    
    with open('generator.yml', 'r') as file:
        filedata = file.read()
    for k,v in replacements.items():
        filedata = filedata.replace(k, v)
    with open('generator.yml', 'w') as file:
        file.write(filedata)    
    genCmd = "yes | cp -rfa generator.yml " + genLoc
    subprocess.run(genCmd, shell=True)
    print("Generating dynamic SNMP config file...")
    subprocess.run("./generator generate", shell=True, cwd=genLoc)
    subprocess.run("yes | cp -rfa snmp.yml ../../../../../snmp2.yml", shell=True, cwd=genLoc)
    print("Success! Configured custom SNMP Exporter container")
else:
    print("invilad switch number")
    exit