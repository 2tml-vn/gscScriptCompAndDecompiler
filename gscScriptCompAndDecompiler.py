import struct
from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog # Import filedialog
import os # Import os for path manipulation
import glob # Import glob for finding files

# Refactor GscFile to accept full file path and manage file handles internally
class GscFile:
    FilePath = '' # Store full file path
    #По умолчанию оный открыт, но можно закрыть и переделать на зпись.
    FileParametrs = []
    #См. FileParametrsSupport.
    FileParametrsSupport = ('Размер файла',
                            'Размер заголовка',
                            'Размер секции команд',
                            'Размер секции объявления строк',
                            'Размер секции определения строк',
                            '???',
                            '???',
                            '???',
                            '???')
    #Собственно структуры для упаковки:
    FileStruct = [b'', b'', b'', b'', b'']
    #См. FileStructSupport.
    FileStructSupport = ('Заголовок',
                         'Секция команд',
                         'Секция объявления строк',
                         'Секция определения строк',
                         'Остальное')
    #Строки:
    FileStringOffsets = []
    FileStrings = []
    #Команды:
    CommandArgs = []
    #Двумерный массив, где глубинные есть массивы аргументов конкретной команды.
    Commands = []
    #Просто массив основных команд.
    CommandsLibrary = ((0x03, 'i', 'JUMP_UNLESS'),
                       (0x05, 'i', 'JUMP'),
                       (0x0D, 'i', 'PAUSE'),
                       (0x0C, 'ii', 'CALL_SCRIPT'), #[имя скрипта без начальных нулей, ???]
                       (0x0E, 'hiiiiiiiiiiiiii', 'CHOICE'),
                       (0x14, 'ii', 'IMAGE_GET'),
                       (0x1A, '', 'IMAGE_SET'),
                       (0x1C, 'iii', 'BLEND_IMG'),
                       (0x1E, 'iiiiii', 'IMAGE_DEF'),
                       (0x51, 'iiiiiii', 'MESSAGE'),
                       (0x52, 'iiiiii', 'APPEND_MESSAGE'),
                       (0x53, 'i', 'CLEAR_MESSAGE_WINDOW'),
                       (0x79, 'ii', 'GET_DIRECTORY'),
                       (0xC8, 'iiiiiiiiiii', 'READ_SCENARIO'), #??? Подправить число аргументов?
                       (0xFF, 'iiiii', 'SPRITE'),
                       (0x3500, 'hhh', 'AND'),
                       (0x4800, 'hhh', 'EQUALS'),
                       (0x5400, 'hhh', 'GREATER_EQUALS'),
                       (0xAA00, 'hhh', 'ADD'),
                       (0xF100, 'hh', 'ASSIGN'),
                       (0x04, 'i', ''),
                       (0x08, '', ''),
                       (0x09, 'h', ''),
                       (0x0A, '', ''), #h в другом типе? Хм-м... #WAIT_FOR_CLICK?
                       (0x0B, '', ''),
                       (0x0F, 'iiiiiiiiiiii', ''), #??? #Массив? Подправить число аргументов?
                       (0x10, 'i', ''),
                       (0x11, '', ''),
                       (0x12, 'ii', ''),
                       (0x13, 'i', ''),
                       (0x15, 'i', ''),
                       (0x16, 'iiii', ''),
                       (0x17, 'iiii', ''),
                       (0x18, 'ii', ''),
                       (0x19, 'ii', ''),
                       (0x1B, '', ''),
                       (0x1D, 'ii', ''),
                       (0x20, 'iiiiii', ''),
                       (0x21, 'iiiii', ''),
                       (0x22, 'iiiii', ''),
                       (0x23, 'ii', ''),
                       (0x24, 'ii', ''),
                       (0x25, 'ii', ''),
                       (0x26, 'iii', ''), #Принцесса порчи: iii, остальное: iiii?
                       (0x27, 'iii', ''),
                       (0x28, 'ii', ''),
                       (0x29, 'ii', ''),
                       (0x2A, 'ii', ''),
                       (0x2B, 'ii', ''),
                       (0x2C, 'i', ''),
                       (0x2D, 'ii', ''),
                       (0x2E, 'i', ''),
                       (0x2F, 'ii', ''),
                       (0x30, 'ii', ''), #Принцесса порчи: ii, остальное: iii?
                       (0x31, 'ii', ''),
                       (0x32, '', ''),
                       (0x33, '', ''),
                       (0x34, '', ''),
                       (0x35, 'i', ''),
                       (0x37, '', ''),
                       (0x38, 'iiiii', ''),
                       (0x39, '', ''),
                       (0x3A, '', ''),
                       (0x3B, 'iiii', ''),
                       (0x3C, 'iii', ''),
                       (0x3D, 'ii', ''),
                       (0x3E, 'i', ''), #'i'? По D&D 'ii'.
                       (0x3F, 'iii', ''), #'iii'? По D&D 'iiii'.
                       (0x40, 'i', ''), #'i'? По D&D 'ii'.
                       (0x41, 'i', ''),
                       (0x42, 'iiii', ''),
                       (0x43, 'i', ''),
                       (0x44, '', ''),
                       (0x45, '', ''),
                       (0x46, 'iiii', ''),
                       (0x47, 'iiii', ''),
                       (0x48, 'i', ''),
                       (0x49, 'iii', ''),
                       (0x4A, 'i', ''),
                       (0x4B, 'iiiii', ''),
                       (0x4D, 'iiii', ''),
                       (0x50, 'i', ''),
                       (0x5A, 'iii', ''),
                       (0x5B, 'iiiii', ''),
                       (0x5C, 'ii', ''),
                       (0x5D, 'ii', ''),
                       (0x5E, 'i', ''),
                       (0x5F, 'ii', ''),
                       (0x60, 'ii', ''),
                       (0x61, 'ii', ''),
                       (0x62, 'ii', ''),
                       (0x63, 'iii', ''),
                       (0x64, 'iii', ''),
                       (0x65, 'ii', ''),
                       (0x66, 'i', ''),
                       (0x67, 'ii', ''),
                       (0x68, 'iiii', ''),
                       (0x69, 'i', ''), #В остальных ii?
                       (0x6A, 'iiiii', ''),#TEMP!
                       (0x6B, 'iii', ''), #TEMP!
                       (0x6C, 'iii', ''), #TEMP
                       (0x6E, 'iii', ''),
                       (0x6F, 'iii', ''),
                       (0x70, 'i', ''),
                       (0x71, 'ii', ''),
                       (0x72, 'ii', ''),
                       (0x73, 'ii', ''),
                       (0x74, 'ii', ''),
                       (0x75, 'ii', ''),
                       (0x78, 'ii', ''),
                       (0x82, 'iiii', ''),
                       (0x83, 'iiiii', ''),
                       (0x84, 'ii', ''),
                       (0x86, 'iii', ''),
                       (0x87, 'iiiii', ''),
                       (0x88, 'iii', ''),
                       (0x96, 'ii', ''),
                       (0x97, 'ii', ''),
                       (0x98, 'ii', ''),
                       (0x99, 'ii', ''),
                       (0x9A, 'ii', ''),
                       (0x9B, 'ii', ''),
                       (0x9E, 'ii', ''),
                       (0x9F, 'ii', ''),
                       (0x9C, 'iii', ''),
                       (0x9D, 'iiiii', ''),
                       (0xC9, 'iiiii', ''),
                       (0xCA, 'iii', ''),
                       (0xD2, 'ii', ''),
                       (0xD3, 'iiii', ''),
                       (0xD4, 'i', ''),
                       (0xD5, 'iii', ''),
                       (0xDC, 'iii', ''),
                       (0xDD, 'ii', ''),
                       (0xDE, '', ''),
                       (0xDF, 'ii', ''),
                       (0xE1, 'iiiii', ''),
                       (0xE6, 'i', ''),
                       (0xE7, 'i', ''),
                       (0x1800, 'hhh', ''),
                       (0x1810, 'hhh', ''), #!!!
                       (0x1900, 'hhh', ''),
                       (0x1910, 'hhh', ''),
                       (0x2500, 'hhh', ''),
                       (0x1A01, 'hhh', ''), #!!!
                       (0x1A00, 'hhh', ''),
                       (0x4400, 'hhh', ''),
                       (0x4810, 'hhh', ''), #!!!
                       (0x4900, 'hhh', ''),
                       (0x4A00, 'hhh', ''),
                       (0x5800, 'hhh', ''),
                       (0x6800, 'hhh', ''),
                       (0x7800, 'hhh', ''),
                       (0x7A00, 'hhh', ''),
                       (0x8800, 'hhh', ''),
                       (0x8A00, 'hhh', ''),
                       (0x9800, 'hhh', ''),
                       (0x9810, 'hhh', ''), #!!!
                       (0x9A00, 'hhh', ''),
                       (0xA100, 'hhh', ''),
                       (0xA200, 'hhh', ''),
                       (0xA201, 'hhh', ''), #!!
                       (0xA400, 'hhh', ''),
                       (0xA500, 'hhh', ''),
                       (0xA600, 'hhh', ''),
                       (0xA800, 'hhh', ''),
                       (0xA810, 'hhh', ''), #!!!
                       (0xA900, 'hhh', ''),
                       (0xB400, 'hhh', ''),
                       (0xB800, 'hhh', ''),
                       (0xB900, 'hhh', ''),
                       (0xC400, 'hhh', ''),
                       (0xC800, 'hhh', ''),
                       (0xD400, 'hhh', ''),
                       (0xD800, 'hhh', ''),
                       (0xE400, 'hhh', ''),
                       (0xE800, 'hhh', ''))
    ConnectedStringsLibrary = [[0x0E, [1, 7, 8, 9, 10, 11]], #Убрать 1?
                               [0x0F, [1]],
                               [0x20, [0]],
                               [0x51, [-3, -2]],
                               [0x52, [-2]],
                               [0x79, [1]]]
    ConnectedOffsetsLibrary = [[0x03, [0]],
                               [0x05, [0]],
                               [0x0E, [2, 3, 4, 5, 6]],
                               [0xC8, [0]]]
    Labels = []

    def __init__(self, FilePath, Mode):
        self.FilePath = FilePath
        self.FileParametrs = []
        self.FileStruct = [b'', b'', b'', b'', b'']
        self.FileStringOffsets = []
        self.FileStrings = []
        self.CommandArgs = []
        self.Commands = []
        self.Labels = [] # Labels are per-file, clear on init

        # File will be opened later by specific read/write methods

    def PrintFilePmt(self):
        print(f"--- File Parameters for {os.path.basename(self.FilePath)} ---")
        for i in range(0, len(self.FileParametrs)):
            print(self.FileParametrsSupport[i] + ": " + str(self.FileParametrs[i]) + ".")
        print("--------------------")

    def PrintFileStrc(self):
        print(f"--- File Structure Hex Dump for {os.path.basename(self.FilePath)} ---")
        for i in range(0, len(self.FileStruct)):
            Aller = self.FileStruct[i].hex()
            AllerN = ''
            ii = 2
            while (ii < len(Aller)):
                AllerN += Aller[(ii-2):ii] + " ";
                ii += 2
            if ii == len(Aller):
                 AllerN += Aller[(ii-2):ii]
            elif ii > len(Aller) and ii > 2:
                 AllerN += Aller[(ii-4):]
            print(self.FileStructSupport[i] + ":\n" + AllerN)
        print("--------------------")

    # Reading binary:
    def ReadHeader(self, file_handle):
        file_handle.seek(0,0)
        Kortez = struct.unpack('ii', file_handle.read(8))
        self.FileParametrs = []
        for i in range(0, 2):
            self.FileParametrs.append(Kortez[i])
        header_size = self.FileParametrs[1]
        if header_size > 8:
            remaining_header_data = file_handle.read(header_size - 8)
            expected_ints = (header_size - 8) // 4
            if len(remaining_header_data) // 4 < expected_ints:
                 print(f"Warning: Not enough data for expected header ints in {os.path.basename(self.FilePath)}. Expected {expected_ints}, got {len(remaining_header_data)//4}")
                 expected_ints = len(remaining_header_data) // 4
            if expected_ints > 0:
                 format_string = 'i' * expected_ints
                 Kortez = struct.unpack(format_string, remaining_header_data)
                 for i in range(0, len(Kortez)):
                    self.FileParametrs.append(Kortez[i])
        else:
             print(f"Warning: Header size is 8 bytes or less in {os.path.basename(self.FilePath)}. No additional header parameters read.")
        file_handle.seek(0,0)
        self.FileStruct[0] = file_handle.read(header_size)
        if len(self.FileStruct[0]) != header_size:
             print(f"Warning: Read {len(self.FileStruct[0])} bytes for header, expected {header_size} in {os.path.basename(self.FilePath)}")

    def ReadCommand(self, file_handle):
        if len(self.FileParametrs) < 3:
            print(f"Error reading commands: Not enough header parameters in {os.path.basename(self.FilePath)}")
            self.FileStruct[1] = b''
            self.Commands = []
            self.CommandArgs = []
            return
        command_section_offset = self.FileParametrs[1]
        command_section_size = self.FileParametrs[2]
        if command_section_size <= 0:
            print(f"Info: Command section size is 0 in {os.path.basename(self.FilePath)}. Skipping command read.")
            self.FileStruct[1] = b''
            self.Commands = []
            self.CommandArgs = []
            return
        file_handle.seek(command_section_offset, 0)
        command_section_data = file_handle.read(command_section_size)
        if len(command_section_data) != command_section_size:
             print(f"Warning: Read {len(command_section_data)} bytes for command section, expected {command_section_size} in {os.path.basename(self.FilePath)}")
             command_section_size = len(command_section_data)
        self.FileStruct[1] = command_section_data
        self.Commands = []
        self.CommandArgs = []
        Reader = 0
        CommandNumber = 0
        while (Reader < command_section_size):
            if Reader + 2 > command_section_size:
                 print(f"Error reading command code: Not enough data left at offset {Reader} in {os.path.basename(self.FilePath)}")
                 break
            Code = struct.unpack('H', command_section_data[Reader:Reader+2])[0]
            Reader += 2
            self.CommandArgs.append([])
            DontKnow = 1
            CommandArgsStruct = ''
            found_command_info = None
            for cmd_info in self.CommandsLibrary:
                if (Code == cmd_info[0]):
                    found_command_info = cmd_info
                    DontKnow = 0
                    CommandArgsStruct = cmd_info[1]
                    break;
            if (DontKnow == 1):
                if ((Code & 0xf000) == 0xf000):
                    CommandArgsStruct = 'hh'
                elif ((Code & 0xf000) == 0x0000):
                    CommandArgsStruct = ''
                else:
                    CommandArgsStruct = 'hhh'
            arg_start_offset = Reader
            for i in CommandArgsStruct:
                ByteSize = 0
                format_char = i
                if ((format_char == 'i') or (format_char == 'I')):
                    ByteSize = 4
                elif ((format_char == 'h') or (format_char == 'H')):
                    ByteSize = 2
                else:
                    print(f"Warning: Unknown format character '{format_char}' for command {hex(Code)} at offset {command_section_offset + Reader} in {os.path.basename(self.FilePath)}")
                    ByteSize = 0
                if ByteSize > 0:
                    if Reader + ByteSize > command_section_size:
                        print(f"Error reading command arguments: Not enough data left at offset {Reader} for format '{format_char}' (size {ByteSize}) for command {hex(Code)} in {os.path.basename(self.FilePath)}")
                        self.CommandArgs[CommandNumber].append(f"ERROR_READING_ARG_{format_char}")
                        break
                    try:
                       arg_data = command_section_data[Reader:Reader+ByteSize]
                       self.CommandArgs[CommandNumber].append(struct.unpack(format_char, arg_data)[0])
                       Reader += ByteSize
                    except struct.error as e:
                        print(f"Error unpacking argument with format '{format_char}' at offset {command_section_offset + Reader}: {e} for command {hex(Code)} in {os.path.basename(self.FilePath)}")
                        self.CommandArgs[CommandNumber].append(f"UNPACK_ERROR_{format_char}")
                        Reader += ByteSize
            self.Commands.append(Code)
            CommandNumber += 1

    def ReadStringDec(self, file_handle):
        if len(self.FileParametrs) < 4:
             print(f"Error reading string declarations: Not enough header parameters in {os.path.basename(self.FilePath)}")
             self.FileStruct[2] = b''
             self.FileStringOffsets = []
             return
        string_dec_offset = sum(self.FileParametrs[1:3])
        string_dec_size = self.FileParametrs[3]
        if string_dec_size <= 0:
            print(f"Info: String declaration section size is 0 in {os.path.basename(self.FilePath)}. Skipping read.")
            self.FileStruct[2] = b''
            self.FileStringOffsets = []
            return
        file_handle.seek(string_dec_offset, 0)
        string_dec_data = file_handle.read(string_dec_size)
        if len(string_dec_data) != string_dec_size:
             print(f"Warning: Read {len(string_dec_data)} bytes for string dec section, expected {string_dec_size} in {os.path.basename(self.FilePath)}")
             string_dec_size = len(string_dec_data)
        self.FileStruct[2] = string_dec_data
        self.FileStringOffsets = []
        expected_offsets = string_dec_size // 4
        if string_dec_size % 4 != 0:
            print(f"Warning: String declaration section size ({string_dec_size}) is not a multiple of 4 in {os.path.basename(self.FilePath)}. Reading {expected_offsets} offsets.")
        for i in range(expected_offsets):
            offset_start = i * 4
            if offset_start + 4 > string_dec_size:
                 print(f"Error reading string offset {i}: Not enough data left in {os.path.basename(self.FilePath)}")
                 break
            try:
                 self.FileStringOffsets.append(struct.unpack('i', string_dec_data[offset_start:offset_start+4])[0])
            except struct.error as e:
                 print(f"Error unpacking string offset {i} at byte offset {offset_start}: {e} in {os.path.basename(self.FilePath)}")
                 pass

    def ReadStringDef(self, file_handle):
        if len(self.FileParametrs) < 5:
            print(f"Error reading string definitions: Not enough header parameters in {os.path.basename(self.FilePath)}")
            self.FileStruct[3] = b''
            self.FileStrings = []
            return
        string_def_offset = sum(self.FileParametrs[1:4])
        string_def_size = self.FileParametrs[4]
        if string_def_size <= 0:
            print(f"Info: String definition section size is 0 in {os.path.basename(self.FilePath)}. Skipping read.")
            self.FileStruct[3] = b''
            self.FileStrings = []
            return
        file_handle.seek(string_def_offset, 0)
        string_def_data = file_handle.read(string_def_size)
        if len(string_def_data) != string_def_size:
             print(f"Warning: Read {len(string_def_data)} bytes for string def section, expected {string_def_size} in {os.path.basename(self.FilePath)}")
             string_def_size = len(string_def_data)
        self.FileStruct[3] = string_def_data
        self.FileStrings = []
        current_pos_in_data = 0
        for i in range(0, len(self.FileStringOffsets)):
            start_offset = self.FileStringOffsets[i]
            if start_offset < 0 or start_offset >= string_def_size:
                 print(f"Warning: Invalid string offset {start_offset} for string index {i} in {os.path.basename(self.FilePath)}. Skipping.")
                 self.FileStrings.append(f"INVALID_OFFSET_STRING_{i}")
                 continue
            end_offset = string_def_size
            if i < (len(self.FileStringOffsets) - 1):
                next_offset = self.FileStringOffsets[i+1]
                if next_offset >= start_offset and next_offset <= string_def_size:
                    end_offset = next_offset
                else:
                    null_pos = string_def_data.find(b'\x00', start_offset)
                    if null_pos != -1:
                        end_offset = null_pos + 1
            string_bytes = string_def_data[start_offset:end_offset]
            while string_bytes and string_bytes.endswith(b'\x00'):
                 string_bytes = string_bytes[:-1]
            try:
                self.FileStrings.append(string_bytes.decode("shift_jis"))
            except UnicodeDecodeError as e:
                print(f"Error decoding string {i} at offset {start_offset}: {e} in {os.path.basename(self.FilePath)}")
                self.FileStrings.append(f"DECODE_ERROR_STRING_{i}")

    def ReadRemaining(self, file_handle):
        if len(self.FileParametrs) < 5:
             print(f"Error reading remaining data: Not enough header parameters in {os.path.basename(self.FilePath)}")
             self.FileStruct[4] = b''
             return
        remaining_offset = sum(self.FileParametrs[1:5])
        current_pos = file_handle.tell()
        file_handle.seek(0, os.SEEK_END)
        actual_file_size = file_handle.tell()
        file_handle.seek(current_pos, 0)
        remaining_data_size = actual_file_size - remaining_offset
        if remaining_data_size <= 0:
            self.FileStruct[4] = b''
            return
        file_handle.seek(remaining_offset, 0)
        self.FileStruct[4] = file_handle.read(remaining_data_size)
        if len(self.FileStruct[4]) != remaining_data_size:
             print(f"Warning: Read {len(self.FileStruct[4])} bytes for remaining section, expected {remaining_data_size} in {os.path.basename(self.FilePath)}")

    def ReadAll(self):
        # Clear internal data structures for this file
        self.FileParametrs = []
        self.FileStruct = [b'', b'', b'', b'', b'']
        self.FileStringOffsets = []
        self.FileStrings = []
        self.CommandArgs = []
        self.Commands = []
        self.Labels = [] # Clear labels for this file

        try:
            # Open the file specifically for reading in this method
            with open(self.FilePath, mode="rb") as file_handle:
                self.ReadHeader(file_handle)
                self.ReadCommand(file_handle)
                self.ReadStringDec(file_handle)
                self.ReadStringDef(file_handle)
                self.ReadRemaining(file_handle)
            # File is automatically closed when exiting the 'with' block
        except FileNotFoundError:
             # Catch specific error for clarity
             raise FileNotFoundError(f"Input file not found: {os.path.basename(self.FilePath)}")
        except Exception as e:
            print(f"Error reading {os.path.basename(self.FilePath)}: {e}")
            raise # Re-raise the exception

    def RewriteGscFile(self):
        try:
            # Open the file specifically for writing in this method
            # This uses self.FilePath which should be correctly set (either original for rebuild
            with open(self.FilePath, mode="wb") as file_handle:
                for section_data in self.FileStruct:
                    file_handle.write(section_data)
            # File is automatically closed when exiting the 'with' block
        except Exception as e:
            print(f"Error writing {os.path.basename(self.FilePath)}: {e}")
            raise # Re-raise

    def RemakeGscFromGsc(self):
        # Assumes self.FilePath is the source .gsc file path and also the target .gsc path
        self.ReadAll()
        self.RedoAll()
        self.RewriteGscFile() # Writes back to the original path

    def DecompileGscToTxt(self):
        # Assumes self.FilePath is the source .gsc file path
        self.ReadAll() # Read the source .gsc file and populate data structures
        txt_filepath = os.path.splitext(self.FilePath)[0] + ".txt"

        try:
            # Open the target .txt file for writing using a separate file handle
            with open(txt_filepath, mode="w", encoding="shift_jis") as output_file:
                StringCount = 0
                Offset = 0
                self.Labels = [] # Clear labels for this file
                current_offset_marker = 0
                LabelNumber = 0
                for CommandNumber in range(0, len(self.Commands)):
                     current_cmd_size = 2
                     Code = self.Commands[CommandNumber]
                     CommandArgsStruct = ''
                     DontKnow = 1
                     found_command_info = None
                     for i in range(0, len(self.CommandsLibrary)):
                         if (Code == self.CommandsLibrary[i][0]):
                             found_command_info = self.CommandsLibrary[i]
                             DontKnow = 0
                             CommandArgsStruct = found_command_info[1]
                             break;
                         DontKnow = 1
                     if (DontKnow == 1):
                         if ((Code & 0xf000) == 0xf000):
                             CommandArgsStruct = 'hh'
                         elif ((Code & 0xf000) == 0x0000):
                             CommandArgsStruct = ''
                         else:
                             CommandArgsStruct = 'hhh'
                     for i in CommandArgsStruct:
                         if ((i == 'i') or (i == 'I')):
                             current_cmd_size += 4
                         elif ((i == 'h') or (i == 'H')):
                             current_cmd_size += 2
                     FindOffset = 0
                     Marbas = 0
                     doKnowOffset = -1
                     while (Marbas < len(self.ConnectedOffsetsLibrary)):
                         if (self.Commands[CommandNumber] == self.ConnectedOffsetsLibrary[Marbas][0]):
                             FindOffset = 1
                             break
                         Marbas += 1
                     if (FindOffset == 1):
                          for Mardab_idx in self.ConnectedOffsetsLibrary[Marbas][1]:
                               if Mardab_idx < len(self.CommandArgs[CommandNumber]):
                                    target_offset = self.CommandArgs[CommandNumber][Mardab_idx]
                                    found_label_index = -1
                                    for known_label in self.Labels:
                                        if known_label[1] == target_offset:
                                            found_label_index = known_label[0]
                                            break
                                    if found_label_index == -1:
                                        self.Labels.append([LabelNumber, target_offset])
                                        LabelNumber += 1
                     current_offset_marker += current_cmd_size
                self.Labels.sort(key=lambda x: x[1])
                Offset = 0
                CommandNumber = 0
                for CommandNumber in range(0, len(self.Commands)):
                    for Marmal in self.Labels:
                        if (Offset == Marmal[1]):
                            output_file.write('@' + str(Marmal[0]) + '\n')
                    DontDef = 0
                    DontKnow = 0
                    CommandName = ''
                    found_command_info = None
                    for i in range(0, len(self.CommandsLibrary)):
                         if (self.Commands[CommandNumber] == self.CommandsLibrary[i][0]):
                             found_command_info = self.CommandsLibrary[i]
                             DontKnow = 0
                             if (found_command_info[2] != ''):
                                 DontDef = 0
                             else:
                                 DontDef = 1
                             break;
                         DontDef = 1
                         DontKnow = 1
                    if (DontDef == 0):
                        CommandName = found_command_info[2]
                    else:
                        CommandName = str(self.Commands[CommandNumber])
                    current_command_args_for_txt = list(self.CommandArgs[CommandNumber])
                    Marbas = 0
                    while (Marbas < len(self.ConnectedOffsetsLibrary)):
                        if (self.Commands[CommandNumber] == self.ConnectedOffsetsLibrary[Marbas][0]):
                            for Mardab_idx in self.ConnectedOffsetsLibrary[Marbas][1]:
                                 if Mardab_idx < len(current_command_args_for_txt):
                                     arg_value = current_command_args_for_txt[Mardab_idx]
                                     found_label_index = -1
                                     for known_label in self.Labels:
                                         if known_label[1] == arg_value:
                                             found_label_index = known_label[0]
                                             break
                                     if found_label_index != -1:
                                         current_command_args_for_txt[Mardab_idx] = found_label_index
                            break
                        Marbas += 1
                    ConStr = 0
                    kk = 0
                    StringsNew = []
                    for kk in range(0, len(self.ConnectedStringsLibrary)):
                         if (self.Commands[CommandNumber] == self.ConnectedStringsLibrary[kk][0]):
                             ConStr = 1
                             break
                    if (ConStr > 0):
                         for kkk_idx in self.ConnectedStringsLibrary[kk][1]:
                             if kkk_idx < len(current_command_args_for_txt):
                                 MessageNum = current_command_args_for_txt[kkk_idx]
                                 if MessageNum >= 0 and MessageNum < len(self.FileStrings):
                                     StringsNew.append(self.FileStrings[MessageNum].replace('^n', '\n'))
                                     current_command_args_for_txt[kkk_idx] = -1
                                 else:
                                     print(f"Warning: Invalid string index {MessageNum} for command {CommandName} arg {kkk_idx} in {os.path.basename(self.FilePath)}. Keeping original value in TXT output.")
                    output_file.write("#" + CommandName + '\n')
                    output_file.write(str(current_command_args_for_txt))
                    if StringsNew:
                        for z in StringsNew:
                            output_file.write("\n>-1\n" + z)
                    if (CommandNumber != (len(self.Commands) - 1)):
                        output_file.write("\n")
                    current_cmd_size = 2
                    if found_command_info:
                        CommandArgsStruct = found_command_info[1]
                        for OfferI in CommandArgsStruct:
                             if ((OfferI == 'h') or (OfferI == 'H')):
                                 current_cmd_size += 2
                             elif ((OfferI == 'i') or (OfferI == 'I')):
                                 current_cmd_size += 4
                    elif DontKnow == 1:
                         if ((Code & 0xf000) == 0xf000):
                             current_cmd_size += 4
                         elif ((Code & 0xf000) == 0x0000):
                             current_cmd_size += 0
                         else:
                             current_cmd_size += 6
                    Offset += current_cmd_size
                referenced_string_indices = set()
                for CommandNumber in range(0, len(self.Commands)):
                     ConStr = 0
                     kk = 0
                     for kk in range(0, len(self.ConnectedStringsLibrary)):
                         if (self.Commands[CommandNumber] == self.ConnectedStringsLibrary[kk][0]):
                             ConStr = 1
                             break
                     if (ConStr > 0):
                          for kkk_idx in self.ConnectedStringsLibrary[kk][1]:
                               if kkk_idx < len(self.CommandArgs[CommandNumber]):
                                    message_index = self.CommandArgs[CommandNumber][kkk_idx]
                                    if message_index >= 0 and message_index < len(self.FileStrings):
                                         referenced_string_indices.add(message_index)
                for string_index in range(len(self.FileStrings)):
                    if string_index not in referenced_string_indices:
                        output_file.write('\n>' + str(string_index) + '\n')
                        string_content_for_txt = self.FileStrings[string_index].replace('^n', '\n')
                        output_file.write(string_content_for_txt)
            # File is automatically closed by 'with' statement
        except FileNotFoundError:
             raise FileNotFoundError(f"Input file not found during decompile: {os.path.basename(self.FilePath)}")
        except Exception as e:
            print(f"Error decompiling {os.path.basename(self.FilePath)}: {e}")
            raise # Re-raise

    def CompileTxtToGsc(self):
        # Assumes self.FilePath is the source .txt file path
        gsc_filepath = os.path.splitext(self.FilePath)[0] + ".gsc"
        # Clear GscFile internal state, but NOT FilePath
        self.FileParametrs = []
        self.FileStruct = [b'', b'', b'', b'', b'']
        self.FileStringOffsets = []
        self.FileStrings = []
        self.CommandArgs = []
        self.Commands = []
        self.Labels = []

        try:
            # Open the source .txt file for reading
            with open(self.FilePath, mode="r", encoding="shift_jis") as input_file:
                Lines = input_file.read().split('\n')
            # File is automatically closed by 'with' statement

            Offset = 0
            LenOff = 0
            self.Labels = []
            temp_commands = []
            temp_command_args = []
            line_index = 0
            while (line_index < len(Lines)):
                 line = Lines[line_index].strip()
                 if line == '' or line.startswith('$'):
                     line_index += 1
                     continue
                 if line.startswith('@'):
                     try:
                          LabelNumber = int(line[1:])
                          NotAnythingNew = 0
                          for Marbas in self.Labels:
                             if (LabelNumber == Marbas[0]):
                                 NotAnythingNew = 1
                                 break
                          if NotAnythingNew == 0:
                             self.Labels.append([LabelNumber, Offset])
                             LenOff += 1
                     except ValueError:
                         print(f"Error: Invalid label format '{line}' at line {line_index + 1} in {os.path.basename(self.FilePath)}. Expected '@N' where N is an integer.")
                     line_index += 1
                 elif line.startswith('#'):
                     CommandDefString = line[1:]
                     CommandType = 0
                     DontKnow = 1
                     found_command_info = None
                     CommandArgsStruct = ''
                     try:
                         CommandType = int(CommandDefString)
                         for cmd_info in self.CommandsLibrary:
                              if CommandType == cmd_info[0]:
                                  found_command_info = cmd_info
                                  DontKnow = 0
                                  CommandArgsStruct = cmd_info[1]
                                  break
                     except ValueError:
                          for cmd_info in self.CommandsLibrary:
                               if CommandDefString == cmd_info[2]:
                                   CommandType = cmd_info[0]
                                   found_command_info = cmd_info
                                   DontKnow = 0
                                   CommandArgsStruct = cmd_info[1]
                                   break
                     if DontKnow == 1:
                         try:
                              CommandType = int(CommandDefString)
                              if ((CommandType & 0xf000) == 0xf000):
                                 CommandArgsStruct = 'hh'
                              elif ((CommandType & 0xf000) == 0x0000):
                                 CommandArgsStruct = ''
                              else:
                                 CommandArgsStruct = 'hhh'
                         except ValueError:
                              print(f"Error: Unknown command '{CommandDefString}' cannot be parsed as integer code at line {line_index + 1} in {os.path.basename(self.FilePath)}. Skipping command.")
                              line_index += 1
                              if line_index < len(Lines) and Lines[line_index].strip().startswith('['):
                                   line_index += 1
                                   while line_index < len(Lines) and Lines[line_index].strip().startswith('>-1'):
                                        line_index += 1
                                        while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                                             line_index += 1
                                   continue
                              else:
                                  continue
                     temp_commands.append(CommandType)
                     current_cmd_size = 2
                     for OfferI in CommandArgsStruct:
                         if ((OfferI == 'h') or (OfferI == 'H')):
                             current_cmd_size += 2
                         elif ((OfferI == 'i') or (OfferI == 'I')):
                             current_cmd_size += 4
                     line_index += 1
                     if line_index >= len(Lines):
                         print(f"Error: Unexpected end of file after command definition at line {line_index} in {os.path.basename(self.FilePath)}. Missing arguments line.")
                         temp_command_args.append([])
                         break
                     args_line = Lines[line_index].strip()
                     if not args_line.startswith('[') or not args_line.endswith(']'):
                          print(f"Error: Expected arguments line starting with '[' and ending with ']' after command definition at line {line_index + 1} in {os.path.basename(self.FilePath)}. Got '{args_line}'. Skipping args.")
                          temp_command_args.append([])
                     else:
                         args_content = args_line[1:-1].strip()
                         CommandCTR_str = args_content.split(',')
                         CommandNEW = []
                         for arg_str in CommandCTR_str:
                             arg_str = arg_str.strip()
                             if arg_str == '':
                                  continue
                             try:
                                 CommandNEW.append(int(arg_str))
                             except ValueError:
                                 print(f"Error: Invalid integer argument '{arg_str}' at line {line_index + 1} in {os.path.basename(self.FilePath)}. Skipping.")
                                 CommandNEW.append(f"INVALID_ARG_{arg_str}")
                         temp_command_args.append(CommandNEW)
                     line_index += 1
                     while line_index < len(Lines):
                         line = Lines[line_index].strip()
                         if line.startswith('>-1'):
                             line_index += 1
                             while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                                 line_index += 1
                         else:
                             break
                     Offset += current_cmd_size
                 elif line.startswith('>'):
                     try:
                         original_index = int(line[1:].strip())
                     except ValueError:
                         print(f"Error: Invalid string index format '{line}' at line {line_index + 1} in {os.path.basename(self.FilePath)}. Expected '>N' where N is an integer index. Skipping string.")
                         line_index += 1
                         while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                              line_index += 1
                         continue
                     line_index += 1
                     StringContent = ''
                     KostilPer = 1
                     while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                          current_content_line = Lines[line_index]
                          if KostilPer == 1:
                              KostilPer = 0
                          else:
                              StringContent += '^n'
                          StringContent += current_content_line
                          line_index += 1
                 else:
                      line_index += 1
            self.Commands = []
            self.CommandArgs = []
            self.FileStrings = []
            string_pool_index = 0
            line_index = 0
            command_index = 0
            while (line_index < len(Lines)):
                 line = Lines[line_index].strip()
                 if line == '' or line.startswith('$'):
                     line_index += 1
                     continue
                 if line.startswith('@'):
                     line_index += 1
                     continue
                 if line.startswith('#'):
                     if command_index < len(temp_commands):
                         CommandType = temp_commands[command_index]
                         CommandNEW = temp_command_args[command_index]
                     else:
                          print(f"Error: Command/argument mismatch during Pass 2 at line {line_index + 1} in {os.path.basename(self.FilePath)}. Skipping.")
                          line_index += 1
                          command_index += 1
                          continue
                     self.Commands.append(CommandType)
                     processed_args_for_binary = list(CommandNEW)
                     Farba = 0
                     while (Farba < len(self.ConnectedOffsetsLibrary)):
                         if (CommandType == self.ConnectedOffsetsLibrary[Farba][0]):
                             for NewZeland_idx in self.ConnectedOffsetsLibrary[Farba][1]:
                                  if NewZeland_idx < len(processed_args_for_binary) and isinstance(processed_args_for_binary[NewZeland_idx], int):
                                      arg_value = processed_args_for_binary[NewZeland_idx]
                                      found_offset = None
                                      for Ai in self.Labels:
                                          if Ai[0] == arg_value:
                                              found_offset = Ai[1]
                                              break
                                      if found_offset is not None:
                                          processed_args_for_binary[NewZeland_idx] = found_offset
                                      else:
                                          print(f"Error: Label '{arg_value}' referenced in command {hex(CommandType)} argument {NewZeland_idx} at line {line_index + 1} was not defined in {os.path.basename(self.FilePath)}. Cannot assign offset. Setting argument to 0.")
                                          processed_args_for_binary[NewZeland_idx] = 0
                                  elif NewZeland_idx < len(processed_args_for_binary):
                                       print(f"Error: Argument {NewZeland_idx} for command {hex(CommandType)} at line {line_index + 1} in {os.path.basename(self.FilePath)} is not an integer ({processed_args_for_binary[NewZeland_idx]}). Expected label number. Cannot assign offset. Setting argument to 0.")
                                       if NewZeland_idx < len(processed_args_for_binary):
                                            processed_args_for_binary[NewZeland_idx] = 0
                             break
                         Farba += 1
                     self.CommandArgs.append(processed_args_for_binary)
                     line_index += 1
                     ConStr = 0
                     kk = 0
                     for kk in range(0, len(self.ConnectedStringsLibrary)):
                         if (CommandType == self.ConnectedStringsLibrary[kk][0]):
                             ConStr = 1
                             break
                     connected_arg_indices = []
                     if ConStr > 0:
                         connected_arg_indices = self.ConnectedStringsLibrary[kk][1]
                     string_read_counter = 0
                     while line_index < len(Lines):
                         line = Lines[line_index].strip()
                         if line.startswith('>-1'):
                             line_index += 1
                             StringContent = ''
                             KostilPer = 1
                             while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                                 current_content_line = Lines[line_index]
                                 if KostilPer == 1:
                                     KostilPer = 0
                                 else:
                                     StringContent += '^n'
                                 StringContent += current_content_line
                                 line_index += 1
                             self.FileStrings.append(StringContent)
                             if string_read_counter < len(connected_arg_indices):
                                 arg_idx_to_update = connected_arg_indices[string_read_counter]
                                 if arg_idx_to_update < len(processed_args_for_binary) and processed_args_for_binary[arg_idx_to_update] == -1:
                                     processed_args_for_binary[arg_idx_to_update] = string_pool_index
                                 else:
                                      print(f"Warning: Argument index {arg_idx_to_update} for command {hex(CommandType)} at line {line_index} in {os.path.basename(self.FilePath)} was expected to be -1 but was not. Cannot assign string index {string_pool_index}. Keeping original argument value.")
                                 string_read_counter += 1
                             else:
                                  print(f"Warning: More connected strings (>-1) found than expected arguments for command {hex(CommandType)} at line {line_index} in {os.path.basename(self.FilePath)}. Skipping association for this string.")
                             string_pool_index += 1
                         else:
                             break
                     command_index += 1
                 elif line.startswith('>'):
                     try:
                         original_index = int(line[1:].strip())
                     except ValueError:
                         print(f"Error: Invalid string index format '{line}' at line {line_index + 1} in {os.path.basename(self.FilePath)}. Expected '>N' where N is an integer index. Skipping string.")
                         line_index += 1
                         while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                              line_index += 1
                         continue
                     line_index += 1
                     StringContent = ''
                     KostilPer = 1
                     while line_index < len(Lines) and not Lines[line_index].strip().startswith(('#', '>', '@', '$')):
                          current_content_line = Lines[line_index]
                          if KostilPer == 1:
                              KostilPer = 0
                          else:
                              StringContent += '^n'
                          StringContent += current_content_line
                          line_index += 1
                     string_for_binary = StringContent.replace('\\', '^')
                     self.FileStrings.append(string_for_binary)
                     string_pool_index += 1
                 else:
                      line_index += 1
            self.RedoAll()
            # Open the target GSC file for writing
            with open(gsc_filepath, mode="wb") as output_file:
                for section_data in self.FileStruct:
                     output_file.write(section_data)
            # File is automatically closed by 'with' statement

        except FileNotFoundError:
             raise FileNotFoundError(f"Input file not found during compile: {os.path.basename(self.FilePath)}")
        except Exception as e:
            print(f"Error compiling {os.path.basename(self.FilePath)}: {e}")
            raise # Re-raise

    def RefreshHeaderPrm(self):
        header_size = 36
        command_section_size = len(self.FileStruct[1])
        string_dec_size = len(self.FileStruct[2])
        string_def_size = len(self.FileStruct[3])
        remaining_size = len(self.FileStruct[4])
        total_size = header_size + command_section_size + string_dec_size + string_def_size + remaining_size
        self.FileParametrs = [
            total_size,
            header_size,
            command_section_size,
            string_dec_size,
            string_def_size,
            4,
            1,
            4,
            1
        ]

    def RemakeHeaderFromPrm(self):
        self.FileStruct[0] = b''
        try:
            if len(self.FileParametrs) < 9:
                 print(f"Warning: Not enough parameters ({len(self.FileParametrs)}) to pack header (expected 9) in {os.path.basename(self.FilePath)}. Padding with zeros.")
                 padded_params = self.FileParametrs + [0] * (9 - len(self.FileParametrs))
            elif len(self.FileParametrs) > 9:
                 padded_params = self.FileParametrs[:9]
            else:
                 padded_params = self.FileParametrs
            for param in padded_params:
                 self.FileStruct[0] += struct.pack("i", param)
            expected_header_size = self.FileParametrs[1] if len(self.FileParametrs) > 1 else 36
            if len(self.FileStruct[0]) != expected_header_size:
                 print(f"Warning: Packed header size ({len(self.FileStruct[0])}) does not match FileParametrs[1] ({expected_header_size}) in {os.path.basename(self.FilePath)}. This might cause issues.")
        except struct.error as e:
             print(f"Error packing header parameters: {e} in {os.path.basename(self.FilePath)}")
             self.FileStruct[0] = b'\x00' * (self.FileParametrs[1] if len(self.FileParametrs) > 1 else 36)

    def RedoHeader(self):
        self.RefreshHeaderPrm()
        self.RemakeHeaderFromPrm()

    def RemakeOffsetsFromStrings(self):
        self.FileStringOffsets = []
        Dohod = 0
        for string_content in self.FileStrings:
            self.FileStringOffsets.append(Dohod)
            encoded_string = string_content.encode("shift_jis")
            Dohod += len(encoded_string) + 1

    def RewriteStringDec(self):
        self.FileStruct[2] = b''
        try:
             for offset in self.FileStringOffsets:
                 self.FileStruct[2] += struct.pack("i", offset)
        except struct.error as e:
             print(f"Error packing string offsets: {e} in {os.path.basename(self.FilePath)}")
             self.FileStruct[2] = b''

    def RewriteStringDef(self):
        self.FileStruct[3] = b''
        try:
             for string_content in self.FileStrings:
                 self.FileStruct[3] += string_content.encode("shift_jis") + b'\x00'
        except Exception as e:
             print(f"Error encoding/packing string content: {e} in {os.path.basename(self.FilePath)}")
             self.FileStruct[3] = b''

    def RedoStrings(self):
        self.RemakeOffsetsFromStrings()
        self.RewriteStringDec()
        self.RewriteStringDef()

    def RedoCommands(self):
        self.FileStruct[1] = b''
        try:
            for NumCom in range(0, len(self.Commands)):
                Code = self.Commands[NumCom]
                DontKnow = 1
                CommandArgsStruct = ''
                found_command_info = None
                for i in range(0, len(self.CommandsLibrary)):
                    if (Code == self.CommandsLibrary[i][0]):
                        found_command_info = self.CommandsLibrary[i]
                        DontKnow = 0
                        CommandArgsStruct = found_command_info[1]
                        break;
                if (DontKnow == 1):
                    if ((Code & 0xf000) == 0xf000):
                        CommandArgsStruct = 'hh'
                    elif ((Code & 0xf000) == 0x0000):
                        CommandArgsStruct = ''
                    else:
                        CommandArgsStruct = 'hhh'
                self.FileStruct[1] += struct.pack('H', Code)
                current_command_args = self.CommandArgs[NumCom]
                if len(current_command_args) != len(CommandArgsStruct):
                     padded_args = list(current_command_args) + [0] * (len(CommandArgsStruct) - len(current_command_args))
                     current_command_args_to_pack = padded_args[:len(CommandArgsStruct)]
                else:
                    current_command_args_to_pack = current_command_args
                for NumArg in range(len(CommandArgsStruct)):
                    CommandStruct = CommandArgsStruct[NumArg]
                    arg_value = current_command_args_to_pack[NumArg]
                    if not isinstance(arg_value, int):
                        print(f"Error: Argument {NumArg} for command {hex(Code)} at index {NumCom} is not an integer ({arg_value}) in {os.path.basename(self.FilePath)}. Cannot pack with format '{CommandStruct}'. Setting to 0.")
                        arg_value = 0
                    try:
                        self.FileStruct[1] += struct.pack(CommandStruct, arg_value)
                    except struct.error as e:
                        print(f"Error packing argument {NumArg} ({arg_value}) with format '{CommandStruct}' for command {hex(Code)} at index {NumCom}: {e} in {os.path.basename(self.FilePath)}")
                        try:
                             if CommandStruct in ('i', 'I'):
                                  self.FileStruct[1] += struct.pack(CommandStruct, 0)
                             elif CommandStruct in ('h', 'H'):
                                  self.FileStruct[1] += struct.pack(CommandStruct, 0)
                             else:
                                  print(f"Error: Cannot pack argument {NumArg} for command {hex(Code)} with unknown format '{CommandStruct}' in {os.path.basename(self.FilePath)}")
                        except struct.error:
                             print(f"Critical Error: Cannot pack 0 with format '{CommandStruct}' for command {hex(Code)} in {os.path.basename(self.FilePath)}. Skipping argument.")
        except Exception as e:
             print(f"An unexpected error occurred during command packing: {e} in {os.path.basename(self.FilePath)}")
             self.FileStruct[1] = b''

    def RedoRemaining(self):
        self.FileStruct[4] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Modified ReinitAll to *not* clear FilePath
    def ReinitAll(self):
        # self.FilePath = '' # REMOVED: Do not clear FilePath here
        self.FileParametrs = []
        self.FileStruct = [b'', b'', b'', b'', b'']
        self.FileStringOffsets = []
        self.FileStrings = []
        self.CommandArgs = []
        self.Commands = []
        self.Labels = []

    # Technical file work (using FilePath):
    # Simplified file operations - open/close explicitly in calling methods
    # Removed ReadFileBin, ReadFile, WriteFileBin, WriteFile methods
    # The read/write logic will be handled inline or by creating file objects directly

    def CloseFile(self):
        # This method is less relevant now that file handles are managed locally in read/write methods
        # but keep it as a safeguard if self.File is ever used directly again.
        if hasattr(self, 'File') and not hasattr(self.File, 'closed') and self.File is not None: # Added check for None and existence of closed attribute
            self.File.close()
            self.File = None # Set to None after closing


