#!/bin/bash 

if cat /home/pat/HG_internship/ASV/ardupilot/Tools/autotest/locations.txt | grep "Viridian=0,0,0,0"
then
echo "location exist already"
else
echo "Viridian=0,0,0,0" >> /home/pat/HG_internship/ASV/ardupilot/Tools/autotest/locations.txt
fi
