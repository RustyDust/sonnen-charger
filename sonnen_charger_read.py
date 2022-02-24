#######################################################
# Modbus reading Python script.                       #
# More details in excel document                      #
# Etrel INCH (Duo) SmartHome Modbus TCPRegisters.xlsx #
#                                                     #
# Version 1.4                                         #
# March, 2021.                                        #
# Author: Samir Gutic, ETREL doo                      #
#######################################################

#Imports
from pymodbus.client.sync import ModbusTcpClient
import datetime
from struct import *
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

#Initialisations
UNIT = 1
separator=80 #Separator line length
clientPort=502 #Port for modbus connection for reading charger's data
clientPortCluster=503 #Port for modbus connection for reading power management data

#PLEASE CHANGE CHARGER'S IP ADDRESS FIRST
################################################

clientIP="192.168.123.123" #Charger's IP address

################################################

# Read data
# Charger data
try:
    #Try to connect to client
    client = ModbusTcpClient(clientIP, clientPort) #Use port 502 for reading charger's data

    #Print connection info
    print("=" * separator)
    #print("Reading data from INCH or DUO:",client)
    print("Reading data from INCH or DUO, IP address and port: " + str(clientIP) + ":" + str(clientPort))

    print("=" * separator)
    print(">>> CHARGER SETTINGS (5 registers) <<<")
    print("=" * separator)

    #Serial number
    response = client.read_input_registers(address=990,count=10,unit=UNIT) #Response: [12600, 12337, 12336, 12336, 0]
    #print(response.registers)
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers)
    serialNumber=decoder.decode_string(20)
    serialNumber = serialNumber.decode("utf-8")
    print("[990]Serial number: " + str(serialNumber)) 
        
    #Model
    response = client.read_input_registers(address=1000,count=10,unit=UNIT) # Response: [20547, 11569, 23091, 11586, 22829]
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers)
    model=decoder.decode_string(20)
    model = model.decode("utf-8")
    print("[1000]Model: " + str(model))

    #HW version
    response = client.read_input_registers(address=1010,count=5,unit=UNIT) # Response: [0, 0, 0, 0, 0]
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers)
    HWversion=decoder.decode_string(20)
    HWversion = HWversion.decode("utf-8")
    print("[1010]HW version: " + str(HWversion))
    
    #SW version
    response = client.read_input_registers(address=1015,count=5,unit=UNIT) # Response: [12590, 12594, 11829, 0, 0]
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers)
    SWversion=decoder.decode_string(20)
    SWversion = SWversion.decode("utf-8")
    print("[1015]SW version: " + str(SWversion))
    
    #Number of connectors
    response = client.read_input_registers(address=1020,count=2,unit=UNIT) #Response: [1, 0]
    print("[1020]Number of connectors: " + str(response.registers[0]))

    connectors = int(str(response.registers[0]))

    for i in range(1, connectors+1):
        offset = (i-1) * 100

        print("=" * separator)
        print("CONNECTOR {} (6 registers)".format(i))
        print("-" * separator)
        
        #Connector 1 Connector type
        response = client.read_input_registers(address=1022+offset,count=1,unit=UNIT) #Response: [2]

        #Print connector type description (you can write your own decriptions)
        if str(response.registers) == str([1]):
            strType = "SocketType2"                       
        elif str(response.registers) == str([2]):
            strType = "CableType2"
        else:
            strType = "Unknown connector type!"

        print("[{}]Connector {} Connector type: {}".format(1022+offset, i, strType))
        
        #Connector 1 Number phases
        response = client.read_input_registers(address=1023,count=1,unit=UNIT) #Response: [3]
        print("[{}]Connector {} Number of phases: {}".format(1023+offset, i, str(response.registers[0])))

        #Connector 1 L1 connected to phase
        response = client.read_input_registers(address=1024,count=1,unit=UNIT) #Response: [1]
        print("[{}]Connector {} L1 connected to phase: {}".format(1024+offset, i, str(response.registers[0])))

        #Connector 1 L2 connected to phase
        response = client.read_input_registers(address=1025,count=1,unit=UNIT) #Response: [2]
        print("[{}]Connector {} L2 connected to phase: {}".format(1025+offset, i, str(response.registers[0])))

        #Connector 1 L3 connected to phase
        response = client.read_input_registers(address=1026,count=1,unit=UNIT) #Response: [3]
        print("[{}]Connector {} L3 connected to phase: {}".format(1026+offset, i, str(response.registers[0])))

        #Connector 1 Custom max current
        response = client.read_input_registers(address=1028,count=2,unit=UNIT) # Response: [16768, 0]
        #Convert to float and round to 2 decimal places
        cMaxCurrent=pack('>HH',response.registers[0],response.registers[1])    
        fcMaxCurrent = unpack('>f', cMaxCurrent)
        print("[{}]Connector {} Custom max current: {}".format(1028+offset, i, str("%.0f" % fcMaxCurrent) + "A"))

        print("-" * separator)
        print("CONNECTOR {} (22 registers)".format(i))
        print("-" * separator)

        #Reading INPUT REGISTERS
        #Connector 1 status
        response = client.read_input_registers(address=0+offset,count=1,unit=UNIT) #Response: [2]
        #Print custom connector status description (you can write your own decriptions)
        if str(response.registers) == str([1]):
            strStatus = "Available"                       
        elif str(response.registers) == str([2]):
            strStatus = "Connect the cable"
        elif str(response.registers) == str([3]):
            strStatus = "Waiting for vehicle to respond"
        elif str(response.registers) == str([4]):
            strStatus = "Charging"
        elif str(response.registers) == str([5]):
            strStatus = "Vehicle has paused charging"
        elif str(response.registers) == str([6]):
            strStatus = "EVSE has paused charging"
        elif str(response.registers) == str([7]):
            strStatus = "Charging has been ended"
        elif str(response.registers) == str([8]):
            strStatus = "Charging fault"
        elif str(response.registers) == str([9]):
            strStatus = "Unpausing charging"
        elif str(response.registers) == str([10]):
            strStatus = "Unavailable"
        else:
            strStatus = "Unknown status!"

        print("[0]Connector {} status: {}".format(i, strStatus))
    
        #Connector i Measured vehicle number of phases
        response = client.read_input_registers(address=1+offset,count=1,unit=UNIT) #Response: [1]
        #print(response.registers)

        #Print number of phases
        if str(response.registers) == str([0]):
            strPhases = "Three phases"                       
        elif str(response.registers) == str([1]):
            strPhases = "Single phase (L1)"
        elif str(response.registers) == str([2]):
            strPhases = "Single phase (L2)"
        elif str(response.registers) == str([3]):
            strPhases = "Single phase (L3)"
        elif str(response.registers) == str([4]):
            strPhases = "Unknown number of phases"
        elif str(response.registers) == str([5]):
            strPhases = "Two phases"
        else:
            strPhases = "Unknown number of phases!"

        print("[{}]Connector {} measured vehicle number of phases: {}".format(1+offset, i, strPhases))
    
        #Connector i EV max phase current
        response = client.read_input_registers(address=2+offset,count=2,unit=UNIT) # Response: [16742, 26214]
        #Convert to float and round to 2 decimal places
        phaseCurrent=pack('>HH',response.registers[0],response.registers[1])    
        fphaseCurrent = unpack('>f', phaseCurrent)
        print("[{}]Connector {} EV max phase current: {}".format(2+offset, i, str("%.2f" % fphaseCurrent) + "A"))
        
        #Connector i Target current from power mgm or modbus
        response = client.read_input_registers(address=4+offset,count=2,unit=UNIT) #Response: [16656, 0]
        #Convert to float and round to 2 decimal places
        targetCurrent=pack('>HH',response.registers[0],response.registers[1])    
        ftargetCurrent = unpack('>f', targetCurrent)
        print("[{}]Connector {} Target current from power mgm or modbus: {}".format(4+offset, i, str("%.2f" % ftargetCurrent) + "A"))
    
        #Frequency
        response = client.read_input_registers(address=6+offset,count=2,unit=UNIT) # Response: [16967, 57672]
        #Convert to float and round to 2 decimal places
        frequency=pack('>HH',response.registers[0],response.registers[1])    
        ffrequency = unpack('>f', frequency)
        print("[{}]Connector {} Frequency: {}".format(6+offset, i, str("%.2f" % ffrequency) + "Hz"))

        #Connector i L-N voltage (L1)
        response = client.read_input_registers(address=8+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        voltageL1=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageL1 = unpack('>f', voltageL1)
        print("[{}]Connector {} L-N voltage (L1): {}".format(8+offset, i, str("%.2f" % fvoltageL1) + "V"))

        #Connector i L-N voltage (L2)
        response = client.read_input_registers(address=10+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        voltageL2=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageL2 = unpack('>f', voltageL2)
        print("[{}]Connector {} L-N voltage (L2): {}".format(10+offset, i, str("%.2f" % fvoltageL2) + "V"))

        #Connector i L-N voltage (L3)
        response = client.read_input_registers(address=12+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        voltageL3=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageL3 = unpack('>f', voltageL3)
        print("[{}]Connector {} L-N voltage (L3): {}".format(12+offset, i, str("%.2f" % fvoltageL3) + "V"))

        #Current (L1)
        response = client.read_input_registers(address=14+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        CurrentL1=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentL1 = unpack('>f', CurrentL1)
        print("[{}]Connector {} Current (L1): {}".format(14+offset, i, str("%.2f" % fCurrentL1) + "A"))

        #Connector i Current (L2)
        response = client.read_input_registers(address=16+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        CurrentL2=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentL2 = unpack('>f', CurrentL2)
        print("[{}]Connector {} Current (L2): {}".format(16+offset, i, str("%.2f" % fCurrentL2) + "A"))

        #Connector i Current (L3)
        response = client.read_input_registers(address=18+offset,count=2,unit=UNIT) #Response: [17261, 35389]
        #Convert to float and round to 2 decimal places
        CurrentL3=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentL3 = unpack('>f', CurrentL3)
        print("[{}]Connector {} Current (L3): {}".format(18+offset, i, str("%.2f" % fCurrentL3) + "A"))

        #Connector i Active power (L1)
        response = client.read_input_registers(address=20+offset,count=2,unit=UNIT) # Response: [16435, 13107]
        #Convert to float and round to 2 decimal places
        PowerL1=pack('>HH',response.registers[0],response.registers[1])    
        fPowerL1 = unpack('>f', PowerL1)
        print("[{}]Connector {} Active power (L1): {}".format(20+offset, i, str("%.2f" % fPowerL1) + "kW"))
   
        #Connector i Active power (L2)
        response = client.read_input_registers(address=22+offset,count=2,unit=UNIT) # Response: [16435, 13107]
        #Convert to float and round to 2 decimal places
        PowerL2=pack('>HH',response.registers[0],response.registers[1])    
        fPowerL2 = unpack('>f', PowerL2)
        print("[{}]Connector {} Active power (L2): {}".format(22+offset, i, str("%.2f" % fPowerL2) + "kW"))

        #Connector i Active power (L3)
        response = client.read_input_registers(address=24+offset,count=2,unit=UNIT) # Response: [16435, 13107]
        #Convert to float and round to 2 decimal places
        PowerL3=pack('>HH',response.registers[0],response.registers[1])    
        fPowerL3 = unpack('>f', PowerL3)
        print("[{}]Connector {} Active power (L3): {}".format(24+offset, i, str("%.2f" % fPowerL3) + "kW"))

        #Connector i Active power (total)
        response = client.read_input_registers(address=26+offset,count=2,unit=UNIT) # Response: [16435, 13107]
        #Convert to float and round to 2 decimal places
        PowerTotal=pack('>HH',response.registers[0],response.registers[1])    
        fPowerTotal = unpack('>f', PowerTotal)
        print("[{}]Connector {} Active power (Total): {}".format(26+offset, i, str("%.2f" % fPowerTotal) + "kW"))

        #Connector i Power factor
        response = client.read_input_registers(address=28+offset,count=2,unit=UNIT) # Response: [16224, 50332]
        #Convert to float and round to 3 decimal places
        PowerFactor=pack('>HH',response.registers[0],response.registers[1])    
        fPowerFactor = unpack('>f', PowerFactor)
        print("[{}]Connector {} Power factor: {}".format(28+offset, i, str("%.3f" % fPowerFactor)))

        #Connector i Total imported active energy in running session
        response = client.read_input_registers(address=30+offset,count=2,unit=UNIT) # Response: [16695, 53276]
        #Convert to float and round to 2 decimal places
        ActiveEnergy=pack('>HH',response.registers[0],response.registers[1])    
        fActiveEnergy = unpack('>f', ActiveEnergy)
        print("[{}]Connector {} Total imported active energy in running session: {}".format(30+offset, i, str("%.2f" % fActiveEnergy) + "kWh"))

        #Connector i Running session duration
        response = client.read_input_registers(address=32+offset,count=4,unit=UNIT) #Response: [0, 0, 0, 218]
        intH=int(float(response.registers[3])/3600);
        intM=int((float(response.registers[3])-intH*3600)/60);
        intS=int(float(response.registers[3])-intH*3600-intM*60);
        
        # Adding leading zeroes for minutes
        if (intM<10):
            strM = "0" + str(intM)                       
        else:
            strM = str(intM)
        
        # Adding leading zeroes for seconds
        if (intS<10):
            strS = "0" + str(intS)                       
        else:
            strS = str(intS)
            
        print("[{}]Connector {} Running session duration (h:mm:ss): {}".format(32+offset, i, str(intH) + ":" + strM + ":" + strS))

        #Connector i Running session departure time
        response = client.read_input_registers(address=36+offset,count=4,unit=UNIT) #Response: [0, 0, 24040, 63560]
        #Create 64bit integer
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big)
        unixTime=decoder.decode_64bit_int() #Decode date/time
        #Print received departure time formated as %d-%m-%Y %H:%M
        print("[{}]Connector {} Running session departure time: {}".format(36+offset, i, datetime.datetime.fromtimestamp(unixTime).strftime('%d-%m-%Y %H:%M')))

        #Connector i Running session ID
        response = client.read_input_registers(address=40+offset,count=4,unit=UNIT)
        intID=int(response.registers[3])
        print("[{}]Connector {} Running session ID: ".format(40+offset, i, str(intID)))

        #Connector i EV max power
        response = client.read_input_registers(address=44+offset,count=2,unit=UNIT)
        #Convert to float and round to 3 decimal places
        evMaxPower=pack('>HH',response.registers[0],response.registers[1])    
        fevMaxPower = unpack('>f', evMaxPower)
        print("[{}]Connector {} EV max power: {}".format(44+offset, i, str("%.3f" % fevMaxPower)))

        #Connector i EV required energy
        response = client.read_input_registers(address=46+offset,count=2,unit=UNIT)
        #Convert to float and round to 3 decimal places
        evReqEnergy=pack('>HH',response.registers[0],response.registers[1])    
        fevReqEnergy = unpack('>f', evReqEnergy)
        print("[{}]Connector {} EV required energy: {}".format(46+offset, i, str("%.3f" % fevReqEnergy)))


    client.close()
    
except:
    print("-" * separator)
    print("An error has occurred during charger's data reading!")

# Cluster settings
try:    
    #Try to connect to client
    clientPC = ModbusTcpClient(clientIP, clientPortCluster, timeout=2, retries=2) #Use port 503 for reading cluster data

    print("=" * separator)
    print(">>> CLUSTER SETTINGS (1 register) <<<")
    print("=" * separator)
    
    #Building LoadGuard installed
    response = clientPC.read_input_registers(address=3000,count=1,unit=UNIT) #Response: [1]

    #Print LoadGuard installation status (you can write your own decriptions)
    if str(response.registers) == str([0]):
        strLG = "Not installed"                       
    elif str(response.registers) == str([1]):
        strLG = "Installed"
    else:
        strLG = "Unknown installation status!"

    print("[3000]LoadGuard installation status: " + strLG)

    clientPC.close()

except:
    print("-" * separator)
    print("An error has occurred during cluster settings reading!")

if strLG != "Not installed":
# Load Guard and power cluster data
    try:
        #Print connection info
        print("=" * separator)
        #print("Reading data from INCH DUO:",clientPC)
        print("Reading cluster data from INCH or DUO, IP address and port: " + str(clientIP) + ":" + str(clientPortCluster))
        print("-" * separator)
        print(">>> CLUSTER DATA (20 registers) <<<")
        print("=" * separator)
        
        #LoadGuard connected
        response = clientPC.read_input_registers(address=2000,count=1,unit=UNIT) # Response: [1]
        #Print LoadGuard connection status (you can write your own decriptions)
        if str(response.registers) == str([0]):
            strLG = "Not connected"                       
        elif str(response.registers) == str([1]):
            strLG = "Connected"
        else:
            strLG = "Unknown connection status!"

        print("[2000]LoadGuard status: " + strLG)

        #LoadGuard frequency
        response = clientPC.read_input_registers(address=2002,count=2,unit=UNIT) # Response: [16968, 7864]
        #Convert to float and round to 2 decimal places
        frequencyLG=pack('>HH',response.registers[0],response.registers[1])    
        ffrequencyLG = unpack('>f', frequencyLG)
        print("[2002]Load Guard frequency: " + str("%.2f" % ffrequencyLG) + "Hz")

        #Load Guard L-N voltage (L1)
        response = clientPC.read_input_registers(address=2004,count=2,unit=UNIT) # Response: [17263, 57016]
        #Convert to float and round to 2 decimal places
        voltageLGL1=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageLGL1 = unpack('>f', voltageLGL1)
        print("[2004]Load Guard L-N voltage (L1): " + str("%.2f" % fvoltageLGL1) + "V")

        #Load Guard L-N voltage (L2)
        response = clientPC.read_input_registers(address=2006,count=2,unit=UNIT) # Response: [17263, 57016]
        #Convert to float and round to 2 decimal places
        voltageLGL2=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageLGL2 = unpack('>f', voltageLGL2)
        print("[2006]Load Guard L-N voltage (L2): " + str("%.2f" % fvoltageLGL2) + "V")

        #Load Guard L-N voltage (L3)
        response = clientPC.read_input_registers(address=2008,count=2,unit=UNIT) # Response: [17263, 57016]
        #Convert to float and round to 2 decimal places
        voltageLGL3=pack('>HH',response.registers[0],response.registers[1])    
        fvoltageLGL3 = unpack('>f', voltageLGL3)
        print("[2008]Load Guard L-N voltage (L3): " + str("%.2f" % fvoltageLGL3) + "V")

        #Load Guard current (L1)
        response = clientPC.read_input_registers(address=2010,count=2,unit=UNIT) # Response: [16184, 37749]
        #Convert to float and round to 2 decimal places
        CurrentLGL1=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentLGL1 = unpack('>f', CurrentLGL1)
        print("[2010]Load Guard current (L1): " + str("%.2f" % fCurrentLGL1) + "A")

        #Load Guard current (L2)
        response = clientPC.read_input_registers(address=2012,count=2,unit=UNIT) # Response: [16184, 37749]
        #Convert to float and round to 2 decimal places
        CurrentLGL2=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentLGL2 = unpack('>f', CurrentLGL2)
        print("[2012]Load Guard current (L2): " + str("%.2f" % fCurrentLGL2) + "A")

        #Load Guard current (L3)
        response = clientPC.read_input_registers(address=2014,count=2,unit=UNIT) # Response: [16184, 37749]
        #Convert to float and round to 2 decimal places
        CurrentLGL3=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentLGL3 = unpack('>f', CurrentLGL3)
        print("[2014]Load Guard current (L3): " + str("%.2f" % fCurrentLGL3) + "A")
        
        #Load Guard active power (L1)
        response = clientPC.read_input_registers(address=2016,count=2,unit=UNIT) # Response: [15826, 61866]
        #Convert to float and round to 2 decimal places
        PowerLGL1=pack('>HH',response.registers[0],response.registers[1])    
        fPowerLGL1 = unpack('>f', PowerLGL1)
        print("[2016]Load Guard active power (L1): " + str("%.2f" % fPowerLGL1) + "kW")
    
        #Load Guard active power (L2)
        response = clientPC.read_input_registers(address=2018,count=2,unit=UNIT) # Response: [15826, 61866]
        #Convert to float and round to 2 decimal places
        PowerLGL2=pack('>HH',response.registers[0],response.registers[1])    
        fPowerLGL2 = unpack('>f', PowerLGL2)
        print("[2018]Load Guard active power (L2): " + str("%.2f" % fPowerLGL2) + "kW")

        #Load Guard active power (L3)
        response = clientPC.read_input_registers(address=2020,count=2,unit=UNIT) # Response: [15826, 61866]
        #Convert to float and round to 2 decimal places
        PowerLGL3=pack('>HH',response.registers[0],response.registers[1])    
        fPowerLGL3 = unpack('>f', PowerLGL3)
        print("[2020]Load Guard active power (L3): " + str("%.2f" % fPowerLGL3) + "kW")

        #Load Guard active power (total)
        response = clientPC.read_input_registers(address=2022,count=2,unit=UNIT) # Response: [15826, 61866]
        #Convert to float and round to 2 decimal places
        PowerLGTotal=pack('>HH',response.registers[0],response.registers[1])    
        fPowerLGTotal = unpack('>f', PowerLGTotal)
        print("[2022]Load Guard active power (Total): " + str("%.2f" % fPowerLGTotal) + "kW")

        #Load Guard power factor
        response = clientPC.read_input_registers(address=2024,count=2,unit=UNIT) # Response: [16254, 13631]
        #Convert to float and round to 2 decimal places
        PowerFactorLG=pack('>HH',response.registers[0],response.registers[1])    
        fPowerFactorLG = unpack('>f', PowerFactorLG)
        print("[2024]Load Guard Power factor: " + str("%.3f" % fPowerFactorLG))

        #Power cluster current (L1)
        response = clientPC.read_input_registers(address=2100,count=2,unit=UNIT)
        #print(response.registers)
        #Convert to float and round to 2 decimal places
        CurrentPCL1=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentPCL1 = unpack('>f', CurrentPCL1)
        print("[2100]Power cluster current (L1): " + str("%.2f" % fCurrentPCL1) + "A")

        #Power cluster current (L2)
        response = clientPC.read_input_registers(address=2102,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        CurrentPCL2=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentPCL2 = unpack('>f', CurrentPCL2)
        print("[2102]Power cluster current (L2): " + str("%.2f" % fCurrentPCL2) + "A")

        #Power cluster current (L3)
        response = clientPC.read_input_registers(address=2104,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        CurrentPCL3=pack('>HH',response.registers[0],response.registers[1])    
        fCurrentPCL3 = unpack('>f', CurrentPCL3)
        print("[2104]Power cluster current (L3): " + str("%.2f" % fCurrentPCL3) + "A")
        
        #Power cluster active power (L1)
        response = clientPC.read_input_registers(address=2106,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        PowerPCL1=pack('>HH',response.registers[0],response.registers[1])    
        fPowerPCL1 = unpack('>f', PowerPCL1)
        print("[2106]Power cluster active power (L1): " + str("%.2f" % fPowerPCL1) + "kW")
    
        #Power cluster active power (L2)
        response = clientPC.read_input_registers(address=2108,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        PowerL2=pack('>HH',response.registers[0],response.registers[1])    
        fPowerL2 = unpack('>f', PowerL2)
        print("[2108]Power cluster active power (L2): " + str("%.2f" % fPowerL2) + "kW")

        #Power cluster active power (L3)
        response = clientPC.read_input_registers(address=2110,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        PowerL3=pack('>HH',response.registers[0],response.registers[1])    
        fPowerL3 = unpack('>f', PowerL3)
        print("[2110]Power cluster active power (L3): " + str("%.2f" % fPowerL3) + "kW")

        #Power cluster active power (total)
        response = clientPC.read_input_registers(address=2112,count=2,unit=UNIT)
        #Convert to float and round to 2 decimal places
        PowerPCTotal=pack('>HH',response.registers[0],response.registers[1])    
        fPowerPCTotal = unpack('>f', PowerPCTotal)
        print("[2112]Power cluster active power (Total): " + str("%.2f" % fPowerPCTotal) + "kW")

    except:
        print("-" * separator)
        print("An error has occurred during cluster data reading!")

