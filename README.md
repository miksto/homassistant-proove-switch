## Proove switch component for Homeassistant
This is a component for Homeassistant.io that simplifies the process of controlling
proove remote controlled outlets from your Raspberry pi.

See https://github.com/miksto/Proove-Raspberry-Pi-Transmitter for more info on my setup.

## Installation
These instructions are for a raspberry pi running hassbian, but might work for other setups as well.


Install pigpio which is used to generate the wave forms for the RF chip.

    sudo apt-get update
    sudo apt-get install pigpio python-pigpio python3-pigpio

Start the pigpio daemon by running `sudo pigpiod`. To automatically start pigpio at boot you can add it to the root's crontab.

    @reboot              /usr/local/bin/pigpiod


Clone this repository into

    /home/homeassistant/.homeassistant/custom_components/switch/


Add your switches to **configuration.yaml**

    switch:
    - platform: proove_rf
      gpio: 22
      transmitter_code: '00101010001001010010110010'
      switches:
        bed_outlets:
          name: 'Bed outlets'
          unit_code: '0000'
        window_outlets:
          name: 'Window side outlets'
          unit_code: '0001'
        tv_bench_outlets:
          name: 'TV bench outlets'
          unit_code: '0010'

Restart homeassistant and your switches should appear in the dashboard.
