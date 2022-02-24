#######################################################
# Modbus writing Python script.                       #
# More details in excel document                      #
# Etrel INCH (Duo) SmartHome Modbus TCPRegisters.xlsx #
#                                                     #
# Version 2.5                                         #
# March, 2021.                                        #
# Author: Samir Gutić, ETREL doo                      #
#######################################################

#Imports
from pymodbus.client.sync import ModbusTcpClient
from datetime import datetime #For UNIX timestamp conversion
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
    
#Initialisations
UNIT = 1
separator=65 #Separator line length
clientPort=502
clientPortCluster=503
connector="a"   #Initialise connector

#PLEASE CHANGE CHARGER'S IP ADDRESS FIRST
################################################

clientIP="192.168.1.250" #Charger's IP address

################################################

#Open client connction
client = ModbusTcpClient(clientIP, clientPort)
    
#Repeat connector selection until user enter e
while connector!="e":
    
    print("-" * separator)
    connector= input("Please enter connector number 1 or 2 for " + clientIP + " (e to exit): ")

    option="a"      #Initialise option
    
    if (connector=="1"):

        #Repeat option selectoon for selected connector until user enter e
        while option!="e":
            try:
                print("-" * separator)
                print("AVAILABLE WRITING OPTIONS for", clientIP)
                print("-" * separator)
                print(">>> CONNECTOR 1 COMMANDS <<<")
                print("1.  Stop charging")
                print("2.  Pause charging")
                print("3.  Set departure time")
                print("4.  Set current setpoint")
                print("5.  Cancel current setpoint")
                print("6.  Set power setpoint")
                print("7.  Cancel power setpoint")
                print("\n>>> CHARGER COMMANDS <<<")
                print("8.  Set time")
                print("9.  Restart charger")
                print("\n>>> CLUSTER COMMANDS <<<")
                print("10.  Cluster - set limit L1")
                print("11.  Cluster - set limit L2")
                print("12.  Cluster - set limit L3")
                print("-" * separator)

                #Read user input (option to write)
                option= input("Please enter option number (1 to 12 or e to exit): ")
            
                if (option=='1' or option=='2' or option=='3' or option=='4' or option=='5' or option=='6' or option=='7' or option=='8' or option=='9'):
                    #client = ModbusTcpClient(clientIP, clientPort)

                    #Print connection info
                    print("-" * separator)
                    print("Connection:",client)

                    if (option=='1' or option=='2' or option=='3' or option=='4' or option=='5'):
                        print("-" * separator)
                        print(">>> CONNECTOR COMMANDS <<<")
                        print("-" * separator)
                    
                    if (option=='1'):
                        #1. Stop charging (sysntax: serverResponse = client.write_registers(address, value))
                        serverResponse = client.write_registers(1, 1) 
                        print("[1]Stop charging on " + str(client))

                    if (option=='2'):
                        #2. Pause charging
                        serverResponse = client.write_registers(2, 1) 
                        print("[2]Pause charging on " + str(client))

                    if (option=='3'):
                        #3. Set departure time (Unix time (seconds since 1970-01-01 00:00:00 UTC))
                        unixTime=int(input("Please enter UNIX timestamp: "))
                        #unixTime=int("1578502800") #8-1-2020 17:00:00
                        binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                        binBuilder.add_64bit_int(unixTime)
                        regData = binBuilder.build()
                        serverResponse  = client.write_registers(4, regData, skip_encode=True)
                        print("[4]Set departure time to: " + str(datetime.utcfromtimestamp(unixTime).strftime('%H:%M:%S %d-%m-%Y ')))

                    if (option=='4'):
                        #4. Set current setpoint
                        currentSetpoint=float(input("Please enter current setpoint in A (e.g. 6.6): "))
                        #currentSetpoint=6.60
                        if (currentSetpoint>=6.0 and currentSetpoint<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentSetpoint)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(8, regData, skip_encode=True)
                            print("[8]Set current setpoint to: " + str(int(currentSetpoint)) + "A") #int because charger sets target to integer value
                        else:
                            print("You have entered unsuported value(" + str(currentSetpoint) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='5'):
                        #5. Cancel current setpoint
                        serverResponse = client.write_registers(10, 1) 
                        print("[10]Cancel current setpoint on " + str(client))

                    if (option=='6'):
                        #6. Set power setpoint
                        powerSetpoint=float(input("Please enter power setpoint in kW (e.g. 11.1): "))
                        if (powerSetpoint<=22.0):
                            
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(powerSetpoint)
                             
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(11, regData, skip_encode=True)
                            
                            print("[11]Set power setpoint to: " + str(powerSetpoint) + "kW") #int because charger sets target to integer value
                        else:
                            print("You have entered unsuported value(" + str(powerSetpoint) + ")")
                            print("Value must be equal to or less than 22")

                    if (option=='7'):
                        #7. Cancel power setpoint
                        serverResponse = client.write_registers(13, 1) 
                        print("[13]Cancel power setpoint on " + str(client))

                    if (option=='8' or option=='9'):
                        print("-" * separator)
                        print(">>> CHARGER COMMANDS <<<")
                        print("-" * separator)

                    if (option=='8'):
                        #8. Set time (Unix time (seconds since 1970-01-01 00:00:00 UTC))
                        unixTime=int(input("Please enter UNIX timestamp: "))
                        #unixTime=int("1601984744") #6-10-2020 13:45:44
                        binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                        binBuilder.add_64bit_int(unixTime)
                        regData = binBuilder.build()
                        serverResponse  = client.write_registers(1000, regData, skip_encode=True)
                        print("[1000]Set time to: " + str(datetime.utcfromtimestamp(unixTime).strftime('%H:%M:%S %d-%m-%Y ')))

                    if (option=='9'):
                        #9. Restart charger
                        serverResponse = client.write_registers(1004, 1) 
                        print("[1004]Restart charger " + str(client))

                elif (option=='10' or option=='11' or option=='12'):
                    client = ModbusTcpClient(clientIP, clientPortCluster)
                    print("-" * separator)
                    print(">>> CLUSTER COMMANDS <<<")
                    print("-" * separator)

                    if (option=='10'):
                        #10. Cluster - set limit L1
                        currentlimitL1=float(input("Please enter cluster current limit for L1 in A (e.g. 6.6): "))
                        #currentlimitL1=6.00
                        if (currentlimitL1>=6.0): # and currentlimitL1<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL1)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2000, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2000]Cluster - set limit L1 to: " + str(currentlimitL1) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL1) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='11'):
                        #11. Cluster - set limit L2
                        currentlimitL2=float(input("Please enter cluster current limit for L2 in A (e.g. 6.6): "))
                        #currentlimitL2=6.00
                        if (currentlimitL2>=6.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL2)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2002, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2002]Cluster - set limit L2 to: " + str(currentlimitL2) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL2) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='12'):
                        #12. Cluster - set limit L3
                        currentlimitL3=float(input("Please enter cluster current limit for L3 in A (e.g. 6.6): "))
                        #currentlimitL3=6.00
                        if (currentlimitL3>=6.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL3)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2004, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2004]Cluster - set limit L3 to: " + str(currentlimitL3) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL3) + ")")
                            print("Value must be between 6.0 and 32.0")
                else:
                    if (option!='e'):
                        print("*" * separator)
                        print("You have entered unsuported option(" + str(option) + ")")
                        print("*" * separator)
            except:
                print("-" * separator)
                print("An error has occurred during writing!")
    elif (connector=="2"):

        #Repeat option selectoon for selected connector until user enter e
        while option!="e":
            try:
                print("-" * separator)
                print("AVAILABLE WRITING OPTIONS for", clientIP)
                print("-" * separator)
                print(">>> CONNECTOR 2 COMMANDS <<<")
                print("1.  Stop charging")
                print("2.  Pause charging")
                print("3.  Set departure time")
                print("4.  Set current setpoint")
                print("5.  Cancel current setpoint")
                print("6.  Set power setpoint")
                print("7.  Cancel power setpoint")
                print("\n>>> CHARGER COMMANDS <<<")
                print("8.  Set time")
                print("9.  Restart charger")
                print("\n>>> CLUSTER COMMANDS <<<")
                print("10.  Cluster - set limit L1")
                print("11.  Cluster - set limit L2")
                print("12.  Cluster - set limit L3")
                print("-" * separator)

                #Read user input (option to write)
                option= input("Please enter option number (1 to 12 or e to exit): ")
                
                if (option=='1' or option=='2' or option=='3' or option=='4' or option=='5' or option=='6' or option=='7' or option=='8' or option=='9'):
                    client = ModbusTcpClient(clientIP, clientPort)

                    #Print connection info
                    print("-" * separator)
                    print("Connection:",client)

                    if (option=='1' or option=='2' or option=='3' or option=='4' or option=='5'):
                        print("-" * separator)
                        print(">>> CONNECTOR COMMANDS <<<")
                        print("-" * separator)
                    
                    if (option=='1'):
                        #1. Stop charging (sysntax: serverResponse = client.write_registers(address, value))
                        serverResponse = client.write_registers(101, 1) 
                        print("[101]Stop charging on " + str(client))

                    if (option=='2'):
                        #2. Pause charging
                        serverResponse = client.write_registers(102, 1) 
                        print("[102]Pause charging on " + str(client))

                    if (option=='3'):
                        #3. Set departure time (Unix time (seconds since 1970-01-01 00:00:00 UTC))
                        unixTime=int(input("Please enter UNIX timestamp: "))
                        #unixTime=int("1578502800") #8-1-2020 17:00:00
                        binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                        binBuilder.add_64bit_int(unixTime)
                        regData = binBuilder.build()
                        serverResponse  = client.write_registers(104, regData, skip_encode=True)
                        print("[104]Set departure time to: " + str(datetime.utcfromtimestamp(unixTime).strftime('%H:%M:%S %d-%m-%Y ')))

                    if (option=='4'):
                        #4. Set current setpoint
                        currentSetpoint=float(input("Please enter current setpoint in A (e.g. 6.6): "))
                        #currentSetpoint=6.60
                        if (currentSetpoint>=6.0 and currentSetpoint<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentSetpoint)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(108, regData, skip_encode=True)
                            print("[108]Set current setpoint to: " + str(int(currentSetpoint)) + "A") #int because charger sets target to integer value
                        else:
                            print("You have entered unsuported value(" + str(currentSetpoint) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='5'):
                        #5. Cancel current setpoint
                        serverResponse = client.write_registers(110, 1) 
                        print("[110]Cancel current setpoint on " + str(client))

                    if (option=='6'):
                        #6. Set current setpoint
                        powerSetpoint=float(input("Please enter power setpoint in kW (e.g. 11.1): "))
                        #powerSetpoint=6.60
                        if (powerSetpoint<=22.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(powerSetpoint)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(111, regData, skip_encode=True)
                            print("[111]Set power setpoint to: " + str(powerSetpoint) + "kW")
                        else:
                            print("You have entered unsuported value(" + str(powerSetpoint) + ")")
                            print("Value must be equal to or less than 22.0")

                    if (option=='7'):
                        #7. Cancel current setpoint
                        serverResponse = client.write_registers(113, 1) 
                        print("[113]Cancel power setpoint on " + str(client))

                    if (option=='8' or option=='9'):
                        print("-" * separator)
                        print(">>> CHARGER COMMANDS <<<")
                        print("-" * separator)

                    if (option=='8'):
                        #8. Set time (Unix time (seconds since 1970-01-01 00:00:00 UTC))
                        unixTime=int(input("Please enter UNIX timestamp: "))
                        #unixTime=int("1578380400") #7-1-2020 7:00:00
                        binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                        binBuilder.add_64bit_int(unixTime)
                        regData = binBuilder.build()
                        serverResponse  = client.write_registers(1000, regData, skip_encode=True)
                        print("[1000]Set time to: " + str(datetime.utcfromtimestamp(unixTime).strftime('%H:%M:%S %d-%m-%Y ')))

                    if (option=='9'):
                        #9. Restart charger
                        serverResponse = client.write_registers(1004, 1) 
                        print("[1004]Restart charger " + str(client))

                elif (option=='10' or option=='11' or option=='12'):
                    client = ModbusTcpClient(clientIP, clientPortCluster)
                    
                    print("-" * separator)
                    print(">>> CLUSTER COMMANDS <<<")
                    print("-" * separator)

                    if (option=='10'):
                        #10. Cluster - set limit L1
                        currentlimitL1=float(input("Please enter cluster current limit for L1 in A (e.g. 6.6): "))
                        #currentlimitL1=6.00
                        if (currentlimitL1>=6.0 and currentlimitL1<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL1)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2000, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2000]Cluster - set limit L1 to: " + str(currentlimitL1) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL1) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='11'):
                        #11. Cluster - set limit L2
                        currentlimitL2=float(input("Please enter cluster current limit for L2 in A (e.g. 6.6): "))
                        #currentlimitL2=6.00
                        if (currentlimitL2>=6.0 and currentlimitL2<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL2)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2002, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2002]Cluster - set limit L2 to: " + str(currentlimitL2) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL2) + ")")
                            print("Value must be between 6.0 and 32.0")

                    if (option=='12'):
                        #12. Cluster - set limit L3
                        currentlimitL3=float(input("Please enter cluster current limit for L3 in A (e.g. 6.6): "))
                        #currentlimitL3=6.00
                        if (currentlimitL3>=6.0 and currentlimitL3<=32.0):
                            binBuilder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                            binBuilder.add_32bit_float(currentlimitL3)
                            regData = binBuilder.build()
                            serverResponse  = client.write_registers(2004, regData, skip_encode=True)
                            #print(serverResponse)
                            print("[2004]Cluster - set limit L3 to: " + str(currentlimitL3) + "A")
                        else:
                            print("You have entered unsuported value(" + str(currentlimitL3) + ")")
                            print("Value must be between 6.0 and 32.0")
                    
                    #print("-" * separator)
                    #print(">>> CUSTOM WRITE EXCEPTIONS <<<")
                    #print("-" * separator)

                    
                    #client.close()
                else:
                    if (option!='e'):
                        print("*" * separator)
                        print("You have entered unsuported option(" + str(option) + ")")
                        print("*" * separator)
            except:
                print("-" * separator)
                print("An error has occurred during writing!")

        else:
            #print("Konektor: ", connector)
            if (connector!="1" and connector!="2"):
                
                if (connector=="e"):
                    print ("To continue, please run script again.")
                else:
                    print ("Connector number", connector, "doesn't exist. Plese enter 1 or 2")

#Close client connection
client.close()
