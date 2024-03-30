#!/usr/bin/env python3

# Author: Dylan Boland
#
# Description of the script:
#
# This script gets (extracts) the list of inputs and outputs of a module.
# It returns the names of the inputs and outputs, their dimensions, as well
# their type (i.e., wire or reg).
#
# The I/O (input-output) list is written to an output .csv file. The output file
# has a name with the following format:
#
#               <module_name>_io.csv
#
# You can email the .csv file to yourself by running the following command:
#
#               mail -a <module_name>_io.csv <your_email_address>
#
# Enter a subject for the email. Then, press ctrl + D.
#
#
# The script is called with the '--filename' switch, followed by the name of the Verilog
# module file. Should the Verilog file be located in a different directory, then the path
# to the file can be given. An example of how the script is called:
#
#               get_module_io.py --filename accumulator.v
#


# Modules that will be useful
import argparse
import os
import sys
import re
import csv

# ==== Some General-info Strings ====
# Tags - define these here so they can be quickly and easily changed
errorTag   = """\t***Error: """
successTag = """\t***Success: """
infoTag    = """\t***Info: """

# Standard help & error messages
helpMsg    = infoTag + """The path to the Verilog or SystemVerilog module description should be
given after using the '--filename' switch."""
noArgsMsg  = errorTag + """No input arguments were specified. Please use '--filename' followed
\tby the name of the module to be instantiated."""
noSuchFileMsg   = errorTag + """The module file '{}' could not be located - double-check the name or file path."""
fileReadSuccess = successTag + """The module file was read in successfully."""
fileReadError   = errorTag + """The module file could not be read in successfully."""
moduleNameNotIdentified = errorTag + """The module name could not be identified. Please ensure that you have used
\ta standard or conventional structure. An example is shown below:
            module serialTX #
                (
                parameter INCR = 26'd25770 // amount by which the accumulator is incremented
                )
                (
                input clk,
                input reset,
                input [7:0] data,
                input send,
                output reg txOut,
                output busy
                );
                // The module description or logic goes below
"""
noParamsFound       = infoTag + """No parameters were identified for this module."""
noInputsIdentified  = errorTag + """No module inputs were identified."""
noOutputsIdentified = errorTag + """No module outputs were identified."""

# Instantiated module print-out message
jobDoneMsg = """
\n\n\t===========================================================================================
\t\tThe I/O list for {} can be found in {}!
\t==========================================================================================="""

# Goodbye message
goodbyeMsg = """
\t===========================================================================================
\t\tYou can email this .CSV file to yourself by running:
\t\t mail -a {} <your_email_address>

\t\tEnter a subject for the email and then press ctrl + D
\t==========================================================================================="""

# Some Header (Delimiter) Strings
# These allow us to cleary separate input and
# output ports when instantiating the module
inputPortsHeader = """// ==== Inputs ===="""
outputPortsHeader = """// ==== Outputs ====\n\t"""
paramsHeader = """// ==== Parameters ===="""

# Function to handle the input arguments
def parsingArguments():
    parser = argparse.ArgumentParser(description = "The file containing the Verilog or SystemVerilog module description.")
    parser.add_argument('--filename', type = str, help = helpMsg)
    return parser.parse_args()

if __name__ == "__main__":
    args = parsingArguments() # parse the input arguments (if there are any)
    if len(sys.argv) == 1:
        print(noArgsMsg)
        exit()
    moduleFileName = args.filename # get the file name (or path) from the input arguments
    moduleFileType = os.path.splitext(moduleFileName)[1] # get the file extension type (either ".v" or ".sv")
    # ==== Check if the File (path) Exists ====
    if os.path.isfile(moduleFileName) is False:
        print(noSuchFileMsg.format(moduleFileName))
        exit()
    
    # ==== Try to Read the Module File in ====
    with open(moduleFileName) as p:
        try:
            moduleContents = p.read() # read the file into a string
            print(fileReadSuccess)
        except:
            print(fileReadError)
            exit()
    
    # ==== Define the Patterns to Look For ====
    moduleNamePattern    = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))module\s+(?:\$\[PREFIX\])?([a-zA-Z\_0-9]+)[\n\s]*#?[\n\s]*\(')
    moduleParamsPattern  = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))parameter\s*(?:\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*=')
    moduleInputsPattern  = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))(input){1}\s+(wire\b|reg\b)?\s*(\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]|\$\$\{[a-zA-Z\_]+\}|\$\[[a-zA-Z\_]+\])?\s*(\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]|\$\$\{[a-zA-Z\_]+\}|\$\[[a-zA-Z\_]+\])?\s*([a-zA-Z\_0-9\$\{\}]+)\s*,?')
    moduleOutputsPattern  = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))(output){1}\s+(wire\b|reg\b)?\s*(\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]|\$\$\{[a-zA-Z\_]+\}|\$\[[a-zA-Z\_]+\])?\s*(\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]|\$\$\{[a-zA-Z\_]+\}|\$\[[a-zA-Z\_]+\])?\s*([a-zA-Z\_0-9\$\{\}]+)\s*,?')

    # ==== Extract the Module Name first ====
    matches = re.findall(moduleNamePattern, moduleContents)
    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
        print(moduleNameNotIdentified)
        exit()
    else:
        moduleName = matches[0] # store the module name

    # ==== Extract the Module Inputs ====
    matches = re.findall(moduleInputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noInputsIdentified) # print a message saying that no module inputs were found
    else:
        moduleInputs = matches # capture the list of module inputs
        numInputs = len(matches)
    
    # ==== Extract the Module Outputs ====
    matches = re.findall(moduleOutputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noOutputsIdentified) # print a message saying that no module outputs were found
    else:
        moduleOutputs = matches # capture the list of module outputs
        numOutputs = len(matches)

    # ==== Form the List of Inputs and Outputs ====
    # The dictionaries below will store the information.
    inputDictionary = {}
    outputDictionary = {}
    for i in range(0, numInputs):
        signalType = moduleInputs[i][1] # the 2nd thing that will match in a port declaration is the signal type (i.e., wire or reg)
        signalDimension = moduleInputs[i][2] + moduleInputs[i][3] # after the signal type comes the signal dimension
        signalName = moduleInputs[i][4] # and after the signal dimension comes the signal name
        inputDictionary[signalName] = {"signalType": signalType,
                "signalDimension": signalDimension
                } 
    for i in range(0, numOutputs):
        signalType = moduleOutputs[i][1]
        signalDimension = moduleOutputs[i][2] + moduleOutputs[i][3]
        signalName = moduleOutputs[i][4]
        outputDictionary[signalName] = {"signalType": signalType,
                "signalDimension": signalDimension
                }

    # ==== Write the I/O List to an Output .CSV File ====
    outputCsvFileName = moduleName + "_io.csv"
    with open(outputCsvFileName, 'w') as p:
        writer = csv.writer(p)
        writer.writerow(["Signal Name", "Input/Output", "Signal Type", "Dimension"])
        for key, value in inputDictionary.items():
            signalType = value["signalType"]
            signalDimension = value["signalDimension"]
            writer.writerow([key, "Input", signalType, signalDimension])
        for key, value in outputDictionary.items():
            signalType = value["signalType"]
            signalDimension = value["signalDimension"]
            writer.writerow([key, "Output", signalType, signalDimension])

    # ==== Inform the User of where the List is ====
    print(jobDoneMsg.format(moduleName, outputCsvFileName))
    print(goodbyeMsg.format(outputCsvFileName))
    exit()
