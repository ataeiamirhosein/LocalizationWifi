import numpy
import matplotlib.pyplot as plt
import time,os
import pyshark

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script")
plt.ion()
plt.show()

while 1:
    os.system('(sudo tshark -Ini en0 -s 256 -f "type mgt subtype beacon" -w beacon.pcap)&')
    time.sleep(5)
    os.system('killall tshark')

    MAC = []
    POWER = []
    KNOWN_AP = ['b8:27:eb:ee:b5:df', 'b8:27:eb:e5:99:fb']
    print("opening...")

    cap = pyshark.FileCapture('beacon.pcap');
    for packet in cap:
        try:
            mac = packet.wlan.sa
            rssi = packet.wlan_radio.signal_dbm
            MAC.append(mac)
            POWER.append(int(rssi))
        except:
            pass

    AVG_POWER = []

    #FOR EACH UNIQUE MAC ADDRESS, COMPUTE ITS AVERAGE POWER
    #AND ADD 1 IN THE BIN CORRESPONDING TO ITS VENDOR (if avg_power > MIN_RSSI)
    for mac in KNOWN_AP:
        idx = [i for i, x in enumerate(MAC) if  x == mac]
        avg_power = numpy.mean([POWER[i] for i in idx])
        AVG_POWER.append(avg_power)

    print("AP:", KNOWN_AP)
    print("RSSI:", AVG_POWER)

    #define MAC address position (known)
    AP_COORD_X = [0,10]
    AP_COORD_Y = [0,0]

    #compute AP weights starting from signal strength measurements
    est_d = [pow(10, -((avg_p+45)/40)) for avg_p in AVG_POWER]
    w = [1/pow(d,2) for d in est_d]
    w_norm = w / sum(w)
    print("WEIGHTS:", w_norm)
    print("ESTIMATED DISTANCES FROM AP:", est_d)

    #compute my position by averaging AP coordinates with the computed weights
    MY_POS_X = numpy.dot(AP_COORD_X,w_norm)
    MY_POS_Y = numpy.dot(AP_COORD_Y,w_norm)
    print("ESTIMATED POSITION:", MY_POS_X, MY_POS_Y)

    #print MY_POS_X
    #print MY_POS_Y

    plt.clf()
    plt.plot(AP_COORD_X,AP_COORD_Y,marker='o',markersize=20,linestyle='none')
    plt.plot(MY_POS_X,MY_POS_Y,marker='x',markersize=20,linestyle='none')
    plt.axis('equal')
    plt.draw()
    plt.pause(0.01)
    #plt.show(block=False)
    #fig.canvas.draw()