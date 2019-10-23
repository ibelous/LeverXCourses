import json
import xml.etree.cElementTree as ET


class BaseWriter:
    def writefile(self, filename: str, data: list):
        return NotImplementedError


class JSONFileReader:
    def __init__(self, path: str):
        self.path = path

    def readFile(self):
        return NotImplementedError


class ReadStudents(JSONFileReader):
    def readFile(self, Student) -> list:
        students = []
        with open(self.path, 'r') as f:
            for stud in json.load(f):
                students.append(Student(stud))
        return students


class ReadRooms(JSONFileReader):
    def readFile(self, RoomWithStudents) -> list:
        rooms = []
        with open(self.path, 'r') as f:
            for room in json.load(f):
                rooms.append(RoomWithStudents(room))
        return rooms


class JsonSelectsWriter(BaseWriter):
    def writefile(self, filename: str, data: list):
        with open(filename+'.json', 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)


class XmlSelectsWriter(BaseWriter):
    def writefile(self, filename: str, data: list):
        roomswithstudents = data
        rooms = ET.Element('rooms')
        for rm in roomswithstudents:
            room = ET.SubElement(rooms, 'room')
            roomname = ET.SubElement(room, 'roomname')
            roomname.text = str(rm.name)

        mydata = ET.ElementTree(rooms)
        ET.dump(mydata)
        mydata.write(filename+'.xml', xml_declaration=True)


class Writer:
    def __init__(self):
        self.formats = {'json': JsonSelectsWriter,
                        'xml': XmlSelectsWriter}

    def choose_format(self, outputformat):
        if outputformat in self.formats:
            return self.formats.get(outputformat)()
        else:
            raise ValueError
