[![Build Status](https://travis-ci.org/kapcom01/CylonAlarm.png?branch=tests-n-improvements)](https://travis-ci.org/kapcom01/CylonAlarm)

# CylonAlarm

This is a **work-in-progress** project. The goal is to become a complete Home Alarm System, comparable to the expensive multi zone commercial systems, easy to setup and use and completely open source from top to bottom, so everyone can install it, study it, change it and do anything one might want to do with it.

### Installation and usage

#### Circuit
Follow the instructions on the images below to prepare the electronics.

![circuit board](https://raw.github.com/kapcom01/CylonAlarm/master/images/cylonalarm_board.png)

![img visual connections](https://raw.github.com/kapcom01/CylonAlarm/master/images/cylonalarm_cabling.png)


#### Software Installation
First of all we log in to Raspberry Pi *(which is running Raspbian OS)* through ssh:

    ssh pi@raspberrypi.lan

Then we do some initial configuration, like expand filesystem, changing password, and changinh hostname:

    sudo raspi-config

Disable the Serial Console to free the UART connection
    
    sudo wget https://raw.github.com/lurch/rpi-serial-console/master/rpi-serial-console -O /usr/bin/rpi-serial-console && sudo chmod +x /usr/bin/rpi-serial-console

    sudo rpi-serial-console disable

And enable the i2c connection protocol following these instructions:

    http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

If we are going to use an NFC Breakout Board with UART, we will need the [*nfc-eventd*](http://nfc-tools.org/index.php?title=Nfc-eventd) app, so we have to do the following:

First we install **libnfc** following these instructions: http://learn.adafruit.com/adafruit-nfc-rfid-on-raspberry-pi/building-libnfc

And then **nfc-eventd**:

    wget https://nfc-tools.googlecode.com/files/nfc-eventd-0.1.7.tar.gz
    tar xvf nfc-eventd-0.1.7.tar.gz
    cd nfc-eventd-0.1.7
    autoreconf -vis
    ./configure
    make
    sudo make install

and make the following changes:

- Add *event tag_insert* action of **/usr/local/etc/nfc-eventd.conf** to: `action = "python /home/pi/CylonAlarm/lib/jsonsockclient.py $TAG_UID 0";` 


I have found that lowering the communications baud rate makes them more stable:

- for i2c:
    
    sudo bash -c "echo options i2c_bcm2708 baudrate=32000 > /etc/modprobe.d/i2c.conf"

- for uart:

    in /etc/nfc-eventd.conf change the device's speed to 9600

We have to install some dependencies, and a virtual screen (tmux):

    sudo apt-get install python-gobject
    sudo apt-get install tmux

Now we can download CylonAlarm:

    git clone https://github.com/kapcom01/CylonAlarm.git
    cd CylonAlarm
    git checkout v0.3.0
    cp config.json.sample config.json

We MUST edit **config.json**!

#### Running
Finally we can run the program in the following way:

    sudo dbus-launch tmux
    ctrl+b ["]
    nfc-eventd
    ctrl+b [up key]
    python cylonalarm.py

This way we can have **nfc-eventd** and **cylonalarm.py** running on the same virtual screen so they can communicate through **dbus**.

#### leave it run
Now we can leave the program run and log out raspberry pi by detatching first the virtual screen:

    ctrl+b [d]

and then log out:

    ctrl+d

#### get back to it
To get back to the virtual screen, we ssh again, and then attach:

    ssh pi@raspberrypi.lan
    sudo tmux attach

and we should now see the screen where we left it.

### Troubleshooting

### Development

To see what has changed in recent versions of CylonAlarm, see the [CHANGELOG]().

### Core Team Members

[Emmanouel Kapernaros](https://github.com/kapcom01)

### Resources

### Other questions

Feel free to contact me.

### Copyright

Copyright © 2013 Emmanouel Kapernaros. See [LICENSE]() for details.

md files by [OSS Manifesto](http://ossmanifesto.com/).
