#! /usr/bin/python -u
'''
#-------------------------------------------------------------------------------
#
# Copyright 2016 Cumulus Networks, Inc.  all rights reserved
#
# This pass_persist script handles IEEE8023-LAG-MIB and displays
# two main tables: dot3adAggTable and dot3adAggPortListTable.
#
# To use this script, place the file in
# /usr/share/snmp, change the permissions (chmod 755) and edit
# /etc/snmp/snmpd.conf and add the following two lines:
#
#        view   systemonly  included   .1.2.840.10006.300.43
#        pass_persist .1.2.840.10006.300.43 /usr/share/snmp/ieee8023_lag_pp.py
#
#-------------------------------------------------------------------------------
'''
import subprocess
import syslog
import json
import glob
import pprint
import time
import string
import snmp_passpersist as snmp

oid_base = '.1.2.840.10006.300.43'

syslog_already_logged = False

def mac_octet(mac=None):
    if mac:
        return mac.replace(':', ' ')
    else:
        return '00 00 00 00 00 00'

def get_octetstring(portlist=None):
    '''
    Given a list of port numbers, we create
    a set of hex characters as a string.  The first octet is a bitmap
    of ports 1-8, the second octet ports 9-16 and so on with port 1 as the
    most significant bit.
    For example, a list of ports [1, 5, 17] gives "88 00 80"
    or, more obvious in binary 10001000 00000000 1000000 where bits
    are set to one in positions 1, 5, and 17.
    '''
    if portlist is None:
        portlist = []
    portbin = [(1 << (i-1)) for i in portlist]
    portsum = sum(portbin)
    # now reverse the binary number, removing the "0b"
    revbin = bin(portsum)[:1:-1]
    # we might need to pad to the end with zeros to make a byte
    padding = (8 - (len(revbin) % 8)) % 8
    paddedrevbin = '%s%s' % (revbin, padding*'0')
    # take the padded binary string in chunks of 8 bits and
    # convert it to a hex
    # string with spaces between the bytes for an snmp octet string
    paddedegressports = ' '.join([('%02x' % int(paddedrevbin[i:i+8], 2))
                                  for i in range(0, len(paddedrevbin), 8)])
    return paddedegressports

def get_octetports(slaveList=[]):
    # given a list of bond slave arrays, grab the ifindex of each one
    if not slaveList:
        return '00'
    portlist = [bp.get('ifindex', 0) for bp in slaveList]
    return (get_octetstring(portlist))

def get_aggOrInd(numports=0):
    if numports > 1:
        # if there is one port, return true(1)
        return 1
    else:
        # return false(2)
        return 2

def state_format(x=0):
    return '{:02x}'.format(int(x))

def get_json_output(commandList=None):
    '''
    This grabs the JSON output of a CLI command and returns an array.
    '''
    global syslog_already_logged
    outArray = {}
    if (not commandList) or (commandList == []):
        syslog.syslog('Error: called get_json_output with'
                      ' invalid command=%s' % \
                      commandList)
        syslog_already_logged = True
        return {}
    try:
        outArray = json.loads(subprocess.check_output((commandList),
                                                      shell=False),
                              encoding="latin-1")
    except Exception as e:
        outArray = {}
        syslog.syslog('Error: command %s EXCEPTION=%s' % \
                      (' '.join(commandList), e))
        syslog_already_logged = True
    return outArray

