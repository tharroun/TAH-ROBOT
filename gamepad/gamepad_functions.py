import evdev

device = evdev.InputDevice('/dev/input/event12')
print(device)

for event in device.read_loop():
    print(evdev.categorize(event))
    print(event.type,event.code,event.value)