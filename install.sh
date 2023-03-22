#!/bin/sh
sudo su <<EOF


# editar archivo inicio /home/pi/.config/autostart/Start.desktop

if [ ! -e /home/pi/.config/autostart/Start.desktop ]; then
    echo "----------- Creando Autostart -----------"
    mkdir /home/pi/.config/autostart
    echo "[Desktop Entry]" >> /home/pi/.config/autostart/Start.desktop
    echo "Type=Application" >> /home/pi/.config/autostart/Start.desktop
    echo "Name=Start" >> /home/pi/.config/autostart/Start.desktop
    echo "Exec=sh Desktop/ContadorRasp/start.sh" >> /home/pi/.config/autostart/Start.desktop
    echo "----------- Autostart creado -----------"
fi


reboot
EOF