# this handles both the dot3adAggTable and the dot3adAggPortListTable
aggEntryArray = {
    'dot3adAggIndex' : {'function': 'add_int', 'default': 0, 'oid': 1,
                        'attribute' : 'ifindex'},
    'dot3adAggMACAddress' : {'function': 'add_oct', 'attribute' : 'address',
                             'default': '00:00:00:00:00:00', 'oid': 2,
                             'modifier': mac_octet},
    'dot3adAggActorSystemPriority' : {'function': 'add_int', 'default': 0,
                                      'attribute' : 'system_priority',
                                      'oid': 3},
    'dot3adAggActorSystemID' : {'function': 'add_oct',
                                'default': '00:00:00:00:00:00',
                                'attribute' : 'system_mac_address',
                                'oid': 4,
                                'modifier': mac_octet},
    'dot3adAggAggregateOrIndividual' : {'function': 'add_int', 'default': 0,
                                        'attribute' : 'number_of_ports',
                                        'oid': 5,
                                        'modifier': get_aggOrInd},
    'dot3adAggActorAdminKey' : {'function': 'add_int', 'default': 0, 'oid': 6,
                                'attribute' : None},
    'dot3adAggActorOperKey' : {'function': 'add_int', 'default': 0, 'oid': 7,
                               'attribute' : 'ifindex'},
    'dot3adAggPartnerSystemID' : {'function': 'add_oct', 'default': '00:00:00:00:00:00',
                                  'attribute' : 'partner_mac_address',
                                  'oid': 8,
                                  'modifier': mac_octet},
    'dot3adAggPartnerSystemPriority' : {'function': 'add_int', 'default': 0, 'oid': 9,
                                        'attribute' : None},
    'dot3adAggPartnerOperKey' : {'function': 'add_int', 'default': 0, 'oid': 10,
                                 'attribute' : 'partner_key'},
    'dot3adAggCollectorMaxDelay' : {'function': 'add_int', 'default': 0, 'oid': 11,
                                    'attribute' : None},
    # this is for the one entry in the dot3adAggPortListEntry
    'dot3adAggPortListEntry' : {'function': 'add_oct', 'default': '', 'oid': 1,
                                'attribute' : 'bond_port_list',
                                'modifier': get_octetports},
    }

aggEntryList = ['dot3adAggIndex', 'dot3adAggMACAddress',
                'dot3adAggActorSystemPriority', 'dot3adAggActorSystemID',
                'dot3adAggAggregateOrIndividual', 'dot3adAggActorAdminKey',
                'dot3adAggActorOperKey', 'dot3adAggPartnerSystemID',
                'dot3adAggPartnerSystemPriority', 'dot3adAggPartnerOperKey',
                'dot3adAggCollectorMaxDelay']

adAggPortListList = ['dot3adAggPortListEntry']

