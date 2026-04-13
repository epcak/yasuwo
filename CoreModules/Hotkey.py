from pynput import keyboard


class Hotkey:
    def __init__(self, keysequence: str, function, functionparameters, active: bool = False):
        self.__keysequence: str = keysequence
        self.__function = function
        self.__parameters = functionparameters
        self.__hotkey: keyboard.GlobalHotKeys
        if functionparameters is None:
            self.__hotkey = keyboard.GlobalHotKeys({self.__keysequence: self.__function})
        else:
            self.__hotkey = keyboard.GlobalHotKeys({self.__keysequence: lambda : self.__function(self.__parameters)})
        self.__active: bool = False
        if active:
            self.activate()

    def gethotkey(self) -> str | None:
        return self.__keysequence

    @staticmethod
    def specifichotkeysequence(sequence: str):
        specialkeys: dict = {}
        for key in keyboard.Key:
            specialkeys[key.name] = key.value
        listenersequence = ""
        first = True
        for key in sequence.split("+"):
            key = key.lower()
            if not first:
                listenersequence += "+"
            if key == "meta":
                listenersequence += "<cmd>"
            elif key == "ins":
                listenersequence += "<insert>"
            elif key in specialkeys.keys():
                listenersequence += f"{specialkeys[key]}"
            else:
                listenersequence += key
            if first:
                first = False
        return listenersequence

    def activate(self):
        if not self.__active:
            self.__active = True
            self.__hotkey.start()

    def deactivate(self):
        if self.__active:
            self.__active = False
            self.__hotkey.stop()
