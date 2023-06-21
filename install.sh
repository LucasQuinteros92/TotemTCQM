#!/bin/sh
sudo su <<EOF

pip3 install websocket
pip3 uninstall websocket -y
pip3 install websocket-client

# editar archivo inicio /home/pi/.config/autostart/Start.desktop

if [ ! -e /home/pi/.config/autostart/Start.desktop ]; then
    echo "----------- Creando Autostart -----------"
    mkdir /home/pi/.config/autostart
    echo "[Desktop Entry]" >> /home/pi/.config/autostart/Start.desktop
    echo "Type=Application" >> /home/pi/.config/autostart/Start.desktop
    echo "Name=Start" >> /home/pi/.config/autostart/Start.desktop
    echo "Exec=sh /home/pi/Desktop/ContadorRasp/start.sh" >> /home/pi/.config/autostart/Start.desktop
    echo "----------- Autostart creado -----------"
fi


reboot
EOF
