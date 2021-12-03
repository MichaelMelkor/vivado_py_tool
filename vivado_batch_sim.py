import sys
import os
import shutil
import chardet
from xml.dom.minidom import parse
from calcu_codefile_lines import VerilogFile

# 工程目录
GLOBAL_PROJ_DIR = '../'
# Linux系统Xilinx相关软件安装目录（Xilinx文件夹所在目录，需自行设置）
GLOBAL_LINUX_XILINX_INSTALL_DIR = '/opt/joat/'
# Windows系统Xilinx相关软件安装目录（Xilinx文件夹所在目录，需自行设置）
GLOBAL_WIN_XILINX_INSTALL_DIR = 'D:/'

# 备用Vivado安装目录路径：用于解决不同版本的Vivado软件未安装在同一分区内的情况 需自行设置
# 含义为Vivado文件夹所在目录路径
GLOBAL_VIVADO_INSTALL_DIR_SPARE_1 = 'D:/Xilinx/'
GLOBAL_VIVADO_INSTALL_DIR_SPARE_2 = 'C:/Xilinx/'

# 获取并返回对应文件或目录路径名列表
def getProjFilePathList(Path = './', FilePartName = '.xpr'):
    # 判断传入参数是否为字符串
    if type(Path) != str or type(FilePartName) != str:
        print('Error: The type of parameter is wrong! Please ensure each input parameter is a string!')
        return []
    # 判断传入的路径参数是否存在
    if os.path.isdir(Path) == False:
        print('Error: The path ' + Path + ' does not exist!')
        return []
    # 查找目标文件，并将查找结果路径记录到FilePathList的列表中
    FilePathList = []
    for FileName in os.listdir(Path):
        if FileName.find(FilePartName) != -1:
            FilePathList.append(Path + FileName)
    # 判断是否查找到对应文件或目录路径
    if len(FilePathList) == 0:
        print('Error: Can not find any file or dir whose name including "' + FilePartName + '" in "' + Path + '"')
    return FilePathList

# 获取并返回对应文件或目录路径名列表中的第一个路径
def getProjFilePath(Path = './', FilePartName = '.xpr'):
    # 获取并返回对应文件或目录路径名列表
    FilePathList = getProjFilePathList(Path, FilePartName)
    # 返回列表中第一个元素
    if len(FilePathList) == 0:
        return ''
    else:
        return FilePathList[0] 

# 将文件FilePath内字符串OriginLine全部替换为UpdateLine
def replaceFileStr(FilePath, OriginLine, UpdateLine):
    # 判断文件路径是否存在
    if os.path.isfile(FilePath) == False:
        print('Error: ' + FilePath + ' is not exist!')
        return 0
    # 读取旧文件中全部文本内容
    File = open(FilePath, 'r')
    FileAllLines = File.readlines()
    File.close()
    File = open(FilePath, 'w')
    # 替换对应字符串并覆写文件
    for eachline in FileAllLines:
        if eachline.find(OriginLine) != -1:
            eachline = eachline.replace(OriginLine, UpdateLine)
        # print(eachline)
        File.writelines(eachline)
    File.close()
    return 0

# 将旧文件OriginFilePath中的全部内容替换成新文件UpdateFilePath中的内容
def replaceFileContent(OriginFilePath, UpdateFilePath):
    # 判断存有替换内容的新文件是否存在
    if os.path.isfile(UpdateFilePath) == False:
        print('Error: ' + UpdateFilePath + ' is not exist!')
        return 0
    # 打开新文件并读取全部内容
    File = open(UpdateFilePath, 'r')
    FileAllLines = File.readlines()
    File.close()
    # 在指定路径新建或覆写对应文件
    File = open(OriginFilePath, 'w')
    File.writelines(FileAllLines)
    File.close()
    return 0

# 递归建立目录
def recursiveMakeDir(DirPath):
    SubDirPath = ''
    if os.path.isdir(DirPath):
        return True
    else:
        if DirPath[len(DirPath) - 1] == '/':
            SubDirPath = DirPath[:len(DirPath)-1]
            # print(SubDirPath)
        else:
            SubDirPath = DirPath
            # print(SubDirPath)
        SplitResult = os.path.split(SubDirPath)
        # print(SplitResult)
        while True:
            if SplitResult[0] == '' or SplitResult[1] == '':
                os.mkdir(DirPath)
                return True
            elif os.path.isdir(SplitResult[0]):
                os.mkdir(DirPath)
                return True
            else:
                recursiveMakeDir(SplitResult[0])

# 直接复制旧文件到新文件目录下
def copyFile(OriginFilePath, NewFilePath):
    if os.path.isfile(OriginFilePath) == False:
        print('Error: ' + OriginFilePath + ' is not exist!')
        return False
    NewFileDirPath = os.path.split(NewFilePath)[0]
    if NewFileDirPath == '':
        NewFileDirPath = './'
    if os.path.isdir(NewFileDirPath) == False:
        recursiveMakeDir(NewFileDirPath)
    shutil.copyfile(OriginFilePath, NewFilePath)
    return True

