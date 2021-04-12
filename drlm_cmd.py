import os
import serial.tools.list_ports

from hw_interfaces import ProController

NUM_PIXELS = 288


def setColor(controller: ProController, R: int, G: int, B: int):
    R = int(R)
    G = int(G)
    B = int(B)
    if 0 <= R <= 255 and 0 <= G <= 255 and 0 <= B <= 255:
        print("Setting color: (" + str(R), G, str(B) + ")")
        for i in range(controller.numPixels):
            controller.setPixel(i, R, G, B)
        controller.write()


def clear(controller: ProController):
    controller.clear()
    controller.write()


commands = {
    "setColor": setColor,
    "clear": clear
}


def main():
    ports = []
    for i, port in enumerate(serial.tools.list_ports.comports()):
        ports.append(port)
        print("[" + str(i) + "]: " + str(port.name))
    portNum = int(input("Port number: "))
    assert portNum < len(ports)

    controller = ProController(NUM_PIXELS, os.path.join("/dev", ports[portNum].name))
    end = False
    while not end:
        cmd = input(">>> ").split(" ")
        if cmd[0] == "end":
            end = True

        elif cmd[0] in commands.keys():
            try:
                commands[cmd[0]](controller, *cmd[1:])
            except Exception as e:
                print(e)
        else:
            print("Invalid command!")
            print(list(commands.keys()))


if __name__ == "__main__":
    main()
