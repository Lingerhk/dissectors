from scapy.all import Packet, rdpcap, ConditionalField, Emph, conf
import binascii # this class to handle the hex/ascii converting
'''
imported files from Scapy library
'''
from scapy.layers.dot11 import *
from scapy.layers.ir import *
from scapy.layers.ppp import *
from scapy.layers.gprs import *
from scapy.layers.mobileip import *
from scapy.layers.smb import *
from scapy.layers.bluetooth import *
from scapy.layers.isakmp import *
from scapy.layers.radius import *
from scapy.layers.hsrp import *
from scapy.layers.netbios import *
from scapy.layers.snmp import *
from scapy.layers.dhcp6 import *
from scapy.layers.l2 import *
from scapy.layers.rip import *
from scapy.layers.inet6 import *
from scapy.layers.netflow import *
from scapy.layers.tftp import *
from scapy.layers.dhcp import *
from scapy.layers.l2tp import *
from scapy.layers.rtp import *
from scapy.layers.inet import *
from scapy.layers.ntp import *
from scapy.layers.x509 import *
from scapy.layers.dns import *
from scapy.layers.llmnr import *
from scapy.layers.sebek import *
from scapy.layers.pflog import *
from scapy.layers.dot11 import *
from scapy.layers.mgcp import *
from scapy.layers.skinny import *
'''
import the protocols classes
'''
from ftp import *
from http import *
from imap import *
from irc import *
from pop import *
from sip import *
from smtp import *
from ssh import *
from telnet import *

def int2bin(n, count=16):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

class Dissector(Packet):
    """
    this is the main class of this library
    Note:
    implemented protocols like http,sip, (usually or sometimes) return binary
    data, and in some other cases return human readable data,
    so i have decided to make these protocols return the data represented as
    a hex values, you may want to have its payload in ascii too if so then
    use get_ascii()
    """
    packet = None
    type = 0
    gn = 0
    def get_ascii(self, hexstr):
        """
        get hex string and returns ascii chars
        @param hexstr: hex value in str format
        """
        return binascii.unhexlify(hexstr)

    def defined_protocol(self, name):
        if name.startswith("tcp") or name.startswith("udp") or name.startswith("icmp") or name.startswith("dns") or name.startswith("http") or name.startswith("ftp") or name.startswith("irc") or name.startswith("smb") or name.startswith("sip") or name.startswith("telnet") or name.startswith("smtp") or name.startswith("ssh") or name.startswith("imap") or name.startswith("pop"):
            return True

    def clean_out(self,value):
        value = value.rstrip()
        value = value.lstrip()
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        elif value.startswith("'") and not value.endswith("'"):
            return value[1:]
        elif value.endswith("'") and not value.startswith("'"):
            return value[:-1]
        else:
            return value
    def hex_it(self, s):
        """
        get ascii chars and returns hex string
        @param s: ascii chars
        """
        for c in s:
            ustruct = struct.unpack(self.fmt, c)
            byte = str(hex(ustruct[0]))[2:]
            if len(byte) == 1:
                byte = "0" + byte
            self.myres = self.myres + byte
        return s

    def dissect(self, packet):
        """
        this is the main method in the library, which dissects packets and
        returns them as a list of protocols' fields.
        @param pcapfile: path to a pcap/cap library
        """
        ct = conf.color_theme
        flds = []
        flds.append(ct.layer_name(packet.name))

        for f in packet.fields_desc:
                if isinstance(f, ConditionalField) and not f._evalcond(self):
                    continue
                if isinstance(f, Emph) or f in conf.emph:
                    ncol = ct.emph_field_name
                    vcol = ct.emph_field_value
                else:
                    ncol = ct.field_name
                    vcol = ct.field_value

                fvalue = packet.getfieldval(f.name)
                flds.append((ncol(f.name), vcol(f.i2repr(self, fvalue))))
        return flds

    def is_printable(self,f):
        if isinstance(f, tuple) and not f[1] == "''" and not f[1] == '' and not f[1] == "" and not f[1] == [] and not f[1] == '[]' and not f[1] == "[]" and len(f[1]) > 0:
            return True
        return False

    def __getattr__(self, attr):
        if self.initialized:
            fld,v = self.getfield_and_val(attr)
            if fld is not None:
                return fld.i2h(self, v)
            return v
        # raise AttributeError(attr)
        


    def dissect_pkts(self, pcapfile):
        """
        this method act as an interface for the dissect() method.
        and to represents the data in the required format.
        @param pcapfile: path to a pcap/cap library
        """
        packetslist = rdpcap(pcapfile)
        pktsfields = []
        protocols = []
        entry = {}
        recognized = False
        for pkt in packetslist:
            firstlayer = True
            if pkt:
                # pktsfields.append("NewPacket")
                if firstlayer:
                    firstlayer = False
                    self.packet = pkt
                    fields = self.dissect(self.packet)

                    j = 1
                    entry = {}
                    while j < len(fields):
                        if self.is_printable(fields[j]):
                            entry[fields[j][0]] = fields[j][1]
                        j = j + 1
                    # pktsfields.append(fields)
                    
                    i = 0
                    while i < len(protocols):
                        if fields[0] in protocols[i]:
                            protocols[i].append(entry)
                            break
                        elif fields[0] not in protocols[i] and \
                        i == len(protocols) - 1:
                            protocols.append([fields[0]])
                            protocols[i + 1].append(entry)
                            break
                        i = i + 1
                    if len(protocols) == 0:
                        protocols.append([fields[0]])
                        protocols[0].append(entry)

                load = pkt
                while load.payload:
                    load = load.payload
                    self.packet = load
                    
                    fields = self.dissect(self.packet)

                    
                    
                    entry = {}
                    # pktsfields.append(fields)
                    if fields[0]:
                        if fields[0] == "NoPayload":
                            break
                        
