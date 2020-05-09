#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="the file for the xml profile to be converted")
parser.add_argument("shiftstate", help="which shiftstate to translate from profile", nargs='?', const="1", type=str, default="1")
args = parser.parse_args()

with open('translate.Logi2G13d.list', 'r') as translateFile:
    logi2G13d = dict([line.split() for line in translateFile])

with open('translate.GButton2Direction.list', 'r') as translateFile:
    gButton2Direction = dict([line.split() for line in translateFile])

def logi2G13dKeypressTranslate(logitechKeypress):
    if logitechKeypress in logi2G13d.keys():
        g13Keypress = logi2G13d.get(logitechKeypress)
    else:
        g13Keypress = logitechKeypress
    return(g13Keypress)

def gButton2DirectionKeypressTranslate(logitechButton):
    if logitechButton in gButton2Direction.keys():
        g13Button = gButton2Direction.get(logitechButton)
    else:
        g13Button = logitechButton
    return(g13Button)

with open(args.file, 'r') as xmlFile:
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    profileName = root.find("./"
    "{http://www.logitech.com/Cassandra/2010.7/Profile}profile").attrib['name']
    assignmentsG13All = root.findall(".//"
    "*[@devicecategory='Logitech.Gaming.LeftHandedController']/"
    "{http://www.logitech.com/Cassandra/2010.7/Profile}assignment")
    assignmentsG13 = []
    for assignmentAll in assignmentsG13All:
        #restricting to one shiftstate... ugh
        if \
        1 <= int(assignmentAll.attrib['contextid'].strip('G')) <= 29 and \
        ( assignmentAll.attrib['shiftstate'] == args.shiftstate or \
        assignmentAll.attrib['shiftstate'] == None ) and \
        ( assignmentAll.attrib['backup'] == "false" or \
        assignmentAll.attrib['backup'] == None ):
            assignmentsG13.append(assignmentAll)
        else:
            print(f"Missed constraint:\n{assignmentAll.attrib}")
    if not assignmentsG13:
        print(f"Are there no keys assigned to the sought-after shiftstate"
        f" {args.shiftstate}?")
    buttonAssignment = []
    for assignment in assignmentsG13:
        assignmentDictG13 = {}
        assignmentDictG13['buttonID'] = assignment.attrib['contextid']
        assignmentDictG13['macroElements'] = root.findall("./*/*/"
        "*[@guid='{}']/".format(assignment.attrib['macroguid']))
        buttonAssignment.append(assignmentDictG13.copy())
    bindSets = []
    for mappingIndex in buttonAssignment:
        bindSet = {}
        bindSet['buttonG13'] = gButton2DirectionKeypressTranslate(mappingIndex['buttonID'])
        for macrotype in mappingIndex['macroElements']:
            #prints Element of keystroke: print(macroIndex)
            if '{http://www.logitech.com/Cassandra/2010.1/Macros/Keystroke}keystroke' in macrotype.tag:
                #handle key and modifier
                for keystroke in macrotype:
                    if '{http://www.logitech.com/Cassandra/2010.1/Macros/Keystroke}key' in keystroke.tag:
                        bindSet['keypress'] = logi2G13dKeypressTranslate(keystroke.attrib['value'])
                    elif '{http://www.logitech.com/Cassandra/2010.1/Macros/Keystroke}modifier' in keystroke.tag:
                        bindSet['modifier'] = logi2G13dKeypressTranslate(keystroke.attrib['value'])
            elif '{http://www.logitech.com/Cassandra/2010.1/Macros/MouseFunction}mousefunction' in macrotype.tag:
                #handle mousefunction
                for mousefunction in macrotype:
                    if '{http://www.logitech.com/Cassandra/2010.1/Macros/MouseFunction}do' in mousefunction.tag:
                        bindSet['mousetask'] = mousefunction.attrib['task']
            elif '{http://www.logitech.com/Cassandra/2010.1/Macros/MultiKey}multikey' in macrotype.tag:
                #handle multikey
                bindSet['mkey'] = []
                for multikey in macrotype.findall("./"):
                    if '{http://www.logitech.com/Cassandra/2010.1/Macros/MultiKey}key' in multikey.tag:
                        if multikey.attrib['direction'] == 'down':
                            bindSet['mkey'].append(logi2G13dKeypressTranslate(multikey.attrib['value']))
            else:
                print(f'{macrotype}: not implemented!')
                bindSet['keypress'] = 'unimplemented'
            bindSets.append(bindSet.copy())

if bindSets:
    import pprint
    pprint.pprint(bindSets)

    with open(f'{profileName}_shiftstate{args.shiftstate}.bind', 'w') as bindFile:
        for buttonSet in bindSets:
            if 'unimplemented' in buttonSet.values():
                bindFile.write(f"#bind {buttonSet['buttonG13']} {buttonSet['keypress']}: see xml to self-implement\n")
            elif 'mkey' in buttonSet.keys():
                KEYStrList = []
                for key in buttonSet['mkey']:
                    KEYStr = "KEY_" + key
                    KEYStrList.append(KEYStr)
                mkeyBindStr = f"bind {buttonSet['buttonG13']} "
                mkeyKEYStr = "+".join(KEYStrList)
                mkeyStr = mkeyBindStr + mkeyKEYStr
                bindFile.write(mkeyStr + "\n")
            elif not 'modifier' in buttonSet.keys():
                bindFile.write(f"bind {buttonSet['buttonG13']} KEY_{buttonSet['keypress']}\n")
            elif 'keypress' and 'modifier' in buttonSet.keys():
                bindFile.write(f"bind {buttonSet['buttonG13']} KEY_{buttonSet['modifier']}+KEY_{buttonSet['keypress']}\n")
            elif 'mousetask' in buttonSet:
                bindFile.write(f"#bind {buttonSet['buttonG13']} {buttonSet['mousetask']} #would need to rewrite if mouse ever becomes supported\n")
            else:
                print(f"unable to bind {buttonSet['buttonG13']} and {buttonSet['keypress']} because not a keypress!\n")
