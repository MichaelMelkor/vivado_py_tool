import os
import re
import chardet

def judgeEmptyLine(FileLine = ''):
    if type(FileLine) != str:
        print('Error: "' + FileLine + '" is not a string')
        return False
    for i in FileLine:
        if i == '\t' or i == '\n' or i == ' ' or i == '\v' or i == '\f' or i == '\r' or i == '':
            continue
        else:
            return False
    return True

def judgeTotalCommentLine(LineCommentsChar = '//', BlockCommentsBeginChar = '/*', BlockCommentsEndChar = '*/', FileLine = ''):
    LineCommLoc = FileLine.find(LineCommentsChar)
    if BlockCommentsBeginChar == '':
        BlockCommFirstBeginLoc = -1
    else:
        BlockCommFirstBeginLoc = FileLine.find(BlockCommentsBeginChar)
    if LineCommLoc == -1 and BlockCommFirstBeginLoc == -1:
        return False
    elif judgeEmptyLine(FileLine[0:LineCommLoc]):
        return True
    elif not judgeEmptyLine(FileLine[0:BlockCommFirstBeginLoc]):
        return False
    else:
        BlockCommBeginLoc = BlockCommFirstBeginLoc
        BlockCommEndLoc = 0
        LineCommLoc = 0
        while True:
            BlockCommEndLoc   = FileLine.find(BlockCommentsEndChar, BlockCommBeginLoc+1)
            if BlockCommEndLoc != -1:
                BlockCommBeginLoc = FileLine.find(BlockCommentsBeginChar, BlockCommEndLoc+2)
            else:
                BlockCommBeginLoc = -1
            LineCommLoc   = FileLine.find(LineCommentsChar, BlockCommBeginLoc+1)
            if BlockCommEndLoc == -1:
                return True
            elif BlockCommBeginLoc == -1:
                if LineCommLoc > BlockCommEndLoc:
                    if judgeEmptyLine(FileLine[BlockCommEndLoc+2:LineCommLoc]):
                        return True
                    else:
                        return False
                elif judgeEmptyLine(FileLine[BlockCommEndLoc+2:]):
                    return True
                else:
                    return False
            elif LineCommLoc == -1:
                if BlockCommBeginLoc <= BlockCommEndLoc:
                    print('Error: judgeTotalCommentLine -- BlockCommBeginLoc <= BlockCommEndLoc!')
                if not judgeEmptyLine(FileLine[BlockCommEndLoc+2:BlockCommBeginLoc]):
                    return False
            elif LineCommLoc < BlockCommBeginLoc:
                if judgeEmptyLine(FileLine[BlockCommEndLoc+2:LineCommLoc]):
                    return True
                else:
                    return False
            elif LineCommLoc > BlockCommBeginLoc:
                if not judgeEmptyLine(FileLine[BlockCommEndLoc+2:BlockCommBeginLoc]):
                    return False
        return False

def judgeBlockCommentLineBegin(LineCommentsChar = '//', BlockCommentsBeginChar = '/*', BlockCommentsEndChar = '*/', FileLine = ''):
    BlockCommBeginLoc = -1
    BlockCommEndLoc = -1
    LineCommLoc = -1
    if BlockCommentsBeginChar == '':
        BlockCommBeginLoc = -1
    else:
        BlockCommBeginLoc = FileLine.find(BlockCommentsBeginChar)
    LineCommLoc = FileLine.find(LineCommentsChar)
    if LineCommLoc < BlockCommBeginLoc and LineCommLoc != -1:
        return False
    while True:
        BeginLocTmp = FileLine.find(BlockCommentsBeginChar, BlockCommBeginLoc+1)
        if BeginLocTmp != -1:
            BlockCommBeginLoc = BeginLocTmp
        else:
            break
    while True:
        EndLocTmp = FileLine.find(BlockCommentsEndChar, BlockCommEndLoc+1)
        if EndLocTmp != -1:
            BlockCommEndLoc = EndLocTmp
        else:
            break

    if BlockCommBeginLoc == -1:
        return False
    elif BlockCommBeginLoc <= BlockCommEndLoc:
        return False
    else:
        return True

def judgeBlockCommentLineEnd(BlockCommentsEndChar = '*/', FileLine = ''):
    if BlockCommentsEndChar == '':
        BlockCommEndLoc = -1
    else:
        BlockCommEndLoc = FileLine.find(BlockCommentsEndChar)
    if BlockCommEndLoc == -1:
        return False
    else:
        return True


