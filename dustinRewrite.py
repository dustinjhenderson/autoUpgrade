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
			#example qextract syntax
			#"quartus_sh --platform_install -package audio_monitor.par; quartus_sh --platform -name audio_monitor -search_path \."
			up.extracParCommand = "" # will get filled in when the name is detected
			up.extracParCommand1 = "quartus_sh --platform_install -package " 
			up.extracParCommand2 = "; quartus_sh --platform -name " 
			up.extracParCommand3 = " -search_path \."
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
			print "upgrading IP the easy way (this may take a while)"
			up.upgradeIp()
			print "building file list"
			up.lastSuc = False
			up.openQsfFile()
			if(up.lastSuc == False):
				return
			up.parsQsf()
			up.closeQsfFile()
			up.lastSuc = False
			up.openQsfFile()
			if(up.lastSuc == False):
				return
			up.createPlatformSetUpFile()
			up.closeQsfFile()
			up.findQsysFiles()
			up.findMasterImage()
			up.lastSuc = False
			up.parsQips()
			if(up.lastSuc == False):
				return
			if(up.blanketUpGrade == False):
				#individually upgrade each ip
				up.individualFileUpgrade()
				#clear the file list
				up.fileList = ['platform_setup.tcl', 'filelist.txt'] 
				up.foundQip = False
				up.qipList = []
				up.nestedQuip = False
				up.quipParentDirectory = ''
				up.qsysFiles = []
				up.qsysFlag = False
				#reparse the updated and upgraded project files
				up.openQsfFile()
				if(up.lastSuc == False):
					return
				up.parsQsf()
				up.closeQsfFile()
				up.lastSuc = False
				up.openQsfFile()
				if(up.lastSuc == False):
					return
				up.createPlatformSetUpFile()
				up.closeQsfFile()
				up.findQsysFiles()
				up.findMasterImage()
				up.lastSuc = False
				up.parsQips()
				if(up.lastSuc == False):
					return
			up.checkForReadMe()
			up.checkFileList()
			up.lastSuc = False
			up.generateFileList()
			if(up.lastSuc == False):
				return
			up.lastSuc = False
			up.archive()
			if(up.lastSuc == False):
				return
			up.lastSuc = False
			up.createTestDirectory()
			if(up.lastSuc == False):
				return
			up.lastSuc = False
			up.copyArchive()
			if(up.lastSuc == False):
				return
			try:
				logging.debug("def: changing directory to: " + up.mainDir + '/' + up.testDirName)
				os.chdir(up.mainDir + '/' + up.testDirName)
			except:
				print "failed to change working directory to the test directory"
				return
			up.lastSuc = False
			up.extractArchiveFile()
			if(up.lastSuc == False):
				return
			up.lastSuc = False
			up.compileProject()
			if(up.lastSuc == False):
				return
			logging.debug("--------------------------------------------------------------------------------------")
			logging.debug("***                                    Done!                                       ***")
			logging.debug("***               Upgrade of the project was successfully completed!               ***")
			logging.debug("--------------------------------------------------------------------------------------")
			print "--------------------------------------------------------------------------------------"
			print "***                                    Done!                                       ***"
			print "***               Upgrade of the project was successfully completed!               ***"
			print "--------------------------------------------------------------------------------------"
		
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
			up.extracParCommand = up.extracParCommand1+ up.projName + up.extracParCommand2 + re.sub('.par', '', up.projName) + up.extracParCommand3
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
		
		'''
		* def name:			findQsysFiles
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def locates any qsys files in the mainDir. Additionally it sets a the qsysFlag 
		*					to true if it finds them. This way later down the line in the single ip upgrade 
		*					process the script will know to look for qsys files. This def will also append the
		*					the qsys files too the up.filesList.
		* 
		* dependantcies:	up.mainDir is populated with the file path the user intends to use. The qsysFlag
		*					needs to be initialised False. 
		'''
		def findQsysFiles(up):
			logging.debug("def: findQsysFiles")
			up.qsysFiles = up.findAllFilesOfType("qsys")
			for file in up.qsysFiles:
				if(".BAK." in  file):
					up.qsysFiles.remove(file)
			logging.debug("qsysFiles len :" + str(len(up.qsysFiles)))
			if(len(up.qsysFiles) != 0):
				logging.debug("found qsys")
				up.qsysFlag = True
				for files in up.qsysFiles:
					up.fileList.append(files)
		
		'''
		* def name:			findMasterImage
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This Def is responcable for finding the master image files that are often included in 
		*					design examples. It uses a list of file extentions to find completed synthsys files.
		*					for example the most common master image file is an sof file. The file extentions are
		*					listed at the top of the script in the initial block for easy editing.
		* 
		* dependantcies:	up.masterImageFileTypes needs to be an initialised list containing the file exensions
		*					of any files that need to 
		'''
		def findMasterImage(up):
			logging.debug("def: findMasterImage")
			for fileType in up.masterImageFileTypes:
				for fileFound in up.findAllFilesOfType(fileType):
					up.fileList.append(fileFound)
		
		'''
		* def name:			upgradeIp
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is used to attempt a blanket ip upgrade of the project. The command works about
		*					60% of the time. If it works it is really easy to skip the one by one upgrade. 
		* 
		* dependantcies:	The command for this def is sotred in the initial as up.updateIpCommand. It's initialised
		*					there for easy future editing.
		'''		
		def upgradeIp(up):
			logging.debug("def: upgradeIp")
			try:
				up.cmdOut = subprocess.check_output((up.updateIpCommand + up.qpfFileName), shell=True)
				logging.debug("updated IP successfully")
				print "pdated IP successfully"
				up.blanketUpGrade = True
			except subprocess.CalledProcessError as testExcept:
				logging.debug("error upgrading IP with blanket statement will try individual files")
				logging.debug("error message: " + str(testExcept))
				up.blanketUpGrade = False
		
		'''
		* def name:			openQsfFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def opens the qsf file inorder for it to be parced. If it fails to open for any reason
		*					it will set the up.lastSuc to false
		*
		* dependantcies:	up.lastsuc is a bool used to indicate failur to open the file
		'''	
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
				
		'''
		* def name:			createPlatformSetUpFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def uses the open qsf file and copies the contence into the platform_setup tcl file
		*					the def also adds proc ::setup_project{}{ to the beginning of the file and the closing }
		*					at the end of the file.
		*
		* dependantcies:	This module depends on the up.qsfFile = open(qsfFile r) being exicuted starting at the 
		*					beginning of the file
		'''	
		def createPlatformSetUpFile(up):
			logging.debug("def: createPlatformSetUpFile")
			file = open('platform_setup.tcl', 'w')
			file.write('proc ::setup_project {} {\n')
			for line in up.qsfFile:
				file.write(line)
			file.write('\n}')
			file.close()
		
		'''
		* def name:			parsQsf
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This module is responcable for finding any files used by the project and appending them
		*					to the project files list. It works by reading the tcl syntax in the qsf file. In the 
		*					init of the class there is a dictionary of filetypes the parser looks for. This dictionary
		*					is used to identify qip, verilog, vhdl, and ect files that need to be included in the filelist.
		*
		* dependantcies:	The initial of the class needs to include a dictionary pre populated with the file types the
		*					parser needs to Identify. Additionally, parsFileNameFromQip def needs to exsist and return
		*					the file location and name when the tcl line is passed into it.
		'''	
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
				
		'''
		* def name:			parsFileNameFromQsf
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def parses the location and name from a line of tcl code in the qsf file. The def
		*					can only accept one line of code at a time.
		*
		* dependantcies:	Only one line of tcl code at a time (passed in as a string) as line. fileType needs to be
		*					passed in. The file type is the syntax used by tcl to identify the type of file. For example
		*					a verilog file is denoted with "VERILOG_FILE".
		'''	
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
			
		'''
		* def name:			closeQsfFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		this module closes the qsf file
		*
		* dependantcies:	the up.qsfFile needed to the the project qsf file opened
		'''	
		def closeQsfFile(up):
			logging.debug("def: closeQsfFile")
			up.qsfFile.close()
		
		'''
		* def name:			parsQips
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This module parses any quip found in the qsf file for files that need to be included for ip.
		*					It runs thought each ......................................................................
		*
		* dependantcies:	...........................................................................................
		'''	
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
					up.lastSuc = True
				except:
					logging.debug("failed to open qip file")
					up.lastSuc = False
		
		'''
		* def name:			parsQuipParent
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	this def needs to have
		'''	
		def parsQuipParent(up, file):
			print os.path.dirname(file) + '/'
			up.quipParentDirectory = os.path.dirname(file) + '/'
		
		'''
		* def name:			readQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
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
		
		'''
		* def name:			checkForParentDir
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def checkForParentDir(up, line):
			logging.debug("def: checkForParentDir")
			if(up.quipParentDirectory != '/'):
				if(up.quipParentDirectory == line[:len(up.quipParentDirectory)]):
					return line
				else:
					return up.quipParentDirectory + line
		
		'''
		* def name:			parsFileNameFromQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
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
		
		'''
		* def name:			individualFileUpgrade
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def gets skipped if the balanked upgrade works (upgradeIp). If it is needed this
		*					def upgrades each piece of ip detected in the project one at a time. Ip in a project is
		*					detected by the presence of a qip file. Evey qip file coresponds to a .qsys, .v, .vhd,
		*					or .sv file. The def starts by upgrading the qsys files in the up.qsysFiles list. While
		*					each file in the up.qsysFiles list is upgraded the file is removed from the up.qipList
		*					list. This prevents trying to upgrade the same file twice. Last the def locates the 
		*					coresponding hdl file to the quip file then runs the upgrade command. 
		*					Example:
		*						pll.qip => quartus_sh -ip_upgrade -variation_files pll.v top
		*						niosSys.qip => quartus_sh -ip_upgrade -variation_files niosSys.qip top
		* 
		* dependantcies:	This def is dependant on up.qsysFiles and up.qipList. The up.qsysFiles needs to list
		*					all qsys files used by the project. the up.qipList needs to list all qip files used
		*					by the project.
		'''	
		def individualFileUpgrade(up):
			failedFlag = False
			updateCommand = ""
			logging.debug("def: individualFileUpgrade")
			logging.debug("qsysGlag status: " + str(up.qsysFlag))
			if(up.qsysFlag == True):
				for qipFile in up.qipList:
					for qsysFile in up.qsysFiles:
						print "qsys :", re.sub('.qsys', '', qsysFile)
						print "qip  :", re.sub('.qip', '', qipFile)
						if (os.path.basename(re.sub('.qsys', '', qsysFile)) == os.path.basename(re.sub('.qip', '', qipFile))):
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
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
				elif os.path.isfile(re.sub('.qip', '.vhd', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					logging.debug("command: " + updateCommand)
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
				elif os.path.isfile(re.sub('.qip', '.vhdl', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					logging.debug("command: " + updateCommand)
					try: 
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
				elif os.path.isfile(re.sub('.qip', '.sv', qipFile)):
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"
					logging.debug("command: " + "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top")
					print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
				else:
					print ("Failed to find IP file in the directory: " + qipFile)
					logging.debug("Failed to find IP file in the directory: " + qipFile)
		
		'''
		* def name:			checkForReadMe
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def checkForReadMe(up):
			logging.debug("def: checkForReadMe")
			for fileType in up.nonQuartusFileList:
				for textFiles in up.findAllFilesOfType(fileType):
					up.fileList.append(textFiles)
		
		'''
		* def name:			checkFileList
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def checkFileList(up):
			logging.debug("def: checkFileList")
			up.fileList = list(set(up.fileList)) #remove duplicate files in file list
			for line in up.fileList:
				for exclude in up.excludeDictionary:
					if(exclude in line):
						up.fileList.remove(line)
		
		'''
		* def name:			generateFileList
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def generateFileList(up):
			logging.debug("def: generateFileList")
			try:
				file = open("filelist.txt", "w")
				for line in up.fileList:
					file.write(line + '\n')
				file.close()
				logging.debug("successfully wrote filelist.txt")
				print "successfully wrote filelist.txt"
				up.lastSuc = True
			except:
				logging.debug("failed to write filelist.txt")
				print "failed to write filelist.txt"
				up.lastSuc = False
		
		'''
		* def name:			archive
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def archive(up):
			logging.debug("def: archive")
			logging.debug("comand: " + str(up.archiveComand))
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
	
		'''
		* def name:			createTestDirectory
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def createTestDirectory(up):
			logging.debug("def: createTestDirectory")
			try:
				print "creating test directory"
				logging.debug("creating test directory")
				os.mkdir(up.testDirName)
				up.lastSuc = True
			except:
				print "Error failed to create test directory"
				logging.debug("Error failed to create test directory")
				up.lastSuc = False
		
		'''
		* def name:			copyArchive
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def copyArchive(up):
			logging.debug("def: copyArchive")
			try:
				print "copping archive file to test directory"
				logging.debug("copping archive file to test directory")
				up.cmdOut = subprocess.check_output(up.copyArchiveCommand, shell=True)
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "Error copping archive file to test directory"
				logging.debug("error copping archive file to test directory")
				up.lastSuc = False
		
		'''
		* def name:			extractArchiveFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def extractArchiveFile(up):
			logging.debug("def: extractArchiveFile")
			try:
				print "extracting archive file"
				logging.debug("extracting archive file")
				up.cmdOut = subprocess.check_output(up.extractArchiveCommand, shell=True)
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "Error extracting archive file"
				logging.debug("error extracting archive file")
				up.lastSuc = False
		
		'''
		* def name:			compileProject
		* 
		* creator:			Dustin Henderson
		* 
		* description:		
		* 
		* dependantcies:	
		'''	
		def compileProject(up):
			logging.debug("def: compileProject")
			try:
				print "compiling test project"
				logging.debug("compiling test project")
				up.cmdOut = subprocess.check_output(up.compileCommand, shell=True)
				#print up.cmdOut
				logging.debug(up.cmdOut)
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "Error compiling test project"
				logging.debug("error compiling test project")
				up.lastSuc = False
		
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