# pkt.underlayer.underlayer.fields["src"]
                    j = 1
                    first = True
                    if not recognized:
                        entry = {}
                    while j < len(fields):
                        if self.is_printable(fields[j]):
                            if fields[0] == "UDP":
                                recognized = True
                                entry["src"] = load.underlayer.fields["src"]
                                entry["dst"] = load.underlayer.fields["dst"]
                                entry["sdport"] = load.fields["sport"]
                                entry["dport"] = load.fields["dport"]
                            if fields[0] == "TCP":
                                recognized = True
                                entry["src"] = load.underlayer.fields["src"]
                                entry["dst"] = load.underlayer.fields["dst"]
                                entry["sdport"] = load.fields["sport"]
                                entry["dport"] = load.fields["dport"]

                            if fields[0] == "DNS":
                                recognized = True
                                qdfield = None
                                anfield = None
                                type = None
                                name = None
                                pname = None
                                found = False
                                entry = []
                                if load.fields["qd"] :
                                    for element in fields:
                                        if "qd" in element:
                                            qdfield = element[1]
                                            #break
                                    if qdfield.count("|") == 1:
                                        line = qdfield.split()
                                        for t in line:
                                            if t.startswith("qname="):
                                                found = True
                                                name = t[6:]
                                            if t.startswith("qtype="):
                                                found = True
                                                type = t[6:]
                                        if found:
                                            entry.append({"name": name, "type": type})
                                            found = False

                                    if qdfield.count("|") > 1:
                                        entry["name"] = []
                                        qlist = qdfield.split(" |")
                                        for record in qlist:
                                            line = record.split()
                                            for t in line:
                                                if t.startswith("qname="):
                                                    found = True
                                                    name = t[6:]
                                                if t.startswith("qtype="):
                                                    found = True
                                                    type = t[6:]
                                            if found:
                                                entry.append({"name": name, "type": type})
                                                found = False
                                            
                                if load.fields["an"] :
                                    for element in fields:
                                        if "an" in element:
                                            anfield = element[1]
                                            #break
                                    if anfield.count("|") == 1:
                                        line = anfield.split()
                                        for t in line:
                                            if t.startswith("rrname="):
                                                found = True
                                                name = t[7:]
                                            if t.startswith("type="):
                                                found = True
                                                type = t[5:]
                                            if t.startswith("rdata="):
                                                found = True
                                                pname = t[6:]
                                        if found:
                                            entry.append({"name": name, "type": type, "pname": pname})
                                            found = False
                                    if anfield.count("|") > 1:
                                        alist = anfield.split(" |")
                                        for record in alist:
                                            line = record.split()
                                            for t in line:
                                                if t.startswith("rrname="):
                                                    found = True
                                                    name = t[7:]
                                                if t.startswith("type="):
                                                    found = True
                                                    type = t[5:]
                                                if t.startswith("rdata="):
                                                    found = True
                                                    pname = t[6:]
                                            if found:
                                                entry.append({"name": name[1:-2], "type": type, "pname": pname[1:-1]})
                                                found = False
                            
                            if isinstance(fields[0], str) and fields[0].startswith("http"):
                                recognized = True
                                if isinstance(fields[j][1], str):
                                    if first and not fields[j][0][:-2] == "unknown-header(s)" and not fields[j][0][:-2] == "message-body":
                                        entry[fields[j][0][:-2]] = self.clean_out(fields[j][1][len(fields[j][0]) + 1:-1])
                                    elif first and fields[j][0][:-2] == "unknown-header(s)":
                                        entry[fields[j][0][:-2]] = self.clean_out(fields[j][1])
                                    elif first and fields[j][0][:-2] == "message-body":
                                        entry[fields[j][0][:-2]] = fields[j][1]
                                    else:
                                        entry[fields[j][0]] = self.clean_out(fields[j][1])

                            if isinstance(fields[0], str) and\
							fields[0].startswith("sip"):
                                recognized = True
                                if isinstance(fields[j][1], str):
                                    if first and not fields[j][0][:-2] == "unknown-header(s)" and not fields[j][0][:-2] == "message-body":
                                        entry[fields[j][0][:-2]] = self.clean_out(fields[j][1][len(fields[j][0]) + 1:-1])
                                    elif first and fields[j][0][:-2] == "unknown-header(s)":
                                        entry[fields[j][0][:-2]] = self.clean_out(fields[j][1])
                                    elif first and fields[j][0][:-2] == "message-body":
                                        entry[fields[j][0][:-2]] = fields[j][1][1:-1]
                                else:
                                    entry[fields[j][0]] = self.clean_out(self.clean_out(fields[j][1]))
                            
                            if isinstance(fields[0], str) and\
                            fields[0].startswith("smtp"):
                                recognized = True
                                if fields[j][1].startswith("'") and fields[j][1].endswith("'"):
                                    entry[fields[j][0]] = self.clean_out(fields[j][1][1:-1])
                                else:
                                    entry[fields[j][0]] = self.clean_out(self.clean_out(fields[j][1]))
                            
                                
                            if isinstance(fields[0], str) and\
                            fields[0].startswith("ftp"):
                                recognized = True
                                entry[fields[j][0]] = self.clean_out(fields[j][1][1:-1])

                            if isinstance(fields[0], str) and\
							fields[0].startswith("imap"):
                                recognized = True
                                entry = entry + fields[j][1] + " "
                            if isinstance(fields[0], str) and\
							fields[0].startswith("pop"):
                                recognized = True
                                entry = entry + fields[j][1] + " "
                            if isinstance(fields[0], str) and\
							 fields[0].startswith("irc"):
                                recognized = True
                                entry = fields[j][1]
                                
                            if isinstance(fields[0], str) and\
                             fields[0].startswith("telnet"):
                                recognized = True
                                entry = fields[j][1][:-1]
                                
                            if not recognized:
                                entry[fields[j][0]] = self.clean_out(fields[j][1])
                            recognized = False
                        j = j + 1

                    i = 0
                    while i < len(protocols):
                        if fields[0].lower() in protocols[i]:
                            protocols[i].append(entry)
                            break
                        elif fields[0].lower() not in protocols[i] and \
                        i == len(protocols) - 1:
                            protocols.append([fields[0].lower()])
                            protocols[i + 1].append(entry)
                            break
                        i = i + 1
                    if len(protocols) == 0:
                        protocols.append([fields[0].lower()])
                        protocols[0].append(entry)
                

        dproto = {}
        i = 0
        for proto in protocols:

            if self.defined_protocol(proto[0].lower()):
                dproto[proto[0].lower()] = proto[1:]
        
        return dproto