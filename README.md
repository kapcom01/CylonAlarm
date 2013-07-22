# About
This is a **work-in-progress** project. The goal is to become a complete Home Alarm System, easy to setup and use and completely open source from top to bottom, so everyone can install it, study it, change it and do anything one might want to do with it.

## Current Status (v0.2)
With this version we have a working alarm system for our home/lab/garage/etc. It can detect an intrusion with motion detectors and door switches, and will turn on one or more sirens. It is enabled and disabled by the residents using nfc tags which everyone can have in their keychains. It can also send a notification-email to pre-configured email addresses using a gmail account.

# Warning!
In this stage the system is for people who really know what they are doing. Experience in electronics and software is required.

# Hardware ingredients
We will need:

- a Rapberry Pi
- a NFC PN532 Breakout board
- one or more NFC Tags
- one or more IR detectors and/or magnetic NC switches
- a siren

for the control unit:

- 1x LED
- 1x buzzer
- 1x LM7805
- 1x 1kΩ resistor

for cabling:

- a long (UTP cable (10 meters or more.. depending on the house)
- a utp patch cable (straight) about 1-2 meters
- RJ-45 plug

and for our CylonAlarm Board v0.2:

- 1x 5V relay
- 1x npn transistor
- 1x diode
- 1x RJ-45 connector
- 1x DC connector
- 2x 1.5kΩ resistors

# Circuit
Follow the instructions on the images below to prepare the electronics.

![circuit board](https://raw.github.com/kapcom01/CylonAlarm/master/images/cylonalarm_board.png)

![img visual connections](https://raw.github.com/kapcom01/CylonAlarm/master/images/cylonalarm_cabling.png)


# Software Installation
First of all we log in to Raspberry Pi *(running Raspbian OS)* through ssh:

    ssh pi@raspberrypi.lan

In this version we need the **nfc-eventd** which will provide our program the information of the nfc tags that are being used.
So we need to download and compile it from source following [these instructions](http://nfc-tools.org/index.php?title=Nfc-eventd)

We have to install some dependencies:

    sudo apt-get install python-dbus
    sudo apt-get install python-gobject

Also we will need a virtual screen for dbus to work so we will install **tmux** for that:

    sudo apt-get install tmux

Now we can download CylonAlarm:

    git clone https://github.com/kapcom01/CylonAlarm.git
    cd CylonAlarm
    git checkout v0.2

We MUST make the following changes:

- Rename **cylonalarm/config.sample.py** to **cylonalarm/config.py** and then edit it.
- In **/etc/nfc-eventd.conf**:
    - *event tag_insert*:

            action = "python /home/pi/CylonAlarm/check_tag-0.2.py $TAG_UID";
    - *tag_remove*:

            action = "python /home/pi/CylonAlarm/check_tag-0.2.py removed"; 

# Running
Finally we can run the program in the following way:

    sudo dbus-launch tmux
    ctrl+b ["]
    nfc-eventd
    ctrl+b [up key]
    python cylonalarm.py

This way we can have **nfc-eventd** and **cylonalarm.py** running on the same virtual screen so they can communicate through **dbus**.

## leave it run
Now we can leave the program run and log out raspberry pi by detatching first the virtual screen:

    ctrl+b [d]

and then log out:

    ctrl+d

## get back to it
To get back to the virtual screen, we ssh again, and then attach:

    ssh pi@raspberrypi.lan
    sudo tmux attach

and we should now see the screen where we left it.