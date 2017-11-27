#design store script rewrite
print "importing libraries"

import subprocess
import logging
import logging.config
import logging.handlers
import os
import optparse
import sys
import re
import time

print "starting"

def updateProcess(mainDir):
	logging.basicConfig(filename=(mainDir+'/LOGOUT.log'),level=logging.DEBUG)
	logging.debug("------------------------------------------------------------------------------")
	logging.debug("def: updateProcess")
	print mainDir
	
	class upgradeClass:
		
		def __init__(up):
			print(mainDir + '/LOGOUT.log')
			logging.debug("def: main")
			up.mainDir = mainDir
			up.lastSuc = False
			up.foundQpf = False
			up.foundPar = False
			up.projName = ""
			up.extracParCommand = "qextract"
			up.cmdOut = ""
			up.updateIpCommand = "quartus_sh --ip_upgrade -mode all "
			up.fileList = ['platform_setup.tcl', 'filelist.txt']
			up.qsfFile = ''
			up.qpfFileName = "top"
			up.qsfFileName = ""
			up.filesDictionary = {"QIP_FILE", "SOURCE_FILE", "VHDL_FILE", "SDC_FILE", "VERILOG_FILE", "SYSTEMVERILOG_FILE", "EDA_TEST_BENCH_FILE", "TCL_SCRIPT_FILE"}
			up.foundQip = False
			up.qipList = []
			up.nestedQuip = False
			up.directoryList = []
			up.quipParentDirectory = ''
			up.archiveComand = "quartus_sh --archive -input filelist.txt -output upgrade.qar"
			up.excludeDictionary = {".qprs", ".qsf", ".qpf"}
			up.testDirName = 'testDirectory'
			up.copyArchiveCommand = "cp upgrade.qar " + up.testDirName + "/upgrade.qar"
			up.extractArchiveCommand = "quartus_sh --platform -name upgrade.qar"
			up.compileCommand = "quartus_sh --flow compile top.qpf"
			up.qsysFiles = []
			up.qsysFlag = False
			up.blanketUpGrade = False
			up.nonQuartusFileList = ["txt", "doc", "docx", "xls", "xlsx", "pdf"]
			up.masterImageFileTypes = ["sof", "pof", "elf", "iso"] #add hex files for memeory configuration
			
			up.classMain()
			
		'''
		* def name:			classMain
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is the main for the upgrade class
		* 
		* dependantcies:	This def is only dependant on the class exsisting and all varibles 
		*					in the classe beeing initialised. Also this def should be called 
		*					at the end of the init in the class.
		'''
		def classMain(up):
			up.checkDir()
			up.genDirectoryList()
			if(up.lastSuc == False):
				return
			up.lastSuc = False
			up.checkForParQar()
			if(up.foundPar == up.foundQpf):
				print "found multiple projects or none"
				logging.debug("found multiple projects or none")
				return
			if(up.foundPar == True):
				up.extractPar()
			if(up.foundQpf == True):
				print "qpf not supported yet"
				return
			if(up.lastSuc == False):
				return
			up.lastSuc == False
			print "upgrading IP (this may take a while)"
			up.upgradeIp()
			print "building file list"
			up.lastSuc = False
			up.openQsfFile()
			if(up.lastSuc == False):
				return
			up.parsQsf()
			up.closeQsfFile()
			up.openQsfFile()
			up.createPlatformSetUpFile()
			up.closeQsfFile()
			up.findQsysFiles()
			up.findMasterImage()
			up.parsQips()
			up.individualFileUpgrade()
			up.checkForReadMe()
			up.checkFileList()
			up.generateFileList()
			up.archive()
			up.createTestDirectory()
			up.copyArchive()
			logging.debug("def: changing directory to: " + up.mainDir + '/' + up.testDirName)
			os.chdir(up.mainDir + '/' + up.testDirName)
			up.extractArchiveFile()
			up.compileProject() 
			print "DONE"
		
		'''
		* def name:			checkDir
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def checks that the entered directory exsists and is not a specific file
		* 
		* dependantcies:	up.mainDir is populated with the file path the user intends to use.
		'''
		def checkDir(up):
			logging.debug("def: checkDir")
			if(os.path.isdir(up.mainDir) == False):
				print "given path is not a directory"
				logging.debug("given path is not a directory")
				up.lastSuc = False
				return
			if(os.path.exists(up.mainDir) == False):
				print "given path does not exsist"
				logging.debug("given path does not exsist")
				up.lastSuc = False
				return
			logging.debug("good directory")
			up.lastSuc = True
		
		'''
		* def name:			genDirectoryList
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def creates a list of all sub directories in the mainDir if there are any
		* 
		* dependantcies:	up.mainDir is populated with the file path the user intends to use.
		'''
		def genDirectoryList(up):
			logging.debug("def: genDirectoryList")
			for x in os.listdir('.'):
				up.directoryList.append(x)
		
		def checkForParQar(up):
			logging.debug("def: checkForParQar")
			projectList = []
			projectList = up.findAllFilesOfType("par")
			if(len(projectList) > 1):
				return
			if(len(projectList) == 1):
				up.foundPar = True
				up.projName = projectList[0]
			projectList = up.findAllFilesOfType("qpf")
			if(len(projectList) > 1):
				return
			if(len(projectList) == 1):
				up.lastSuc = False
				up.foundQpf = True
				up.projName = projectList[0]
		
		'''
		* pulled from the original script
		'''
		def findAllFilesOfType(up, fileExt): #pulled from original script
			logging.debug("def: findAllFilesOfType")
			"""
			Gets a list of all the files of a certain type in a directory
			:param file_ext: a string representing the file type to search for
			:return: a list of paths to all of the files with the given type and their
			"""
			# Make sure the file extension has a dot before it
			if fileExt[0] != ".":
				fileExt = "." + fileExt
			# Holds all of the files with the given extension
			fileList = []
			# Now recursively get all of the files with the given extension
			for dirpath, dirnames, filenames in os.walk("."):
				# Do not include the test directory when searching for files
				if "test" in dirnames:
					dirnames.remove("test")
				for filename in filenames:
					# If any of the files have the given extension, add it to the list of files found
					if filename.endswith(fileExt):
						# Get the full pathname of the qar file and add it to the list of files
						filepath = os.path.join(dirpath, filename)
						fileList.append(os.path.normpath(filepath))
			return fileList
		
		'''
		* def name:			extractPar
		* 
		* creator:			Dustin Henderson
		* 
		* description:		this def extracts the .par file that comes from the design store. The project
		*					extracted from the par file will always be named top. Before the project extracts
		*					the par it moves to the mainDir location.
		* 
		* dependantcies:	mainDir must be a valid directory containing a par file. 
		'''
		def extractPar(up):
			logging.debug("def: extractPar")
			logging.debug("Changing directory to " + mainDir)
			os.chdir(mainDir)
			logging.debug("comand: " + str(up.extracParCommand))
			print "extracting par file"
			try:
				up.cmdOut = subprocess.check_output(up.extracParCommand, shell=True)
				logging.debug("extracted par successfully")
				print "extracted par successfully"
				up.lastSuc = True
				time.sleep(5) #give the file system time to update
			except subprocess.CalledProcessError as testExcept:
				logging.debug("error extracting par")
				logging.debug("error message: " + str(testExcept))
				up.lastSuc = False
		
		def findQsysFiles(up):
			logging.debug("def: findQsysFiles")
			up.qsysFiles = up.findAllFilesOfType("qsys")
			logging.debug("qsysFiles len :" + str(len(up.qsysFiles)))
			if(len(up.qsysFiles) != 0):
				logging.debug("found qsys")
				up.qsysFlag = True
				for files in up.qsysFiles:
					up.fileList.append(files)
		
		def findMasterImage(up):
			logging.debug("def: findMasterImage")
			for fileType in up.masterImageFileTypes:
				for fileFound in up.findAllFilesOfType(fileType):
					up.fileList.append(fileFound)
			
		def upgradeIp(up):
			logging.debug("def: upgradeIp")
			try:
				up.cmdOut = subprocess.check_output((up.updateIpCommand + up.qpfFileName), shell=True)
				logging.debug("updated IP successfully")
				print "pdated IP successfully"
			except subprocess.CalledProcessError as testExcept:
				logging.debug("error upgrading IP with blanket statement will try individual files")
				logging.debug("error message: " + str(testExcept))
				blanketUpGrade = False
		
		def openQsfFile(up):
			logging.debug("def: openQsfFile")
			try: 
				print "opening qsf file"
				logging.debug("opening qsf file: " + up.projName)
				print "project name: ", up.projName
				up.qsfFile = open("top.qsf", "r")
				up.lastSuc = True
			except:
				logging.debug("failed to open qsf file: " + up.projName)
				print "failed to open qsf file"
				up.lastSuc = False
				
		def createPlatformSetUpFile(up):
			logging.debug("def: createPlatformSetUpFile")
			file = open('platform_setup.tcl', 'w')
			file.write('proc ::setup_project {} {\n')
			for line in up.qsfFile:
				file.write(line)
			file.write('\n}')
			file.close()
				
		def parsQsf(up):
			logging.debug("def: parsQsf")
			for line in up.qsfFile:
				for fileType in up.filesDictionary:
					if fileType in line:
						line = up.parsFileNameFromQsf(fileType, line)
						up.fileList.append(line)
						if(fileType == 'QIP_FILE'):
							logging.debug("found qip file. qip flag set true")
							up.foundQip = True
							up.qipList.append(line)
						logging.debug("found file: " + line)
				
		def parsFileNameFromQsf(up, fileType, line):
			logging.debug("def: parsFileNameFromQsf")
			line = re.sub('set_global_assignment -name ' + fileType + ' ', '', line)
			if '-tag platfrom' in line:
				line = re.sub(' -tag platfrom', '', line) 	#you need both platfrom and platform
			if '-tag platform' in line:						#which one shows up is dependant on the
				line = re.sub(' -tag platform', '', line)	#version your porting from
			if '\n' in line:
				line = re.sub('\n', '', line)
			return line
			
		def closeQsfFile(up):
			logging.debug("def: closeQsfFile")
			up.qsfFile.close()
		
		def parsQips(up):
			logging.debug("def: parsQuips")
			for file in up.qipList:
				try:
					up.parsQuipParent(file)
					logging.debug("opening file: " + file)
					file = open(file, "r") #'ip/bemicro_max10_serial_flash_controller/bemicro_max10_serial_flash_controller.qip'
					logging.debug('file opened successfully')
					up.readQip(file)
					logging.debug('closing qip file')
					file.close()
				except:
					logging.debug("failed to open file")
		
		def parsQuipParent(up, file):
			print os.path.dirname(file) + '/'
			up.quipParentDirectory = os.path.dirname(file) + '/'
		
		def readQip(up, file):
			logging.debug("def: readQip")
			for line in file:
				for fileType in up.filesDictionary:
					if fileType in line:
						#print line
						line = up.parsFileNameFromQip(fileType, line)
						line = up.checkForParentDir(line)
						up.fileList.append(line)
						if(fileType == 'QIP_FILE'):
							logging.debug("found qip file. qip flag set true")
							up.nestedQuip = True
						logging.debug("found file: " + line)
		
		def checkForParentDir(up, line):
			logging.debug("def: checkForParentDir")
			if(up.quipParentDirectory != '/'):
				if(up.quipParentDirectory == line[:len(up.quipParentDirectory)]):
					return line
				else:
					return up.quipParentDirectory + line
		
		def parsFileNameFromQip(up, fileType, line):
			logging.debug("def: parsFileNameFromQip")
			if(line.find('$::quartus(qip_path)') == -1):
				line = up.parsFileNameFromQsf(fileType, line)
			else:
				line = line[line.find('$::quartus(qip_path)')+22:]
				if '"]' in line:
					line = re.sub('"]', '', line)
				if '\n' in line:
					line = re.sub('\n', '', line)
			return line
		
		def individualFileUpgrade(up):
			updateCommand = ""
			logging.debug("def: individualFileUpgrade")
			logging.debug("qsysGlag status: " + str(up.qsysFlag))
			if(up.qsysFlag == True):
				for qipFile in up.qipList:
					for qsysFile in up.qsysFiles:
						print "qsys :", re.sub('.qsys', '', qsysFile)
						print "qip  :", re.sub('.qip', '', qipFile)
						if re.sub('.qsys', '', qsysFile) in re.sub('.qip', '', qipFile):
							print "match"
							up.qipList.remove(qipFile)
						print "\n"
				for qsysFile in up.qsysFiles:
					print "quartus_sh -ip_upgrade -variation_files " + qsysFile + " top"
			for qipFile in up.qipList:
				if os.path.isfile(re.sub('.qip', '.v', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " top"
					logging.debug("command: " + "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " top")
					print updateCommand
					up.cmdOut = subprocess.check_output(updateCommand, shell=True)
				elif os.path.isfile(re.sub('.qip', '.vhd', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					logging.debug("command: " + updateCommand)
					up.cmdOut = subprocess.check_output(updateCommand, shell=True)
				elif os.path.isfile(re.sub('.qip', '.vhdl', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					logging.debug("command: " + updateCommand)
					up.cmdOut = subprocess.check_output(updateCommand, shell=True)
				elif os.path.isfile(re.sub('.qip', '.sv', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"
					logging.debug("command: " + "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top")
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"
					up.cmdOut = subprocess.check_output(updateCommand, shell=True)
				else:
					print "Failed to find IP file in the directory"
					logging.debug("Failed to find IP file in the directory")
		
		def checkForReadMe(up):
			logging.debug("def: checkForReadMe")
			for fileType in up.nonQuartusFileList:
				for textFiles in up.findAllFilesOfType(fileType):
					up.fileList.append(textFiles)
			
		def checkFileList(up):
			logging.debug("def: checkFileList")
			for line in up.fileList:
				for exclude in up.excludeDictionary:
					if(exclude in line):
						up.fileList.remove(line)
		
		def generateFileList(up):
			logging.debug("def: generateFileList")
			file = open("filelist.txt", "w")
			for line in up.fileList:
				file.write(line + '\n')
			file.close()
	
		def archive(up):
			logging.debug("def: archive")
			logging.debug("comand: " + str(up.extracParCommand))
			print "archiving project file"
			try:
				up.cmdOut = subprocess.check_output(up.archiveComand, shell=True)
				logging.debug("extracted par successfully")
				print "archived project successfully"
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "error archiving project"
				logging.debug("error archived project")
				logging.debug("error message: " + str(testExcept))
				up.lastSuc = False
	
		def createTestDirectory(up):
			logging.debug("def: createTestDirectory")
			try:
				print "creating test directory"
				logging.debug("creating test directory")
				os.mkdir(up.testDirName)
			except:
				print "Error failed to create test directory"
				logging.debug("Error failed to create test directory")
		
		def copyArchive(up):
			logging.debug("def: copyArchive")
			try:
				print "copping archive file to test directory"
				logging.debug("copping archive file to test directory")
				up.cmdOut = subprocess.check_output(up.copyArchiveCommand, shell=True)
			except subprocess.CalledProcessError as testExcept:
				print "Error copping archive file to test directory"
				logging.debug("error copping archive file to test directory")
		
		def extractArchiveFile(up):
			logging.debug("def: extractArchiveFile")
			try:
				print "extracting archive file"
				logging.debug("extracting archive file")
				up.cmdOut = subprocess.check_output(up.extractArchiveCommand, shell=True)
			except subprocess.CalledProcessError as testExcept:
				print "Error extracting archive file"
				logging.debug("error extracting archive file")
				
		def compileProject(up):
			logging.debug("def: extractArchiveFile")
			try:
				print "compiling test project"
				logging.debug("compiling test project")
				up.cmdOut = subprocess.check_output(up.compileCommand, shell=True)
				#print up.cmdOut
				logging.debug(up.cmdOut)
			except subprocess.CalledProcessError as testExcept:
				print "Error compiling test project"
				logging.debug("error compiling test project")
		
	runClass = upgradeClass()

def main (argv):
	option_parser = optparse.OptionParser()

	option_parser.set_defaults(upgrade = None)
	
	option_parser.add_option("-u", "--single_upgrade", dest="upgrade", action="store",
		help="Will upgrade qsys based IP")
		
	options, args = option_parser.parse_args(argv)
	
	if options.upgrade != None:
		os.chdir(options.upgrade)
		updateProcess(mainDir = options.upgrade)
		
if __name__ == '__main__':
	running = main(sys.argv)
	sys.exit(running)