# 提取文本文件内容，转换为utf-8编码后，写入到新文件
def convertToUTF_8InNewFile(OriginFilePath, NewFilePath):
    if os.path.isfile(OriginFilePath) == False:
        print('Error: ' + OriginFilePath + ' is not exist!')
        return False
    NewFileDirPath = os.path.split(NewFilePath)[0]
    if NewFileDirPath == '':
        NewFileDirPath = './'
    if os.path.isdir(NewFileDirPath) == False:
        recursiveMakeDir(NewFileDirPath)
    OriginFile = open(OriginFilePath, 'rb')
    ChardetDetectInfo = chardet.detect(OriginFile.read())
    OriginFile.close()
    FileEncoding = ''
    if ChardetDetectInfo['confidence'] > 0.5:
        FileEncoding = ChardetDetectInfo['encoding']
    else:
        FileEncoding = 'utf-8'
        try:
            OriginFile = open(OriginFilePath, 'r', encoding=FileEncoding)
            OriginFile.read()
        except UnicodeDecodeError:
            FileEncoding = 'GBK'
        OriginFile.close()
    if FileEncoding == 'GB2312' or FileEncoding == 'gb2312':
        FileEncoding = 'GBK'
    OriginFile = open(OriginFilePath, 'r', encoding = FileEncoding)
    NewFile = open(NewFilePath, 'w', encoding='utf-8')
    OriginFileData = OriginFile.readline()
    while OriginFileData != '':
        NewFile.write(OriginFileData)
        OriginFileData = OriginFile.readline()
    OriginFile.close()
    NewFile.close()
    return True

