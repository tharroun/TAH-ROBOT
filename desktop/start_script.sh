#!/bin/bash

DIALOG_CANCEL=1
DIALOG_ESC=255

display_result() {
  dialog --title "$1" \
    --no-collapse \
    --msgbox "$result" 0 0
}

exec 3>&1
selection=$(dialog \
  --backtitle "ROBOT CONTROL" \
  --title "BLUETOOTH CHECK" \
  --clear \
  --cancel-label "CANCEL" \
  --yesno "Is the gamepad connected by bluetooth?" 0 0 2>&1 1>&3)
exit_status=$?
exec 3>&-
case $exit_status in
  $DIALOG_CANCEL)
    clear
    echo "Program terminated"
    exit
    ;;
  $DIALOG_ESC)
    clear
    echo "Program aborted." >&2
    exit 1
    ;;
esac


exec 3>&1
selection2=$(dialog \
  --backtitle "ROBOT CONTROL" \
  --title "Robot function" \
  --clear \
  --cancel-label "CANCEL" \
  --menu "MAKE A CHOICE:" 0 0 4 \
  "A" "Just drive" \
  "B" "Follow with servo" \
  "C" "Follow with motor" \
  "D" "Follow with both" \
  2>&1 1>&3)
exit_status=$?
exec 3>&-
case $exit_status in
  $DIALOG_CANCEL)
    clear
    echo "Program terminated"
    exit
    ;;
  $DIALOG_ESC)
    clear
    echo "Program aborted." >&2
    exit 1
    ;;
esac
clear
case $selection2 in
  "A" )
    echo "JUST DRIVE"
    ;;
  "B" )
    echo "FOLLOW WITH SERVOS ONLY"
    ;;
  "C" )
    echo "FOLLOW WITH MOTORS ONLY"
    ;;
  "D" )
    echo "FOLLOW WITH SERVOS AND MOTORS"
    ;;
esac