class GUI():
    root = Tk()
    Language = 'ENG' #RUS
    FolderPath = StringVar()
    LeftSide = Frame(root)
    LeftTop = Frame(root)
    LeftMiddle = Frame(root)
    LeftBottom = Frame(root)
    RussianLang = Button(root)
    EnglishLang = Button(root)
    FolderEntry = Entry(root)
    SelectFolderButton = Button(root)
    Clearer = Button(root) # Kept for backward compatibility with language setting
    Undefiner = Button(root) # Kept for backward compatibility with language setting
    ClearFolderButton = None # New button for Clear action
    UndefineFolderButton = None # New button for Undefine action
    SpacerTop = LabelFrame(root)
    Rebuild = Button(root)
    Decompile = Button(root)
    Compile = Button(root)
    SpacerBottom = LabelFrame(root)
    CommonHelper = Button(root)
    CommandHelper = Button(root)
    SyntaxHelper = Button(root)
    Outer = Text(root)

    def __init__(self):
        self.root['background']='white'
        self.root.resizable(width=False, height=True)
        self.root.geometry("400x500+{}+{}".format((self.root.winfo_screenwidth()-400)//2, (self.root.winfo_screenheight()-500)//2))
        self.root.title("GscScriptCompAndDecompiler by Tester 2.0 (Folder Mode)")
        self.LeftSide = Frame(self.root, width=400, height=600)
        self.LeftSide.pack(side='left', fill='y')
        self.LeftTop = Frame(self.LeftSide, width=400, height=32, bg="grey")
        self.LeftMiddle = Frame(self.LeftSide, width=400, height=90, bg="grey")
        self.LeftBottom = Frame(self.LeftSide, width=400, height=600, bg="grey")
        self.LeftTop.pack_propagate(False)
        self.LeftTop.pack(fill='x')
        self.LeftMiddle.pack_propagate(False)
        self.LeftMiddle.pack(fill='x')
        self.LeftBottom.pack(fill='both', expand=True)
        self.InitLangButtons()
        self.InitLeftSide()
        self.SetLangEng()

    def InitLangButtons(self):
        self.RussianLang = Button(self.LeftTop, command=self.SetLangRus, bg='white', activebackground='gray', font = 'calibri 12', text='　 　　　 　　　РУССКИЙ')
        self.EnglishLang = Button(self.LeftTop, command=self.SetLangEng, bg='white', activebackground='gray', font = 'calibri 12', text='ENGLISH　　　 　　　　 　')
        self.RussianLang.pack(side='left', fill='x', expand='yes')
        self.EnglishLang.pack(side='right', fill='x', expand='yes')

    def InitLeftSide(self):
        FolderSelectFrame = Frame(self.LeftMiddle, bg="grey")
        self.FolderEntry = Entry(FolderSelectFrame, textvariable=self.FolderPath, width=30, bd=2, fg="black", font='calibri 12', state='readonly')
        self.SelectFolderButton = Button(FolderSelectFrame, command=self.SelectFolder, bg='white', activebackground='gray', font = 'calibri 12', text='Select Folder')
        self.SelectFolderButton.pack(side='right', padx=2)
        self.FolderEntry.pack(side='left', fill='x', expand='yes', padx=2)
        FolderSelectFrame.pack(side='top', fill='x', pady=5)
        ActionButtonsFrame = Frame(self.LeftMiddle, bg="grey")
        self.DefineFolderButton = Button(ActionButtonsFrame, command=self.DefineFolder, bg='white', activebackground='gray', font = 'calibri 12', text='                  DEFINE')
        # Use new button names for clarity and avoid conflict with language setting attributes
        self.ClearFolderButton = Button(ActionButtonsFrame, command=self.ClearFolder, bg='white', activebackground='gray', font = 'calibri 12', text='          CLEAR          ')
        self.UndefineFolderButton = Button(ActionButtonsFrame, command=self.UndefineFolder, bg='white', activebackground='gray', font = 'calibri 12', text='UNDEFINE               ')
        # Assign the new buttons to the old names for language setting methods
        self.Clearer = self.ClearFolderButton
        self.Undefiner = self.UndefineFolderButton

        self.DefineFolderButton.pack(side='left', fill='x', expand='yes', padx=1)
        self.ClearFolderButton.pack(side='left', fill='x', expand='yes', padx=1)
        self.UndefineFolderButton.pack(side='left', fill='x', expand='yes', padx=1)
        ActionButtonsFrame.pack(side='top', fill='x', pady=5)
        self.SpacerTop = LabelFrame(self.LeftBottom, bg='white', height=150, width=400, font = 'calibri 12')
        self.SpacerTop.pack_propagate(False)
        self.SpacerTop.pack(side='top', fill='x')
        self.Rebuild = Button(self.SpacerTop, command=self.RebuildFolder, bg='white', activebackground='gray', font = 'calibri 12', text='Rebuild .gsc files in folder (.gsc -> .gsc)')
        self.Rebuild.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.Decompile = Button(self.SpacerTop, command=self.DecompileFolder, bg='white', activebackground='gray', font = 'calibri 12', text='Decompile .gsc files in folder (.gsc -> .txt)')
        self.Decompile.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.Compile = Button(self.SpacerTop, command=self.CompileFolder, bg='white', activebackground='gray', font = 'calibri 12', text='Compile .txt files in folder (.txt -> .gsc)')
        self.Compile.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.SpacerBottom = LabelFrame(self.LeftBottom, bg='white', height=150, width=400, font = 'calibri 12')
        self.SpacerBottom.pack_propagate(False)
        self.SpacerBottom.pack(side='top', fill='x')
        self.CommonHelper = Button(self.SpacerBottom, command=self.CommonHelp, bg='white', activebackground='gray', font = 'calibri 12', text='Common help')
        self.CommonHelper.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.CommandHelper = Button(self.SpacerBottom, command=self.CommandHelp, bg='white', activebackground='gray', font = 'calibri 12', text='Command help')
        self.CommandHelper.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.SyntaxHelper = Button(self.SpacerBottom, command=self.SyntaxHelp, bg='white', activebackground='gray', font = 'calibri 12', text='Syntax help')
        self.SyntaxHelper.pack(side='top', fill="x", expand='yes', pady=2, padx=5)
        self.Outer = Text(self.LeftBottom, width=400, height=5, font='arial 10', state=DISABLED, wrap='word')
        self.Outer.pack(side='bottom', fill='both', expand=True, pady=5, padx=5)
        self.FolderPath.set("")
        self.UndefineFolder()

    def SetLangRus(self):
        self.Language = "RUS"
        self.root.title("GscScriptCompAndDecompiler от Tester-а 2.0 (Режим Папки)")
        self.SelectFolderButton['text'] = 'Выбрать Папку'
        self.DefineFolderButton['text'] = "           ОПРЕДЕЛИТЬ"
        self.ClearFolderButton['text'] = " ОЧИСТИТЬ "
        self.UndefineFolderButton['text'] = "РАЗОПРЕДЕЛИТЬ        "
        self.SpacerTop['text'] = 'КОМАНДЫ:'
        self.Rebuild['text'] = 'Перестроить .gsc файлы в папке (.gsc -> .gsc)'
        self.Decompile['text'] = 'Декомпилировать .gsc файлы в папке (.gsc -> .txt)'
        self.Compile['text'] = 'Компилировать .txt файлы в папке (.txt -> .gsc)'
        self.SpacerBottom['text'] = 'ПОМОЩЬ:'
        self.CommonHelper['text'] = 'Общая помощь'
        self.CommandHelper['text'] = 'Помощь по командам'
        self.SyntaxHelper['text'] = 'Помощь по синтаксису'
        self.UpdateOuter("Язык успешно сменён.")

    def SetLangEng(self):
        self.Language = "ENG"
        self.root.title("GscScriptCompAndDecompiler by Tester 2.0 (Folder Mode)")
        self.SelectFolderButton['text'] = 'Select Folder'
        self.DefineFolderButton['text'] = "                  DEFINE"
        self.ClearFolderButton['text'] = "          CLEAR          "
        self.UndefineFolderButton['text'] = "UNDEFINE               "
        self.SpacerTop['text'] = 'COMMANDS:'
        self.Rebuild['text'] = 'Rebuild .gsc files in folder (.gsc -> .gsc)'
        self.Decompile['text'] = 'Decompile .gsc files in folder (.gsc -> .txt)'
        self.Compile['text'] = 'Compile .txt files in folder (.txt -> .gsc)'
        self.SpacerBottom['text'] = 'HELP:'
        self.CommonHelper['text'] = 'Common help'
        self.CommandHelper['text'] = 'Command help'
        self.SyntaxHelper['text'] = 'Syntax help'
        self.UpdateOuter("The language was successfully changed.")

    def UpdateOuter(self, text):
        self.Outer['state'] = NORMAL
        self.Outer.delete(1.0, END)
        self.Outer.insert(END, text)
        self.Outer['state'] = DISABLED
        self.root.update_idletasks()

    def AppendOuter(self, text):
        self.Outer['state'] = NORMAL
        self.Outer.insert(END, text + "\n")
        self.Outer.see(END)
        self.Outer['state'] = DISABLED
        self.root.update_idletasks()

    def SelectFolder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.FolderPath.set(folder_path)
            self.DefineFolder()

    def ClearFolder(self):
        # The FolderEntry is readonly, so clearing it isn't the primary action.
        # This button doesn't have a clear function in the folder mode logic.
        # UndefineFolder is used to reset the selected folder state.
        # Keeping this method stub but it won't do anything meaningful in this version.
        if (self.Language == 'RUS'):
            self.UpdateOuter("Для сброса папки используйте кнопку 'РАЗОПРЕДЕЛИТЬ'.")
        else:
            self.UpdateOuter("Use the 'UNDEFINE' button to clear the folder selection.")

    def DefineFolder(self):
        folder_path = self.FolderPath.get()
        if os.path.isdir(folder_path):
            self.FolderEntry['state'] = 'readonly'
            self.DefineFolderButton['state'] = DISABLED
            self.ClearFolderButton['state'] = DISABLED
            self.UndefineFolderButton['state'] = NORMAL
            self.Rebuild['state'] = NORMAL
            self.Decompile['state'] = NORMAL
            self.Compile['state'] = NORMAL
            if (self.Language == 'RUS'):
                self.UpdateOuter(f"Папка '{folder_path}' успешно определена.")
            else:
                self.UpdateOuter(f"Folder '{folder_path}' was successfully defined.")
        else:
            self.FolderPath.set("")
            if (self.Language == 'RUS'):
                self.UpdateOuter("Некорректный путь к папке или папка не выбрана.")
            else:
                self.UpdateOuter("Invalid folder path or no folder selected.")
            self.UndefineFolder()

    def UndefineFolder(self):
        self.FolderPath.set("")
        self.FolderEntry['state'] = 'readonly'
        self.DefineFolderButton['state'] = NORMAL
        self.ClearFolderButton['state'] = NORMAL
        self.UndefineFolderButton['state'] = DISABLED
        self.Rebuild['state'] = DISABLED
        self.Decompile['state'] = DISABLED
        self.Compile['state'] = DISABLED
        if (self.Language == 'RUS'):
            self.UpdateOuter("Папка успешно разопределена.")
        else:
            self.UpdateOuter("The folder was successfully undefined.")

    def RebuildFolder(self):
        folder_path = self.FolderPath.get()
        if not os.path.isdir(folder_path):
            if (self.Language == 'RUS'):
                 self.UpdateOuter("Папка не определена или не существует.")
            else:
                 self.UpdateOuter("Folder is not defined or does not exist.")
            return
        gsc_files = glob.glob(os.path.join(folder_path, "*.gsc"))
        if not gsc_files:
            if (self.Language == 'RUS'):
                 self.UpdateOuter(f"В выбранной папке '{folder_path}' не найдено файлов .gsc.")
            else:
                 self.UpdateOuter(f"No .gsc files found in the selected folder '{folder_path}'.")
            return
        processed_count = 0
        failed_files = []
        self.UpdateOuter(f"Начата перестройка {len(gsc_files)} файлов .gsc в папке '{folder_path}'...")
        for file_path in gsc_files:
            file_name = os.path.basename(file_path)
            self.AppendOuter(f"Обработка файла: {file_name}...")
            try:
                # Instantiate GscFile with the full file path and binary mode (0)
                new_script = GscFile(file_path, 0) # FilePath is set in __init__
                # Reinit is done internally by ReadAll now
                new_script.RemakeGscFromGsc() # Rebuild process
                self.AppendOuter(f"  Успешно перестроен: {file_name}")
                processed_count += 1
            except FileNotFoundError:
                 self.AppendOuter(f"  Ошибка: Файл {file_name} не найден.")
                 failed_files.append(file_name)
            except Exception as e:
                self.AppendOuter(f"  Ошибка при перестройке {file_name}: {e}")
                failed_files.append(file_name)
        if failed_files:
             if (self.Language == 'RUS'):
                 self.AppendOuter(f"Перестройка завершена. Успешно перестроено {processed_count} из {len(gsc_files)} файлов. Ошибки в файлах: {', '.join(failed_files)}")
             else:
                 self.AppendOuter(f"Rebuild complete. Successfully rebuilt {processed_count} out of {len(gsc_files)} files. Failed files: {', '.join(failed_files)}")
        else:
             if (self.Language == 'RUS'):
                  self.AppendOuter(f"Перестройка успешно завершена для всех {processed_count} файлов .gsc.")
             else:
                  self.AppendOuter(f"Rebuild successfully completed for all {processed_count} .gsc files.")

    def DecompileFolder(self):
        folder_path = self.FolderPath.get()
        if not os.path.isdir(folder_path):
            if (self.Language == 'RUS'):
                 self.UpdateOuter("Папка не определена или не существует.")
            else:
                 self.UpdateOuter("Folder is not defined or does not exist.")
            return
        gsc_files = glob.glob(os.path.join(folder_path, "*.gsc"))
        if not gsc_files:
            if (self.Language == 'RUS'):
                 self.UpdateOuter(f"В выбранной папке '{folder_path}' не найдено файлов .gsc.")
            else:
                 self.UpdateOuter(f"No .gsc files found in the selected folder '{folder_path}'.")
            return
        processed_count = 0
        failed_files = []
        self.UpdateOuter(f"Начата декомпиляция {len(gsc_files)} файлов .gsc в папке '{folder_path}'...")
        for file_path in gsc_files:
            file_name = os.path.basename(file_path)
            self.AppendOuter(f"Обработка файла: {file_name}...")
            try:
                # Instantiate GscFile with the full file path and binary mode (0)
                new_script = GscFile(file_path, 0) # FilePath is set in __init__
                # Reinit is done internally by ReadAll now
                new_script.DecompileGscToTxt() # Decompile process
                self.AppendOuter(f"  Успешно декомпилирован: {file_name}")
                processed_count += 1
            except FileNotFoundError:
                 self.AppendOuter(f"  Ошибка: Файл {file_name} не найден.")
                 failed_files.append(file_name)
            except Exception as e:
                self.AppendOuter(f"  Ошибка при декомпиляции {file_name}: {e}")
                failed_files.append(file_name)
        if failed_files:
             if (self.Language == 'RUS'):
                 self.AppendOuter(f"Декомпиляция завершена. Успешно декомпилировано {processed_count} из {len(gsc_files)} файлов. Ошибки в файлах: {', '.join(failed_files)}")
             else:
                 self.AppendOuter(f"Decompile complete. Successfully decompiled {processed_count} out of {len(gsc_files)} files. Failed files: {', '.join(failed_files)}")
        else:
             if (self.Language == 'RUS'):
                  self.AppendOuter(f"Декомпиляция успешно завершена для всех {processed_count} файлов .gsc.")
             else:
                  self.AppendOuter(f"Decompile successfully completed for all {processed_count} .gsc files.")

    def CompileFolder(self):
        folder_path = self.FolderPath.get()
        if not os.path.isdir(folder_path):
            if (self.Language == 'RUS'):
                 self.UpdateOuter("Папка не определена или не существует.")
            else:
                 self.UpdateOuter("Folder is not defined or does not exist.")
            return
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        if not txt_files:
            if (self.Language == 'RUS'):
                 self.UpdateOuter(f"В выбранной папке '{folder_path}' не найдено файлов .txt.")
            else:
                 self.UpdateOuter(f"No .txt files found in the selected folder '{folder_path}'.")
            return
        processed_count = 0
        failed_files = []
        self.UpdateOuter(f"Начата компиляция {len(txt_files)} файлов .txt в папке '{folder_path}'...")
        for file_path in txt_files:
            file_name = os.path.basename(file_path)
            self.AppendOuter(f"Обработка файла: {file_name}...")
            try:
                # Instantiate GscFile with the full file path and text mode (1)
                new_script = GscFile(file_path, 1) # FilePath is set in __init__
                # Reinit is done internally by CompileTxtToGsc now
                new_script.CompileTxtToGsc() # Compile process
                self.AppendOuter(f"  Успешно компилирован: {file_name}")
                processed_count += 1
            except FileNotFoundError:
                 self.AppendOuter(f"  Ошибка: Файл {file_name} не найден.")
                 failed_files.append(file_name)
            except Exception as e:
                self.AppendOuter(f"  Ошибка при компиляции {file_name}: {e}")
                failed_files.append(file_name)
        if failed_files:
             if (self.Language == 'RUS'):
                 self.AppendOuter(f"Компиляция завершена. Успешно компилировано {processed_count} из {len(txt_files)} файлов. Ошибки в файлах: {', '.join(failed_files)}")
             else:
                 self.AppendOuter(f"Compile complete. Successfully compiled {processed_count} out of {len(txt_files)} files. Failed files: {', '.join(failed_files)}")
        else:
             if (self.Language == 'RUS'):
                  self.AppendOuter(f"Компиляция успешно завершена для всех {processed_count} файлов .txt.")
             else:
                  self.AppendOuter(f"Compile successfully completed for all {processed_count} .txt files.")

    def CommonHelp(self):
        if (self.Language == "RUS"):
            mb.showwarning("Общая помощь", """Данная программа разработана для корректной работы с файлами .gsc движка codeX RScript. Эта версия работает с *папками*, обрабатывая все .gsc или .txt файлы в выбранной директории.\n\nДанная программа позволяет:\n1. Перестраивать .gsc-файлы из самих себя в выбранной папке, тем самым по сути их оптимизируя. Также позволяет просматривать ход обработки и потенциальные ошибки для каждого файла.\n2. Декомпиляция .gsc-файлов в .txt в выбранной папке. Позволяет массово подготовить скрипты к редактированию.\n3. Компиляция .txt-файлов в .gsc в выбранной папке. Позволяет массово пересобирать .gsc на основе отредактированных .txt файлов.\n\nДля использования:\n1. Перетащите .gsc-файлы или .txt-файлы (для компиляции) в одну папку.\n2. Нажмите кнопку 'Выбрать Папку' и выберите эту директорию.\n3. Нажмите 'ОПРЕДЕЛИТЬ'. Путь к папке появится в поле.\n4. Используйте команды снизу для обработки файлов в этой папке.""")
        else:
            mb.showwarning("Common help", """This program was developed for correctly working with .gsc files of the engine codeX RScript. This version works with *folders*, processing all .gsc or .txt files in the selected directory.\n\nThis program allows you to:\n1. Rebuild .gsc-files from themselves in the selected folder, optimizing them. You can also see the processing progress and potential errors for each file.\n2. Decompile .gsc-files to .txt in the selected folder. Allows you to mass-prepare scripts for editing.\n3. Compile .txt-files to .gsc in the selected folder. Allows you to mass-rebuild .gsc based on edited .txt files.\n\nFor usage:\n1. Drag the .gsc scripts or .txt files (for compiling) into one folder.\n2. Press the 'Select Folder' button and choose that directory.\n3. Press 'DEFINE'. The folder path will appear in the field.\n4. Use the commands below to process the files in that folder.""")

    def CommandHelp(self):
         if (self.Language == "RUS"):
             mb.showwarning("Помощь по командам", """Увы, команд известно мало (но не их структур), а их аргументов ещё меньше. Что, впрочем, может измениться в будущем. Всякая известная команда в файле обозначена некоторой строкой.\n\nИтак, приведём базовые известные команды с аргументами:\n\n3 (0x03): JUMP_UNLESS.\nАргументы: [метка].\n5 (0x05): JUMP.\nАргументы: [метка].\n12 (0x0C): CALL_SCRIPT.\nАргументы: [номер скрипта без начальных нулей, ???]\n13 (0x0D): PAUSE.\nАргументы: [время в секундах].\n14 (0x0E): CHOICE.\nАргументы: [???, ???, ???, ???, ???, ???, ???, -1, -1, -1, -1, -1, ???, ???, ???].\n20 (0x14): IMAGE_GET.\nАргументы: [индекс картинки (из имени), ???].\n26 (0x1A): IMAGE_SET.\nАргументы: [].\n28 (0x1C): BLEND_IMG.\nАргументы: [???, тип1, тип2].\n30 (0x1E): IMAGE_DEF.\nАргументы: [???, ???, ???, ???, ???, ???].\n81 (0x51): MESSAGE.\nАргументы: [???, индекс гласа (из имени), ???, -1, -1, ???].\n82 (0x52): APPEND_MESSAGE.\nАргументы: [???, ???, ???, ???, -1, ???].\n83 (0x53): CLEAR_MESSAGE_WINDOW.\nАргументы: [???].\n121 (0x79): GET_DIRECTORY.\nАргументы: [???, -1].\n200 (0xC8): READ_SCENARIO.\nАргументы: [label, ???, ???, ???, ???, ???, ???, ???, ???, ???, ???].\n255 (0xFF): SPRITE.\nАргументы: [режим, позиция, индекс картинки, ???, ???].\n13568 (0x3500): AND.\nАргументы: [???, ???, ???].\n18432 (0x4800): EQUALS.\nАргументы: [???, ???, ???].\n21504 (0x5400): GREATER_EQUALS.\nАргументы: [???, ???, ???].\n43520 (0xAA00): ADD.\nАргументы: [???, ???, ???].\n61696 (0xF100): ASSIGN.\nАргументы: [???, ???].""")
         else:
             mb.showwarning("Command help", """Unfortunately, the number of known commands aren't big (but not of the structures). It may change it the future. All known commands are defined in decomilated file as a string.\n\nWell, let's show you a basic known commands with the arguments:\n\n3 (0x03): JUMP_UNLESS.\nArguments: [label]\n5 (0x05): JUMP.\nArguments: [label].\n12 (0x0C): CALL_SCRIPT.\nArguments: [script number, ???]0\n13 (0x0D): PAUSE.\nArguments: [time in seconds].\n14 (0x0E): CHOICE.\nArguments: [???, ???, ???, ???, ???, ???, ???, -1, -1, -1, -1, -1, ???, ???, ???].\n20 (0x14): IMAGE_GET.\nArguments: [image index (from the name), ???].\n26 (0x1A): IMAGE_SET.\nArguments: [].\n28 (0x1C): BLEND_IMG.\nArguments: [???, type1, type2].\n30 (0x1E): IMAGE_DEF.\nArguments: [???, ???, ???, ???, ???, ???].\n81 (0x51): MESSAGE.\nArguments: [???, voice index (from the name), ???, -1, -1, ???].\n82 (0x52): APPEND_MESSAGE.\nArguments: [???, ???, ???, ???, -1, ???].\n\n83 (0x53): CLEAR_MESSAGE_WINDOW.\nArguments: [???].121 (0x79): GET_DIRECTORY.\nArguments: [???, -1].\n200 (0xC8): READ_SCENARIO.\nArguments: [метка, ???, ???, ???, ???, ???, ???, ???, ???, ???, ???].\n255 (0xFF): SPRITE.\nArguments: [mode, position, image index, ???, ???].\n13568 (0x3500): AND.\nArguments: [???, ???, ???].\n18432 (0x4800): EQUALS.\nArguments: [???, ???, ???].\n21504 (0x5400): GREATER_EQUALS.\nArguments: [???, ???, ???].\n43520 (0xAA00): ADD.\nArguments: [???, ???, ???].\n61696 (0xF100): ASSIGN.\nArguments: [???, ???].""")

    def SyntaxHelp(self):
         if (self.Language == "RUS"):
             mb.showwarning("Помощь по синтаксису", """Для тех, кто скрипты именно редактировать жаждет, сие крайне важно знать. Синтаксис в целом прост, но имеет ряд особенностей.\n\n|"$" в начале строки обозначает однострочный комментарий.\n"#" в начале строки есть определение команды.\n\n"[..., ..., ...]" есть форма описания аргументов функции (разделяются запятой) и следует сразу после определения команды.\n\n"@" есть метка, на кою ссылаются некоторые команды.\n\nАргумент "-1" значит, что он связан с индексом следующей строки.\n\n">" обозначает строк начало.\nПосле сего идёт либо показатель изначального индекса строки, либо -1. -1 значит, что строка связанная. Связанные строки всегда следуют после задачи связанных аргументов.\nВАЖНО: ИНДЕКСЫ ПОСЛЕ ">" ОТОБРАЖАЮТ ЛИШЬ ИЗНАЧАЛЬНЫЕ ИНДЕКСЫ! ПРИ КОМПИЛЯЦИИ ИНДЕКС СТРОКИ БЕРЁТСЯ ЛИШЬ ИЗ НОМЕРА ">" В СКРИПТЕ!\nВАЖНО: НЕ ВСЕ СВЯЗНАННЫЕ ИНДЕКСЫ БЫЛИ НАЙДЕНЫ!""")
         else:
             mb.showwarning("Syntax help", """For those who desire for scripts to edit it's very important. The syntax is rather simple, but it have some specific moments.\n\n"$" is the string's beginning is for one-string comment.\n\n"#" in the string's beginning is for defination of command.\n\n"[..., ..., ...]" is for function argument's splitted with "," form. It goes strictly on the next line after the command defination.\n\n"@" is a label, to which some arguments are connecting.\n\nA "-1" argument means it connected with next string index.\n\n">" is for string beginning.\nAfter its goes mark of primar index of string or -1. If it's -1, the string is connected. Connected strings always goes after the defination of connected arguments.\nDO NOTE: INDEXES AFTER ">" SHOWS ONLY PRIMAR INDEXES! THEN COMPILE PROGRAM TAKE A STRING INDEX ONLY FROM THE NUMBER OF ">" IN SCRIPT!\nDO NOTE: NOT AN ALL OF CONNECTED INDEXES WAS FOUND!""")

# Create and run the GUI
# Note: This script requires a graphical environment (DISPLAY) to run the Tkinter GUI.
# If you are running this in a headless environment, you will get the _tkinter.TclError.
# To run this script, you need to have a display server active or use a virtual framebuffer
# like Xvfb if running on a server.
CurrentSession = GUI()
CurrentSession.root.mainloop()