aggPortEntryArray = {
    'dot3adAggPortIndex' : {'function': 'add_int',
                            'default': 0, 'oid': 1,
                            'attribute' : 'ifindex'},
    'dot3adAggPortActorSystemPriority' : {'function': 'add_int', 'default': 0,
                                          'attribute' : 'actor_system_priority',
                                          'oid': 2},
    'dot3adAggPortActorSystemID' : {'function': 'add_oct',
                                    'default': '00:00:00:00:00:00',
                                    'attribute' : 'actor_system_mac_address',
                                    'oid': 3,
                                    'modifier': mac_octet},
    'dot3adAggPortActorAdminKey' : {'function': 'add_int',
                                    'default': 0, 'oid': 4,
                                    'attribute' : None},  # needs actor_admin_key
    'dot3adAggPortActorOperKey' : {'function': 'add_int',
                                   'default': 0, 'oid': 5,
                                   'attribute' : 'masterifindex'},
    'dot3adAggPortPartnerAdminSystemPriority' : {'function': 'add_int',
                                                 'default': 0, 'oid': 6,
                                                 'attribute' : None}, # needs actor_admin_system_priority
    'dot3adAggPortPartnerOperSystemPriority' : {'function': 'add_int',
                                                'default': 0, 'oid': 7,
                                                'attribute' : 'parter_system_priority'},
    'dot3adAggPortPartnerAdminSystemID' : {'function': 'add_oct',
                                           'default': '00:00:00:00:00:00',
                                           'attribute' : None,  # needs partner_admin_sytem_mac_address
                                           'oid': 8,
                                           'modifier': mac_octet},
    'dot3adAggPortPartnerOperSystemID' : {'function': 'add_oct',
                                          'default': '00:00:00:00:00:00',
                                          'attribute' : 'partner_system_mac_address',
                                          'oid': 9,
                                          'modifier': mac_octet},
    'dot3adAggPortPartnerAdminKey' : {'function': 'add_int',
                                      'default': 0, 'oid': 10,
                                      'attribute' : None},   # needs partner_admin_key
    'dot3adAggPortPartnerOperKey' : {'function': 'add_int',
                                     'default': 0, 'oid': 11,
                                     'attribute' : 'partner_oper_key'},
    'dot3adAggPortSelectedAggID' : {'function': 'add_int',
                                    'default': 0, 'oid': 12,
                                    'attribute' : 'aggregator_id'},
    'dot3adAggPortAttachedAggID' : {'function': 'add_int',
                                    'default': 0, 'oid': 13,
                                    'attribute' : None},   # not sure where this comes from
    'dot3adAggPortActorPort' : {'function': 'add_int',
                                'default': 0, 'oid': 14,
                                'attribute' : 'actor_port_number'},
    'dot3adAggPortActorPortPriority' : {'function': 'add_int',
                                        'default': 0, 'oid': 15,
                                        'attribute' : 'actor_port_priority'},
    'dot3adAggPortPartnerAdminPort' : {'function': 'add_int',
                                       'default': 0, 'oid': 16,
                                       'attribute' : None},   # needs parter_admin_port
    'dot3adAggPortPartnerOperPort' : {'function': 'add_int',
                                      'default': 0, 'oid': 17,
                                      'attribute' : 'partner_port_number'},
    'dot3adAggPortPartnerAdminPortPriority' : {'function': 'add_int',
                                               'default': 0, 'oid': 18,
                                               'attribute' : None},  # needs admin_partner_port_priority
    'dot3adAggPortPartnerOperPortPriority' : {'function': 'add_int',
                                              'default': 0, 'oid': 19,
                                              'attribute' : 'partner_port_priority'},
    'dot3adAggPortActorAdminState' : {'function': 'add_oct',
                                      'default': 0, 'oid': 20,
                                      'modifier': state_format,
                                      'attribute' : None},   # needs actor_admin_port_state
    'dot3adAggPortActorOperState' : {'function': 'add_oct',
                                     'default': 0, 'oid': 21,
                                     'modifier': state_format,
                                     'attribute' : 'actor_port_state'},
    'dot3adAggPortPartnerAdminState' : {'function': 'add_oct',
                                        'default': 0, 'oid': 22,
                                        'modifier': state_format,
                                        'attribute' : None},   # needs partner_admin_port_state
    'dot3adAggPortPartnerOperState' : {'function': 'add_oct',
                                       'default': 0, 'oid': 23,
                                       'modifier': state_format,
                                       'attribute' : 'partner_port_state'},
    'dot3adAggPortAggregateOrIndividual' : {'function': 'add_int', 'default': 0,
                                            'attribute' : 'number_of_ports',
                                            'oid': 24,
                                            'modifier': get_aggOrInd}}
aggPortEntryList = ['dot3adAggPortIndex',
                    'dot3adAggPortActorSystemPriority',
                    'dot3adAggPortActorSystemID',
                    'dot3adAggPortActorAdminKey',
                    'dot3adAggPortActorOperKey',
                    'dot3adAggPortPartnerAdminSystemPriority',
                    'dot3adAggPortPartnerOperSystemPriority',
                    'dot3adAggPortPartnerAdminSystemID',
                    'dot3adAggPortPartnerOperSystemID',
                    'dot3adAggPortPartnerAdminKey',
                    'dot3adAggPortPartnerOperKey',
                    'dot3adAggPortSelectedAggID',
                    'dot3adAggPortAttachedAggID',
                    'dot3adAggPortActorPort',
                    'dot3adAggPortActorPortPriority',
                    'dot3adAggPortPartnerAdminPort',
                    'dot3adAggPortPartnerOperPort',
                    'dot3adAggPortPartnerAdminPortPriority',
                    'dot3adAggPortPartnerOperPortPriority',
                    'dot3adAggPortActorAdminState',
                    'dot3adAggPortActorOperState',
                    'dot3adAggPortPartnerAdminState',
                    'dot3adAggPortPartnerOperState',
                    'dot3adAggPortAggregateOrIndividual']

