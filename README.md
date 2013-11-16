[![Build Status](https://travis-ci.org/kapcom01/CylonAlarm.png?branch=master)](https://travis-ci.org/kapcom01/CylonAlarm)

# CylonAlarm

This is a **work-in-progress** project. The goal is to become a complete Home Alarm System, comparable to the expensive multi zone commercial systems, easy to setup and use and completely open source from top to bottom, so everyone can install it, study it, change it and do anything one might want to do with it.

### Installation and usage

#### Circuit
Follow the instructions on the images below to prepare the electronics.

TODO: Add the new images

#### Software Installation
First of all we log in to Raspberry Pi *(which is running Raspbian OS)* through ssh:

    ssh pi@raspberrypi.lan

Then we do some initial configuration, like change timezon, expand filesystem, change password and hostname:

    sudo raspi-config

Enable UART connection
    
    sudo wget https://raw.github.com/lurch/rpi-serial-console/master/rpi-serial-console -O /usr/bin/rpi-serial-console && sudo chmod +x /usr/bin/rpi-serial-console

    sudo rpi-serial-console disable

Enable i2c connection: http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c


For the NFC to work in long distances we need to lower the baud rate:

- for i2c:
    
    sudo bash -c "echo options i2c_bcm2708 baudrate=38400 > /etc/modprobe.d/i2c.conf"

- for uart:

    in /etc/nfc-eventd.conf change the device's speed to 9600

We have to install some dependencies:

    sudo apt-get install python-gobject

Now we can download CylonAlarm:

    git clone https://github.com/kapcom01/CylonAlarm.git
    cd CylonAlarm
    sudo cp init/cylonalarmd /etc/init.d/
    sudo update-rc.d cylonalarmd defaults
    cp config.json.sample config.json

We MUST edit **config.json**!

#### Running
Finally we start the service:

    sudo /etc/init.d/cylonalarmd start

### Troubleshooting

### Development

To see what has changed in recent versions of CylonAlarm, see the [CHANGELOG](CHANGELOG.md).

### Core Team Members

[Emmanouel Kapernaros](https://github.com/kapcom01)

### Resources

### Other questions

Feel free to contact me.

### Copyright

Copyright © 2013 Emmanouel Kapernaros. This is Free Software. See [LICENSE](LICENSE.md) for details.

.md files by [OSS Manifesto](http://ossmanifesto.com/).