class VerilogFile():
    def __init__(self, FilePath):
        self.Path = ''
        self.InitSuccess = True
        self.EmptyLinesNum = 0
        self.CodeLinesNum = 0
        self.BlockCommentsLinesNum = 0
        self.LineCommentsLinesNum = 0
        self.TotalLinesNum = 0
        self.LineCommentsChar = '//'
        self.BlockCommentsBeginChar = '/*'
        self.BlockCommentsEndChar = '*/'
        self.checkFile(FilePath)

    def checkFile(self, FilePath):
        if os.path.isfile(FilePath) == False:
            print('Error: The "' + FilePath + '" is not exist!')
            self.Path = ''
            self.InitSuccess = False
            return False
        FileSuffix = os.path.splitext(FilePath)[1]
        # print('$test--FileSuffix : ' + FileSuffix)
        if FileSuffix == '.v' or FileSuffix == '.sv' or FileSuffix == '.c' or FileSuffix == '.cpp':
            self.LineCommentsChar = '//'
            self.BlockCommentsBeginChar = '/*'
            self.BlockCommentsEndChar = '*/'
        elif FileSuffix == '.vhd':
            self.LineCommentsChar = '--'
            self.BlockCommentsBeginChar = ''
            self.BlockCommentsEndChar = ''
        else:
            print('Error: The "' + FilePath + '" can not be identified!')
            self.Path = ''
            self.InitSuccess = False
            return False
        self.Path = FilePath
        self.InitSuccess = True
        return True

    def countLinesNum(self):
        if self.InitSuccess == False:
            print('Error: Init failed! Can not countLinesNum!')
            return False
        print('-- Begin to count ' + self.Path)
        VerilogFile = open(self.Path, 'rb')
        ChardetDetectInfo = chardet.detect(VerilogFile.read())
        VerilogFile.close()
        print('--', ChardetDetectInfo)
        FileEncoding = ''
        if ChardetDetectInfo['confidence'] > 0.5:
            FileEncoding = ChardetDetectInfo['encoding']
        else:
            FileEncoding = 'utf-8'
            try:
                VerilogFile = open(self.Path, 'r', encoding=FileEncoding)
                VerilogFile.read()
            except UnicodeDecodeError:
                FileEncoding = 'GBK'
            VerilogFile.close()
        if FileEncoding == 'GB2312' or FileEncoding == 'gb2312':
            print('-- Open this file with encoding : GBK')
            FileEncoding = 'GBK'
        else:
            print('-- Open this file with encoding : ' + FileEncoding)
        VerilogFile = open(self.Path, 'r', encoding = FileEncoding)
        BlockCommLinesNum = 0
        while True:
            FileLine = VerilogFile.readline()
            if not FileLine:
                break
            self.TotalLinesNum += 1
            if BlockCommLinesNum != 0:
                if judgeBlockCommentLineEnd(self.BlockCommentsEndChar, FileLine):
                    BlockCommLinesNum += 1
                    self.BlockCommentsLinesNum += BlockCommLinesNum
                    BlockCommLinesNum = 0
                    continue
                else:
                    BlockCommLinesNum += 1
                    continue
            elif judgeEmptyLine(FileLine):
                self.EmptyLinesNum += 1
            else:
                if judgeBlockCommentLineBegin(self.LineCommentsChar, self.BlockCommentsBeginChar, self.BlockCommentsEndChar, FileLine):
                    BlockCommLinesNum = 1
                else:
                    LineCommBeginLoc = FileLine.find(self.LineCommentsChar)
                    if self.BlockCommentsBeginChar == '':
                        BlockCommBeginLoc = -1
                    else:
                        BlockCommBeginLoc = FileLine.find(self.BlockCommentsBeginChar)
                    if LineCommBeginLoc != -1 and BlockCommBeginLoc != -1:
                        if LineCommBeginLoc < BlockCommBeginLoc:
                            self.LineCommentsLinesNum += 1
                        else:
                            self.BlockCommentsLinesNum += 1
                    elif FileLine.find(self.LineCommentsChar) != -1:
                        self.LineCommentsLinesNum += 1
                    elif self.BlockCommentsBeginChar != '' and FileLine.find(self.BlockCommentsBeginChar) != -1:
                        self.BlockCommentsLinesNum += 1
                if not judgeTotalCommentLine(self.LineCommentsChar, self.BlockCommentsBeginChar, self.BlockCommentsEndChar, FileLine):
                    self.CodeLinesNum += 1
        print('-- ' + self.Path + ' finish')
        print('------------------------------------------------------------------')
        VerilogFile.close()
        return True

# if __name__ == "__main__":
#     verilog_file = VerilogFile('sat_54_gaogui_FPGA1_bus_top.v')
#     verilog_file.countLinesNum()
#     print('BlockCommLines: ', verilog_file.BlockCommentsLinesNum)
#     print('LineCommLines: ', verilog_file.LineCommentsLinesNum)
#     print('EmptyLines: ', verilog_file.EmptyLinesNum)
#     print('CodeLines: ', verilog_file.CodeLinesNum)
#     print('TotalLines: ', verilog_file.TotalLinesNum)