# 定义工程类
class VivadoProj():
    def __init__(self, 
                proj_dir                   = GLOBAL_PROJ_DIR, 
                linux_xilinx_install_dir   = GLOBAL_LINUX_XILINX_INSTALL_DIR, 
                win_xilinx_install_dir     = GLOBAL_WIN_XILINX_INSTALL_DIR, 
                vivado_install_dir_spare_1 = GLOBAL_VIVADO_INSTALL_DIR_SPARE_1, 
                vivado_install_dir_spare_2 = GLOBAL_VIVADO_INSTALL_DIR_SPARE_2, 
                sim_tcl_file_name          = 'sim.tcl', 
                synth_tcl_file_name        = 'synth.tcl', 
                impl_tcl_file_name         = 'impl.tcl'):
        # 工程目录
        self.PROJ_DIR = proj_dir
        # Linux系统Xilinx相关软件安装目录（Xilinx文件夹所在目录，需自行设置）
        self.LINUX_XILINX_INSTALL_DIR = linux_xilinx_install_dir
        # Windows系统Xilinx相关软件安装目录（Xilinx文件夹所在目录，需自行设置）
        self.WIN_XILINX_INSTALL_DIR = win_xilinx_install_dir
        # 备用Xilinx相关软件安装目录（需自行设置）
        self.VIVADO_INSTALL_DIR_SPARE_1 = vivado_install_dir_spare_1 + 'Vivado/'
        self.VIVADO_INSTALL_DIR_SPARE_2 = vivado_install_dir_spare_2 + 'Vivado/'
        # 本程序中使用到的相关tcl脚本文件名称及路径
        # 本程序中使用到的相关tcl脚本文件名称及路径
        self.SIM_TCL_FILE_NAME   = sim_tcl_file_name
        self.SYNTH_TCL_FILE_NAME = synth_tcl_file_name
        self.IMPL_TCL_FILE_NAME  = impl_tcl_file_name
        # 当前工程xpr文件路径
        self.XPR_FILE_PATH = ''
        # 当前工程版本
        self.PROJ_VERSION = ''
        # 当前系统类型
        self.SystemType = ''
        # 系统命令符-执行
        self.EXE_CMD = ''
        # 系统Vivado软件所在目录
        self.VIVADO_DIR = ''
        # Vivado软件的settings64文件名
        self.SETTING_BATCH_FILE = ''
        # 系统脚本文件后缀
        self.BATCH_FILE_SUFFIX = ''
        # 系统命令符-命令连接符
        self.CMD_CONCAT_OPERATOR = ''

        # 解析xpr文件所得的Configuration节点
        self.Configuration = ''
        # 解析xpr文件所得的FileSets节点
        self.FileSets = ''
        # 解析xpr文件所得的Simulators节点
        self.Simulators = ''
        # 解析xpr文件所得的Runs节点
        self.Runs = ''
        # 解析xpr文件所得的Configuration节点中的Option关键词字典
        self.ConfigurationOptionDict = {'Part':'', 'CompiledLibDir':'', 'TargetSimulator':'', 'ActiveSimSet':'', 'DefaultLib':''}
        # 创建并初始化当前待Synthesis的参数关键词字典
        self.RunSynthActiveDict = {'Id':'', 'SrcSet':'', 'ConstrsSet':'', 'Dir':''}
        # 创建并初始化当前待Implement的参数关键词字典
        self.RunImplActiveDict = {'Id':'', 'ConstrsSet':'', 'SynthRun':'', 'Dir':''}
        # 创建并初始化当前Synthesis的SrcSet的参数关键词字典
        self.SynthSrcSetConfigDict = {'DesignMode':'', 'TopModule':''}
        # 初始化当前待Synthesis的Active对象Id
        # self.SynthActiveId = ''
        # 初始化当前待Implement的Active对象Id
        # self.ImplActiveId = ''
        # 第一次仿真标志位（第一次仿真时需要重新生成脚本再执行）
        # self.FirstSimulateFlag = True
        # 当前工程仿真的相关目录
        self.SimDir = ''
        self.ActiveSimSetDir = ''
        self.ActiveSimSetBehaveDir = ''
        self.ActiveSimSetBehaveSimDir = ''
        # 生成的Compile脚本文件名
        self.CompileScriptFile = ''
        # 生成的Elaborate脚本文件名
        self.ElaborateScriptFile = ''
        # 生成的Simulate脚本文件名
        self.SimulateScriptFile = ''
        # 人机交互输入的参数
        self.InputNum = ''
        # 初始化成功标志
        self.InitSuccess = True
        # 系统内存在对应版本的Vivado软件
        self.VivadoExist = False

        # 待初始化的相关命令
        # 命令-调用Vivado安装目录中的settings文件，以便使用命令行调用Vivado
        self.SourceSettingsFileCmd = ''

        # 初始化部分参数
        # 初始化xpr文件路径
        self.InitSuccess = self.getXprFilePath()
        # 初始化获取xpr文件工程版本
        self.InitSuccess = self.getProjVersion()
        # 初始化系统基础命令片段
        self.InitSuccess = self.getSystemPartCMD()
        # 解析xml格式的xpr文件，根据文件内容初始化相关参数
        self.InitSuccess = self.parseXprFile()
        # 初始化获取仿真目录路径
        self.InitSuccess = self.getSimDirs()
        # 初始化相关基础命令字符串
        self.InitSuccess = self.getBasicCMD()

    # 初始化获取xpr文件路径
    def getXprFilePath(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to get xpr file\'s path!')
            return False
        # 获取工程目录下名称中带有.xpr的文件路径的字符串列表
        XprFilePathList = getProjFilePathList(self.PROJ_DIR, '.xpr')
        # 当列表非空时，将列表中第一个字符串元素默认为当前工程的xpr文件
        if len(XprFilePathList) == 0:
            self.XPR_FILE_PATH = ''
            return False
        elif len(XprFilePathList) == 1:
            self.XPR_FILE_PATH = XprFilePathList[0]
            return True
        else:
            print('We find more than one XPR file in project path : "' + self.PROJ_DIR + '"')
            print('---------------------------------------------------------')
            XprFileSelectNum = 0
            for XprFilePath in XprFilePathList:
                print('-- ' + str(XprFileSelectNum) + ' : ' + XprFilePath)
                XprFileSelectNum += 1
            print('---------------------------------------------------------')
            while XprFileSelectNum >= len(XprFilePathList):
                XprFileSelectNum = input('Please select one as this project\'s XPR file :')
                try:
                    XprFileSelectNum = int(XprFileSelectNum)
                except ValueError:
                    XprFileSelectNum = len(XprFilePathList)
                if XprFileSelectNum >= len(XprFilePathList):
                    print('Error: Invalid num!')
            self.XPR_FILE_PATH = XprFilePathList[0]
            return True

    # 初始化获取当前工程版本
    def getProjVersion(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to get current proj\'s version!')
            return False
        # 初始化-行字符串、版本号字符串、版本号字符串起始位置数值变量
        VivadoProjVerLine = ''
        VivadoProjVer = ''
        VivadoProjVerLoc = -1
        # 打开并读取工程的xpr文件
        if self.XPR_FILE_PATH == '':
            print('Can not find the xpr file!')
            self.PROJ_VERSION = ''
            return False
        XprFile = open(self.XPR_FILE_PATH, "r")
        for line_text in XprFile.readlines():
            # 定位版本号字符串所在行及位置，并获取行内容
            if line_text.find('Product Version: Vivado v') != -1:
                VivadoProjVerLoc = line_text.find('Product Version: Vivado v') + len('Product Version: Vivado v')
                VivadoProjVerLine = line_text
                break
        XprFile.close()
        if VivadoProjVerLoc == -1:
            VivadoProjVer = ''
            print('Error: Can not find the version of proj, please ensure the xpr file is ok!')
            self.PROJ_VERSION = ''
            return False
        # 判断查找到的版本号字符串是否合法
        for CharVer in VivadoProjVerLine[VivadoProjVerLoc :]:
            if CharVer == ' ' and VivadoProjVer != '':
                break
            elif CharVer >= '0' and CharVer <= '9':
                VivadoProjVer = VivadoProjVer + CharVer
            elif CharVer == '.':
                VivadoProjVer = VivadoProjVer + CharVer
            else:
                VivadoProjVer = ''
                print('Error: Can not identify the version of this xpr file!')
                return False
        self.PROJ_VERSION = VivadoProjVer
        return True
 
    # 根据系统类型（Linux，Windows）产生对应的批处理命令片段和相关路径片段
    def getSystemPartCMD(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to get current os command!')
            return False
        if self.LINUX_XILINX_INSTALL_DIR == '' or self.WIN_XILINX_INSTALL_DIR == '':
            print('Error: The software\'s install directory is wrong!')
            return False
        exe_cmd = ''
        vivado_dir = ''
        setting_batch_file = ''
        batch_file_suffix = ''
        cmd_concat_operator = '' # 命令链接运算符
        # 获取当前系统类型
        if sys.platform.find('linux') != -1:
            self.SystemType = 'linux'
        elif sys.platform.find('win') != -1:
            self.SystemType = 'win'
        else:
            self.SystemType = 'win'

        if self.SystemType == 'linux': # 当前系统为linux
            exe_cmd = 'source '
            vivado_dir = self.LINUX_XILINX_INSTALL_DIR + 'Xilinx/Vivado/'
            setting_batch_file = 'settings64.sh'
            batch_file_suffix = '.sh'
            cmd_concat_operator = ' ' + '&&' + ' ' # 命令链接运算符，linux下为 "&&" 
        elif self.SystemType == 'win': # 当前系统为windows
            exe_cmd = 'call '
            vivado_dir = self.WIN_XILINX_INSTALL_DIR + 'Xilinx/Vivado/'
            setting_batch_file = 'settings64.bat'
            batch_file_suffix = '.bat'
            cmd_concat_operator = ' ' + '&&' + ' ' # 命令链接运算符，windows下为 "&&" 
        else: # 其他系统则不支持
            print('Sorry but current os is not supported!')
            return False
        # 系统命令符-执行
        self.EXE_CMD = exe_cmd
        # 系统Vivado软件所在目录
        self.VIVADO_DIR = vivado_dir
        # Vivado软件的settings64文件名
        self.SETTING_BATCH_FILE = setting_batch_file
        # 系统脚本文件后缀
        self.BATCH_FILE_SUFFIX = batch_file_suffix
        # 系统命令符-命令连接符
        self.CMD_CONCAT_OPERATOR = cmd_concat_operator
        return True

    #检测当前系统Xilinx软件的安装目录下是否存在settings64文件，若无，产生一个到当前目录下
    #并使用该settings64文件生成source命令
    def makeSourceSettingsFileCmd(self):
        FileDir = self.VIVADO_DIR + self.PROJ_VERSION
        if os.path.isfile(FileDir + '/' + self.SETTING_BATCH_FILE):
            self.SourceSettingsFileCmd = self.EXE_CMD + FileDir + '/' + self.SETTING_BATCH_FILE 
            return True
        else:
            Settings64File = open(self.SETTING_BATCH_FILE, "w")
            if self.SystemType == 'win':
                Settings64File.write('@echo off\n')
                Settings64File.write('SET PATH=' + FileDir.replace('/', '\\') + '\\' + 'bin;' +  FileDir.replace('/', '\\') + '\\' + 'lib\\win64.o;%PATH%\n')
                Settings64File.write('SET XILINX_VIVADO=' + FileDir.replace('/', '\\') + '\n')
            elif self.SystemType == 'linux':
                Settings64File.write('export XILINX_VIVADO=' + FileDir + '\n')
                Settings64File.write('if [ -n \"${PATH}\" ]; then\n')
                Settings64File.write('  export PATH=' + FileDir + '/bin:$PATH\n')
                Settings64File.write('else\n')
                Settings64File.write('  export PATH=' + FileDir + '/bin\n')
                Settings64File.write('fi\n')
            Settings64File.close()
            self.SourceSettingsFileCmd = self.EXE_CMD + './' + self.SETTING_BATCH_FILE 
            return True


    # 识别对应版本Vivado软件所在目录，并产生基础的批处理命令
    def getBasicCMD(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to get current os command!')
            return False
        self.SourceSettingsFileCmd = ''
        SettingsFileDir = self.VIVADO_DIR + self.PROJ_VERSION + '/'
        # 判断当前系统Xilinx安装目录下是否存在对应版本的Vivado
        if not os.path.isdir(SettingsFileDir):
            print('There is no Vivado' + self.PROJ_VERSION + ' in ' + self.VIVADO_DIR + ' of this os!')
            print('Checking ' + self.VIVADO_INSTALL_DIR_SPARE_1 + ' ...')
            SettingsFileDir = self.VIVADO_INSTALL_DIR_SPARE_1 + self.PROJ_VERSION + '/'
            self.VIVADO_DIR = self.VIVADO_INSTALL_DIR_SPARE_1
        if not os.path.isdir(SettingsFileDir):
            print('There is no Vivado' + self.PROJ_VERSION + ' in ' + self.VIVADO_INSTALL_DIR_SPARE_1 + ' of this os!')
            print('Checking ' + self.VIVADO_INSTALL_DIR_SPARE_2 + ' ...')
            SettingsFileDir = self.VIVADO_INSTALL_DIR_SPARE_2 + self.PROJ_VERSION + '/'
            self.VIVADO_DIR = self.VIVADO_INSTALL_DIR_SPARE_2
        if not os.path.isdir(SettingsFileDir):
            print('There is no Vivado' + self.PROJ_VERSION + ' in ' + self.VIVADO_INSTALL_DIR_SPARE_2 + ' of this os!')
            self.VivadoExist = False
            return True
        else: # 若存在，组合命令，并执行
            print('Find Vivado' + self.PROJ_VERSION + ' in ' + self.VIVADO_DIR)
            ##self.SourceSettingsFileCmd = self.EXE_CMD + SettingsFileDir + self.SETTING_BATCH_FILE 
            self.makeSourceSettingsFileCmd()
            self.VivadoExist = True
            return True

    # 解析xpr文件并记录参数
    def parseXprFile(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to parse the xpr file!')
            return False
        if self.XPR_FILE_PATH == '':
            return False
        else:
            # 解析xpr工程文件
            doc = parse(self.XPR_FILE_PATH)
            root = doc.documentElement
            # 记录解析出的四个节点
            self.Configuration = root.getElementsByTagName('Configuration')[0]
            self.FileSets = root.getElementsByTagName('FileSets')[0]
            self.Simulators = root.getElementsByTagName('Simulators')[0]
            self.Runs = root.getElementsByTagName('Runs')[0]
            # 查找xpr工程文件中Configuration节点中的关键词并记录到关键词字典中
            Options = self.Configuration.getElementsByTagName('Option')
            print('-----------------------Configuration Parameter-------------------------')
            for Option in Options:
                if Option.hasAttribute('Name') and Option.hasAttribute('Val'):
                    for keyword in self.ConfigurationOptionDict:
                        if Option.getAttribute('Name') == keyword:
                            self.ConfigurationOptionDict[keyword] = Option.getAttribute('Val')
                            print('Config - Find the ' + keyword + (20-len(keyword))*' ' + ' : ' + self.ConfigurationOptionDict[keyword])
            print('-----------------------------------------------------------------------')
            if self.ConfigurationOptionDict['ActiveSimSet'] == '':
                print('Warning: 当前工程未设定ActiveSimSet！')
            if self.ConfigurationOptionDict['TargetSimulator'] == '':
                print('Warning: 当前工程未设定第三方仿真器！')
            # 查找当前Active的Synthesis和Implement的关键词
            for Run in self.Runs.getElementsByTagName('Run'):
                if Run.hasAttribute('State') and Run.hasAttribute('Description'):
                    if Run.getAttribute('State') == 'current':
                        if Run.getAttribute('Description').find('Synthesis') != -1:
                            # self.SynthActiveId = Run.getAttribute('Id')
                            # print('Find the SynthActiveId: ' + self.SynthActiveId)
                            print('-------------------------Synthesis Parameter---------------------------')
                            for i in self.RunSynthActiveDict:
                                if Run.hasAttribute(i):
                                    self.RunSynthActiveDict[i] = Run.getAttribute(i)
                                    print('Synth - Find the ' + i + (20-len(i))*' ' +': ' + self.RunSynthActiveDict[i])
                                else:
                                    print('Synth - Can not find the ' + i)
                            print('-----------------------------------------------------------------------')
                        elif Run.getAttribute('Description').find('Implement') != -1:
                            # self.ImplActiveId = Run.getAttribute('Id')
                            # print('Find the ImplActiveId: ' + self.ImplActiveId)
                            print('-------------------------Implement Parameter---------------------------')
                            for i in self.RunImplActiveDict:
                                if Run.hasAttribute(i):
                                    self.RunImplActiveDict[i] = Run.getAttribute(i)
                                    print('Impl  - Find the ' + i + (20-len(i))*' ' + ': ' + self.RunImplActiveDict[i])
                                else:
                                    print('Impl  - Can not find the ' + i)
                            print('-----------------------------------------------------------------------')
            # 生成并输出综合和实现的tcl命令到tcl脚本中
            TclResFile = open(self.SYNTH_TCL_FILE_NAME,'w')
            TclResFile.writelines('reset_run ' + self.RunSynthActiveDict['Id'] + '\n')
            TclResFile.writelines('launch_runs ' + self.RunSynthActiveDict['Id'] + '\n')
            TclResFile.close()
            TclResFile = open(self.IMPL_TCL_FILE_NAME,'w')
            TclResFile.writelines('launch_runs ' + self.RunImplActiveDict['Id'] + ' -to_step write_bitstream' + '\n')
            TclResFile.close()
            print('-------------------------SrcSet Configuration--------------------------')
            for FileSet in self.FileSets.getElementsByTagName('FileSet'):
                if FileSet.getAttribute('Name') == self.RunSynthActiveDict['SrcSet']:
                    FileSetConfig = FileSet.getElementsByTagName('Config')[0]
                    for Option in FileSetConfig.getElementsByTagName('Option'):
                        for i in self.SynthSrcSetConfigDict:
                            if Option.getAttribute('Name') == i and Option.hasAttribute('Val'):
                                self.SynthSrcSetConfigDict[i] = Option.getAttribute('Val')
                                print('SrcSet - Find the ' + i + (20-len(i))*' ' + ': ' + self.SynthSrcSetConfigDict[i])
            print('-----------------------------------------------------------------------')
            return True

    # 初始化仿真目录
    def getSimDirs(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to get the simulation\'s directory!')
            return False
        # 查找当前工程仿真目录
        self.SimDir = getProjFilePath(self.PROJ_DIR, '.sim') + '/'
        # print(SimDir)
        self.ActiveSimSetDir = self.SimDir + self.ConfigurationOptionDict['ActiveSimSet'] + '/'
        self.ActiveSimSetBehaveDir = self.ActiveSimSetDir + 'behav/'
        if self.PROJ_VERSION == '2017.2':
            self.ActiveSimSetBehaveSimDir = self.ActiveSimSetBehaveDir
        elif self.PROJ_VERSION == '2018.2' or self.PROJ_VERSION == '2019.2':
            self.ActiveSimSetBehaveSimDir = self.ActiveSimSetBehaveDir + self.ConfigurationOptionDict['TargetSimulator'].lower() + '/'
        else:
            self.ActiveSimSetBehaveSimDir = self.ActiveSimSetBehaveDir
        # print(ActiveSimSetBehaveSimDir)
        if os.path.isdir(self.ActiveSimSetBehaveSimDir) == False:
            print('Error: The sim file path "' + self.ActiveSimSetBehaveSimDir + '" is not exist!')
            return False

    # 利用Vivado的Batch Mode执行对应脚本，实现生成仿真脚本、综合、实现等功能
    def sourceTclByBatchMode(self, TclFilePath):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to make the simulation scripts!')
            return False
        # 检测当前tcl脚本是否存在
        if os.path.isfile(TclFilePath) == False:
            print('Error: The file ' + TclFilePath + ' is not exist!')
            return False
        # 组合生成脚本命令字符串并执行
        VivadoBatchSimCmd = 'vivado -mode batch -source ' + TclFilePath +' -nojournal -nolog ' + self.XPR_FILE_PATH 
        # print(self.SourceSettingsFileCmd + self.CMD_CONCAT_OPERATOR + VivadoBatchSimCmd)
        os.system(self.SourceSettingsFileCmd + self.CMD_CONCAT_OPERATOR + VivadoBatchSimCmd)
        return True

    # 进行编译
    def startCompile(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to compile!')
            return False
        # 初始化编译脚本文件名
        self.CompileScriptFile = './compile' + self.BATCH_FILE_SUFFIX
        if os.path.isfile(self.ActiveSimSetBehaveSimDir + self.CompileScriptFile) == False:
            print('Error: The Compile Script File is not exist!')
            return False
        # 生成跳转到仿真目录的命令（脚本文件执行需要在其所在目录下，否则脚本中的相对路径命令无法执行）
        CdCmd = 'cd ' + self.ActiveSimSetBehaveSimDir 
        # print(CdCmd)
        # 组合编译命令字符串
        CompileCmd = self.EXE_CMD + self.CompileScriptFile 
        # print(CompileCmd)
        os.system(CdCmd + self.CMD_CONCAT_OPERATOR + CompileCmd)
        print('Compile success!')
        return True

    # 进行Elaborate
    def startElaborate(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to elaborate!')
            return False
        # 初始化Elaborate脚本文件名
        self.ElaborateScriptFile = './elaborate' + self.BATCH_FILE_SUFFIX
        if os.path.isfile(self.ActiveSimSetBehaveSimDir + self.ElaborateScriptFile) == False:
            print('Error: The Elaborate Script File is not exist!')
            return False
        # 生成跳转到仿真目录的命令（脚本文件执行需要在其所在目录下，否则脚本中的相对路径命令无法执行）
        CdCmd = 'cd ' + self.ActiveSimSetBehaveSimDir 
        # print(CdCmd)
        # 组合Elaborate命令字符串
        ElaborateCmd = self.EXE_CMD + self.ElaborateScriptFile 
        # print(ElaborateCmd)
        os.system(CdCmd + self.CMD_CONCAT_OPERATOR + ElaborateCmd)
        print('Elaborate success!')
        return True

    # 进行仿真
    def startSimulate(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to simulate!')
            return False
        # Vivado生成的脚本文件名
        self.SimulateScriptFile = './simulate' + self.BATCH_FILE_SUFFIX
        if os.path.isfile(self.ActiveSimSetBehaveSimDir + self.SimulateScriptFile) == False:
            print('Error: The Simulate Script File is not exist!')
            return False
        # 生成跳转到仿真目录的命令（脚本文件执行需要在其所在目录下，否则脚本中的相对路径命令无法执行）
        CdCmd = 'cd ' + self.ActiveSimSetBehaveSimDir 
        # print(CdCmd)
        # 组合仿真命令字符串
        SimulateCmd = self.EXE_CMD + self.SimulateScriptFile 
        # 获取编译、Elaborate、仿真需要的do文件的路径
        CompileDoFilePath = getProjFilePath(self.ActiveSimSetBehaveSimDir, 'compile.do')
        ElaborateDoFilePath = getProjFilePath(self.ActiveSimSetBehaveSimDir, 'elaborate.do')
        SimulateDoFilePath = getProjFilePath(self.ActiveSimSetBehaveSimDir, 'simulate.do')
        # 若在windows系统下，获取存有波形设置的do文件的路径，并对仿真脚本中部分内容进行替换
        WaveDoFilePath = ''
        if self.SystemType == 'win': # 当前系统为windows
            WaveDoFilePath = getProjFilePath(self.ActiveSimSetBehaveSimDir, 'wave.do')
            # print(WaveDoFilePath)
            replaceFileStr(self.ActiveSimSetBehaveSimDir + self.SimulateScriptFile, self.EXE_CMD + '%bin_path%/vsim  -c -do', self.EXE_CMD + '%bin_path%/vsim -do')
        elif self.SystemType == 'linux': # 当前系统为linux
            replaceFileStr(self.ActiveSimSetBehaveSimDir + self.SimulateScriptFile, 'simv $', 'simv -gui $')
            if os.path.isfile(self.ActiveSimSetBehaveSimDir + 'makefile') == False:
                replaceFileContent(self.ActiveSimSetBehaveSimDir + 'makefile', './sim_makefile')
        # 对仿真设置相关的do文件中的内容进行替换
        replaceFileStr(SimulateDoFilePath, 'run 1000ns', 'log -r ./*\nrun 100000ns')
        replaceFileStr(SimulateDoFilePath, 'view wave', ' ')
        replaceFileStr(SimulateDoFilePath, 'view structure', ' ')
        replaceFileStr(SimulateDoFilePath, 'view signals', ' ')
        replaceFileStr(SimulateDoFilePath, 'quit -force', ' ')
        replaceFileStr(SimulateDoFilePath, 'quit', '')
        # replaceFileStr(WaveDoFilePath, 'add wave *', 'add wave -noupdate -expand -group tb *')
        # 若在windows系统下，用本目录下的波形设置文件内容对Vivado自动生成的波形设置文件内容予以替换
        UpdateWaveDoFilePath = getProjFilePath('./', 'wave.do')
        if UpdateWaveDoFilePath != '' and WaveDoFilePath != '':
            replaceFileContent(WaveDoFilePath, UpdateWaveDoFilePath)

        # print(CdCmd + CMD_CONCAT_OPERATOR + SimulateCmd)
        os.system(CdCmd + self.CMD_CONCAT_OPERATOR + SimulateCmd)

    # 打印交互界面，并实现交互功能
    def startInteraction(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to start interaction!')
            return False
        self.InputNum = ''
        print('#######################################################################')
        print('1 ：退出')
        print('2 ：打开GUI工程')
        print('3 ：全流程仿真 - Compile Elaborate Simulate（可用于修改了代码之后重新仿真）')
        print('4 ：重新生成脚本，全流程仿真（用于添加了新的代码文件或IP核之后重新仿真）')
        print('5 ：单流程仿真 - Simulate（仅用于未做任何修改的仿真）')
        print('6 ：提取代码文件并转换为UTF-8编码 -> ./copy_code_files/')
        print('7 ：提取IP核xci文件 -> ./copy_ip_files/')
        print('8 ：进行综合 - Synthesis')
        print('9 ：进行实现 - Implement')
        print('10：生成EDF网表文件和对应的Verilog、VHDL源文件')
        print('11：重新解析工程xpr文件，并初始化参数')
        print('12：统计工程中Verilog和VHDL代码文件的行数 -> ./calcu_code_files_lines/')
        print('#######################################################################')
        self.InputNum = input('请输入：')
        return True

    # 打开工程的GUI界面
    def openGUIProj(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not open GUI!')
            return False
        # 组合打开GUI命令并执行
        VivadoOpenGUIProjCMD = 'vivado -nojournal -nolog ' + self.XPR_FILE_PATH + '\n'
        os.system(self.SourceSettingsFileCmd + self.CMD_CONCAT_OPERATOR + VivadoOpenGUIProjCMD)
        return True

    # 替换路径字符串中的工程路径常量
    def replacePathConst(self, PathStr):
        if PathStr.find('$PPRDIR/') != -1:
            PathStr = PathStr.replace('$PPRDIR/', self.PROJ_DIR)
        elif PathStr.find('$PSRCDIR/') != -1:
            PathStr = PathStr.replace('$PSRCDIR/', getProjFilePath(self.PROJ_DIR, '.src') + '/')
        elif PathStr.find('$PRUNDIR/') != -1:
            PathStr = PathStr.replace('$PRUNDIR/', getProjFilePath(self.PROJ_DIR, '.run') + '/')
        return PathStr

    # 解析全部代码文件路径，并记录到文件中
    def logAllCodeFilesPath(self, WrFilePath = './filelist.f'):
        WrFile = open(WrFilePath, 'w', encoding='utf-8')
        Path = ''
        FileSetList = self.FileSets.getElementsByTagName('FileSet')
        for FileSet in FileSetList:
            if FileSet.hasAttribute('Name'):
                if FileSet.getAttribute('Name').find('source') != -1 or FileSet.getAttribute('Name').find('constrs') != -1 or FileSet.getAttribute('Name').find('sim') != -1:
                    FileList = FileSet.getElementsByTagName('File')
                    for File in FileList:
                        if File.hasAttribute('Path'):
                            Path = File.getAttribute('Path')
                            if os.path.splitext(Path)[1] != '.xci':
                                Path = self.replacePathConst(Path)
                                WrFile.write(Path + '\n')
        WrFile.close()
        return True

    # 提取全部代码文件
    def getAllCodeFiles(self, FileListPath = './filelist.f'):
        if os.path.isdir('./copy_code_files/') == False:
            os.mkdir('./copy_code_files')
        self.logAllCodeFilesPath(FileListPath)
        RdFile = open(FileListPath, 'r', encoding='utf-8')
        CodeFilePathList = RdFile.readlines()
        RdFile.close()
        for CodeFilePath in CodeFilePathList:
            CodeFilePath = CodeFilePath.replace('\n', '')
            CopyPath = './copy_code_files/' + CodeFilePath.replace('../', '')
            # copyFile(CodeFilePath, CopyPath)
            print('Converting ' + CodeFilePath)
            convertToUTF_8InNewFile(CodeFilePath, CopyPath)
            print('Convert Finished!')
        return True

    # 提取全部ip核的xci文件
    def getAllXciFiles(self, WrFilePath = './iplist.f'):
        if os.path.isdir('./copy_ip_files/') == False:
            os.mkdir('./copy_ip_files')
        WrFile = open(WrFilePath, 'w')
        Path = ''
        CopyPath = ''
        FileSetList = self.FileSets.getElementsByTagName('FileSet')
        for FileSet in FileSetList:
            FileList = FileSet.getElementsByTagName('File')
            for File in FileList:
                if File.hasAttribute('Path'):
                    Path = File.getAttribute('Path')
                    if os.path.splitext(Path)[1] == '.xci':
                        Path = self.replacePathConst(Path)
                        WrFile.write(Path + '\n')
                        CopyPath = './copy_ip_files/' + Path.replace('../', '')
                        copyFile(Path,CopyPath)
        WrFile.close()
        return True

    # 统计全部代码文件的行数
    def calcuCodeFileLines(self, FileListPath = './filelist.f', WrFilePath = './calcu_code_files_lines/CodeLinesResult.txt'):
        if os.path.isdir('./calcu_code_files_lines/') == False:
            os.mkdir('./calcu_code_files_lines')
        self.logAllCodeFilesPath(FileListPath)
        RdFile = open(FileListPath, 'r', encoding='utf-8')
        CodeFilePathList = RdFile.readlines()
        AllCodeFilesBlockCommLinesNum = 0
        AllCodeFilesLineCommLinesNum = 0
        AllCodeFilesEmptyLinesNum = 0
        AllCodeFilesCodeLinesNum = 0
        AllCodeFilesTotalLinesNum = 0
        VerilogFileNum = 0
        ExistVerilogFileNum = 0
        NotExistVerilogFileNum = 0
        WrFile = open(WrFilePath, 'w')
        for CodeFilePath in CodeFilePathList:
            CodeFilePath = CodeFilePath.replace('\n', '')
            snaffix = os.path.splitext(CodeFilePath)[1]
            if snaffix == '.v' or snaffix == '.sv' or snaffix == '.vhd':
                CodeFilePath = self.replacePathConst(CodeFilePath)
                CodeFile = VerilogFile(CodeFilePath)
                if CodeFile.InitSuccess:
                    CodeFile.countLinesNum()
                    WrFile.write('/*****************************************************/\n')
                    WrFile.write(CodeFilePath + '\n')
                    WrFile.write('Block Comment Lines : ' + str(CodeFile.BlockCommentsLinesNum) + '\n')
                    WrFile.write('Line  Comment Lines : ' + str(CodeFile.LineCommentsLinesNum)  + '\n')
                    WrFile.write('Empty         Lines : ' + str(CodeFile.EmptyLinesNum)         + '\n')
                    WrFile.write('Code          Lines : ' + str(CodeFile.CodeLinesNum)          + '\n')
                    WrFile.write('Total         Lines : ' + str(CodeFile.TotalLinesNum)         + '\n')
                    AllCodeFilesBlockCommLinesNum += CodeFile.BlockCommentsLinesNum
                    AllCodeFilesLineCommLinesNum  += CodeFile.LineCommentsLinesNum
                    AllCodeFilesEmptyLinesNum     += CodeFile.EmptyLinesNum
                    AllCodeFilesCodeLinesNum      += CodeFile.CodeLinesNum
                    AllCodeFilesTotalLinesNum     += CodeFile.TotalLinesNum
                    ExistVerilogFileNum += 1
                elif not os.path.isfile(CodeFilePath):
                    WrFile.write('/*****************************************************/\n')
                    WrFile.write(CodeFilePath + '\n')
                    WrFile.write('This file is not exist!\n')
                    NotExistVerilogFileNum += 1
                VerilogFileNum += 1
        WrFile.write('/*****************************************************/\n')
        WrFile.write('All       Code Files\n')
        WrFile.write('All       Code Files Num  : ' + str(VerilogFileNum) + '\n')
        WrFile.write('Exist     Code Files Num  : ' + str(ExistVerilogFileNum) + '\n')
        WrFile.write('Not Exist Code Files Num  : ' + str(NotExistVerilogFileNum) + '\n')
        WrFile.write('All   Block Comment Lines : ' + str(AllCodeFilesBlockCommLinesNum) + '\n')
        WrFile.write('All   Line  Comment Lines : ' + str(AllCodeFilesLineCommLinesNum)  + '\n')
        WrFile.write('All   Empty         Lines : ' + str(AllCodeFilesEmptyLinesNum)     + '\n')
        WrFile.write('All   Code          Lines : ' + str(AllCodeFilesCodeLinesNum)      + '\n')
        WrFile.write('All   Total         Lines : ' + str(AllCodeFilesTotalLinesNum)     + '\n')
        WrFile.write('/*****************************************************/\n')
        WrFile.close()
        print('--**--**--**--**--**--**--**--********--**--**--**--**--**--**--**--')
        print('--                             FINISH                             --')
        print('--    Details -> ./calcu_code_files_lines/CodeLinesResult.txt     --')
        print('--**--**--**--**--**--**--**--********--**--**--**--**--**--**--**--')
        print('-- All       Code Files                                           --')
        print('-- All       Code Files Num  : ' + str(VerilogFileNum) + (35-len(str(VerilogFileNum)))*' ' + '--')
        print('-- Exist     Code Files Num  : ' + str(ExistVerilogFileNum) + (35-len(str(ExistVerilogFileNum)))*' ' + '--')
        print('-- Not Exist Code Files Num  : ' + str(NotExistVerilogFileNum) + (35-len(str(NotExistVerilogFileNum)))*' ' + '--')
        print('-- All   Block Comment Lines : ' + str(AllCodeFilesBlockCommLinesNum) + (35-len(str(AllCodeFilesBlockCommLinesNum)))*' ' + '--')
        print('-- All   Line  Comment Lines : ' + str(AllCodeFilesLineCommLinesNum) + (35-len(str(AllCodeFilesLineCommLinesNum)))*' ' + '--')
        print('-- All   Empty         Lines : ' + str(AllCodeFilesEmptyLinesNum) + (35-len(str(AllCodeFilesEmptyLinesNum)))*' ' + '--')
        print('-- All   Code          Lines : ' + str(AllCodeFilesCodeLinesNum) + (35-len(str(AllCodeFilesCodeLinesNum)))*' ' + '--')
        print('-- All   Total         Lines : ' + str(AllCodeFilesTotalLinesNum) + (35-len(str(AllCodeFilesTotalLinesNum)))*' ' + '--')
        print('--**--**--**--**--**--**--**--********--**--**--**--**--**--**--**--')
        return True

    # 针对综合后的结果生成edf网表文件和相关的verilog以及VHDL源代码文件
    def writeEdfAndCodeFile(self):
        DirPath = './edf_verilog_vhdl_stub/'
        if os.path.isdir(DirPath) == False:
            os.mkdir(DirPath)
        EdfFilePath = DirPath + self.SynthSrcSetConfigDict['TopModule'] + '.edf'
        VerilogFilePath = DirPath + self.SynthSrcSetConfigDict['TopModule'] + '_stub.v'
        VhdlFilePath = DirPath + self.SynthSrcSetConfigDict['TopModule'] + '_stub.vhd'
        TclFilePath = './write_edf_verilog_vhdl.tcl'
        TclFile = open(TclFilePath, 'w')
        TclFile.writelines('open_run ' + self.RunSynthActiveDict['Id']+ ' -name ' + self.RunSynthActiveDict['Id'] + '\n')
        TclFile.writelines('write_edif ' + EdfFilePath + '\n')
        TclFile.writelines('write_verilog -mode synth_stub ' + VerilogFilePath + '\n')
        TclFile.writelines('write_vhdl -mode synth_stub ' + VhdlFilePath + '\n')
        TclFile.close()
        self.sourceTclByBatchMode(TclFilePath)

    # 运行
    def run(self):
        # 若该方法之前的执行的初始化操作未完成/失败，则直接返回失败
        if self.InitSuccess == False:
            print('Error: Init Failed! Can not continue to run!')
            return False
        # 生成脚本、编译、Elaborate
        # self.sourceTclByBatchMode(self.SIM_TCL_FILE_NAME)
        # self.startCompile()
        # self.startElaborate()
        while True:
            # 交互界面
            self.startInteraction()
            # 判断交互结果并执行对应功能
            if self.InputNum == '1':
                break
            elif self.InputNum == '2':
                if self.VivadoExist:
                    self.openGUIProj()
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '3':
                self.startCompile()
                self.startElaborate()
                self.startSimulate()
            elif self.InputNum == '4':
                if self.VivadoExist:
                    self.sourceTclByBatchMode(self.SIM_TCL_FILE_NAME)
                    self.startCompile()
                    self.startElaborate()
                    self.startSimulate()
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '5':
                if self.VivadoExist:
                    self.startSimulate()
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '6':
                self.getAllCodeFiles()
            elif self.InputNum == '7':
                self.getAllXciFiles()
            elif self.InputNum == '8':
                if self.VivadoExist:
                    self.sourceTclByBatchMode(self.SYNTH_TCL_FILE_NAME)
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '9':
                if self.VivadoExist:
                    self.sourceTclByBatchMode(self.IMPL_TCL_FILE_NAME)
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '10':
                if self.VivadoExist:
                    self.writeEdfAndCodeFile()
                else:
                    print('Error: There is no Vivado' + self.PROJ_VERSION + ' in the ' + self.VIVADO_DIR + ' of this os!')
            elif self.InputNum == '11':
                self.__init__()
            elif self.InputNum == '12':
                self.calcuCodeFileLines()
            else:
                print('Error: Invalid num!')
        return True

