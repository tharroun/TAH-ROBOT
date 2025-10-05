#!/usr/bin/bash
function StartDialog () {
dialog --yesno "Is the gamepad and robot ready?" 10 31
}
StartDialog
RESPONSE=$?
if [ $RESPONSE -eq 0 ]; then
  clear
  echo "Running!"
  source /home/tah/.bashrc
  source /home/tah/GitHub/TAH-ROBOT/.venv/bin/activate
  python3 /home/tah/GitHub/TAH-ROBOT/follow/follow.py
else 
  echo "Not ready"
fi