# some variables we will be using taken from IEEE8023-LAG-MIB
lagMIBObjects = '1'
dot3adAgg = '1'                 # 1.1
dot3adAggTable = '1'            # 1.1.1
dot3adAggEntry = '1'            # 1.1.1.1

dot3adAggPortListTable = '2'    # 1.1.2
dot3adAggPortListEntry = '1'    # 1.1.2.1
dot3adAggPortListPorts = '1'    # 1.1.2.1.1

dot3adAggPort = '2'             # 1.2
dot3adAggPortTable = '1'        # 1.2.1
dot3adAggPortEntry = '1'        # 1.2.1.1

dot3adAggPortStatsTable = '2'   # 1.2.2
dot3adAggPortStatsEntry = '1'   # 1.2.2.1

dot3adTablesLastChanged = '3'

def update():
    '''
    This is the main method that will be called periodically.  This grabs the
    output of showbondattrs and provides the agent with various tables.
    '''
    # this returns a list (in order by ifindex) of bond arrays
    bondJson = get_json_output(commandList=['sudo','/usr/share/snmp/showprocnetbonding'])

    # Handle the dot3adAggTable and dot3adAggPortListTable  43.1.1.1 43.1.1.2
    for table,tableEntry,entryList in [
        [dot3adAggTable, dot3adAggEntry, aggEntryList],
        [dot3adAggPortListTable, dot3adAggPortListEntry, adAggPortListList]]:
        for entry in entryList:
            for bondArray in bondJson.get('bond_list', []):
                myfunc = getattr(pp, aggEntryArray[entry]['function'])

                # get the value or a default
                #if aggEntryArray[entry].get('attribute', None):
                value = bondArray.get(aggEntryArray[entry].get('attribute', None),
                                      aggEntryArray[entry]['default'])
                # for some things that need modifying...like MACs or slaves)
                if aggEntryArray[entry].get('modifier', None):
                    value = aggEntryArray[entry]['modifier'](value)
                # Now show it
                myfunc('%s.%s.%s.%s.%s.%s' % \
                       (lagMIBObjects, dot3adAgg, table,
                        tableEntry, aggEntryArray[entry]['oid'],
                        bondArray['ifindex']), value)

    # Handle the dot3adAggPort .1.2.840.10006.300.43.1.2  We show dot3adAggPortTable(1)
    # this is indexed by the bond ports
    # create an array of bondports indexed by ifindex
    bondportArray = {}
    for bond in bondJson['bond_list']:
        for bondport in bond['bond_port_list']:
            bondportArray.setdefault(bondport['ifindex'], bondport)

    ifindexList = bondportArray.keys()
    ifindexList.sort()
    for entry in aggPortEntryList:
        for ifindex in ifindexList:
            myfunc = getattr(pp, aggPortEntryArray[entry]['function'])
            bondport = bondportArray.get(ifindex, {})
            # get the value or a default
            value = bondport.get(aggPortEntryArray[entry].get('attribute', None),
                                 aggPortEntryArray[entry]['default'])
            # for some things that need modifying, like MACs or slaves, call the function
            if aggPortEntryArray[entry].get('modifier', None):
                value = aggPortEntryArray[entry]['modifier'](value)
            # Now show it
            myfunc('%s.%s.%s.%s.%s.%s' % \
                   (lagMIBObjects, dot3adAggPort, dot3adAggPortTable,
                    dot3adAggPortEntry, aggPortEntryArray[entry]['oid'],
                    ifindex), value)
    return
################################################################################

pp = snmp.PassPersist(oid_base)
pp.debug = False

if pp.debug:
    # just run the update script once and print debugs to stdout
    update()
else:
    pp.start(update, 60)
