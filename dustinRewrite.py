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


'''*********************************************************************************************'''
'''**  Main upgrade class                                                                      *'''
'''** Description: 	This class is used to upgrade exsisting project from the design store      *'''
'''** 				archived in a .par extention. Almos all varibles passed from one def to    *'''
'''**				to another are initialed or instantiated in the ___init___ def of the class*'''
'''** 				See the developer section of the documentation to see how to edit thes     *'''
'''** 				varibles to update, change, or fix the functionality of the script*		   *'''
'''**                                                                                          *'''
'''** Dependancies: This class is dependant on having the main directory parsed and passed to  *'''
'''** 				The main directory needs to point to the directory containing the par fill *'''
'''** 				that needs to be upgraded.												   *'''
'''*********************************************************************************************'''
def updateProcess(mainDir, packageBool=False):
	logging.basicConfig(filename=(mainDir+'/LOGOUT.log'),level=logging.DEBUG)
	logging.debug("------------------------------------------------------------------------------")
	logging.debug("def: updateProcess")
	print "------------------------------------------------------------------------------"
	print "/t/tSTARTING INFO"
	print "Main Directory:/t", mainDir
	quartusVer = subprocess.check_output("which quartus", shell=True)
	print "Quartus Version:/t", quartusVer
	
	class upgradeClass:
		
		def __init__(up):
			'''****************'''
			'''initiate logging'''
			'''****************'''
			print(mainDir + '/LOGOUT.log')
			logging.debug("def: main")
			
			'''****************'''
			'''*testing flags *'''
			'''****************'''
			up.testingParser = False	#disables extracting par upgrading ip and testing the newly created file if set to to True
			
			'''****************'''
			'''**** flags *****'''
			'''****************'''
			up.lastSuc = False			#this bool is used to tell if the last function that was run was succeful
			up.foundQpf = False			#this bool is used to tell if a qpf was found in the main directory
			up.foundPar = False			#this bool is used to tell if there is a par in the main directory
			up.foundQip = False			#bool used to flag if there is qip files in the project
			up.nestedQuip = False		#this bool flags if there is a qip file called in a qip file (currently not supported by the script)
			up.qsysFlag = False			#this bool is used to indicate whether or not a qsys file is found in the project directory
			up.blanketUpGrade = False	#this bool is used to indicate if the blanket upgrade was succeful.
			up.repairQsfBool = False
			
			'''****************'''
			'''generated lists '''
			'''****************'''
			up.qipList = []											#stores a list of all the qip files. populated after the qsf is parsed
			up.directoryList = []									#This list stores every directory in the directory passed to the script
			up.qsysFiles = []										#
			up.fileList = ['platform_setup.tcl', 'filelist.txt']	#this list stores all the files that will be written to the file list.txt used for archiving the project
			up.repairQsfLines = [] #2d
			
			'''****************'''
			'''** user lists **'''
			'''****************'''
			#list of the tags used in the settings file for files that need to be included in the file list
			up.filesDictionary = ["SYSTEMVERILOG_FILE", "QIP_FILE", "SOURCE_FILE", "VHDL_FILE", "SDC_FILE", "VERILOG_FILE", "EDA_TEST_BENCH_FILE", "TCL_SCRIPT_FILE", "QSYS_FILE", "USE_SIGNALTAP_FILE", "SIGNALTAP_FILE", "SLD_FILE", "MISC_FILE"]
			up.excludeDictionary = {".qprs", ".qsf", ".qpf", "None", ".BAK."}	#This list is all the file typse and strings that are not allowed in the file list. If they are found in the fileList they will be removed.
			up.nonQuartusFileList = ["txt", "doc", "docx", "xls", "xlsx", "pdf"]#This list stores all file typs that are possibly documentation or read me file in the project directory.
			up.masterImageFileTypes = ["sof", "pof", "elf", "iso", ".hex"]		#***TODO:*** add hex files for memeory configuration
		
			'''****************'''
			'''** user names **'''
			'''****************'''
			up.qpfFileName = "top"				#stores the name of the quartus project file
			up.qsfFileName = "top.qsf" 			#currently not detected just hard set sotres the name of the quartus setting file
			up.testDirName = 'testDirectory'	#this string stores the name of the directory that will be created to test the upgraded project. It needs to be a legal dir name and unique
			
			'''****************'''
			'''generated names '''
			'''****************'''
			up.projName = ""			#this string is used to store the name of the project
			up.packageBool = packageBool#sets the package bool
			up.mainDir = mainDir		#set the main directory the same as the one passed in to the class this is used to store the location of the
			up.qsfFile = ''				#sting stores the name of the project qsf file
			up.quipParentDirectory = ''	#This string is used to store the directory a qip file that is beeing parsed is stored in
			up.cmdOut = ""				#this sting sotres output of the cmd after a comand is run
		
			'''****************'''
			'''*** Commands ***'''
			'''****************'''
			#example qextract syntax
			#"quartus_sh --platform_install -package audio_monitor.par; quartus_sh --platform -name audio_monitor -search_path \."
			up.extracParCommand = "" # will get filled in when the name is detected
			#the three
			up.extracParCommand1 = "quartus_sh --platform_install -package "	#part one of the extract command
			up.extracParCommand2 = "; quartus_sh --platform -name " 			#part two of the extract command
			up.extracParCommand3 = " -search_path \."							#part three of the extract command
			up.archiveComand = "quartus_sh --archive -input filelist.txt -output upgrade.qar"	#This string is the archive command used to package the upgraded project
			up.updateIpCommand = "quartus_sh --ip_upgrade -mode all "			#the comand used to complete the blanket upgrade
			up.copyArchiveCommand = "cp upgrade.qar " + up.testDirName + "/upgrade.qar"	#This sting stores the command for coping upgraded archive file to the test directory
			up.extractArchiveCommand = "quartus_sh --platform -name upgrade.qar"#this string contains the command to extract the archived project created by the script
			up.compileCommand = "quartus_sh --flow compile top.qpf"				#this string contains the command for compiling the upgraded project in the test directory
		
			'''****************'''
			'''*** main Def ***'''
			'''****************'''
			if(packageBool == True):
				print "Running Packager"
				up.packagerMain()
			else:
				print "Running Upgrade"
				up.upgradeClassMain()	#call the main def of the class
		
		'''
		* def name:			packagerMain
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This is the main def for packaging projects this def only calls other defs used to package projects.
		*					no upgrade happens durring this process. The packager works baised off the same parsers that are used
		*					to find and package the files in the upgrad process.
		* 
		* dependantcies:	Dependant on the up data structure containing the defs responcable parsing fils from the project
		'''
		def packagerMain(up):
			up.checkDir()
			if(up.lastSuc == False):
				return
			try:
				logging.debug("def: changing directory to: " + up.mainDir)
				os.chdir(up.mainDir)
			except:
				print "ERROR: changing to the project directory"
				logging.debug("ERROR: changing directory to: " + up.mainDir)
				return
			up.genDirectoryList()
			up.lastSuc = False
			if(up.packageBool == True):
				up.checkForParQar()
				if(up.foundQpf == True):
					print "Found quartus project"
					print "building file list"
					up.lastSuc = False
					up.openQsfFile()
					if(up.lastSuc == False):
						return
					up.lastSuc = False			
					up.parsQsf()
					if(up.lastSuc == False):
						return
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
					if(up.testingParser == False):
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
							logging.debug("ERROR: failed to change working directory to the test directory")
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
					return
				else:
					print "Did not find qpf in the project"
					return
		
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
		def upgradeClassMain(up):
			up.checkDir()
			if(up.lastSuc == False):
				return
			try:
				logging.debug("def: changing directory to: " + up.mainDir)
				os.chdir(up.mainDir)
			except:
				print "ERROR: changing to the project directory"
				logging.debug("ERROR: changing directory to: " + up.mainDir)
				return
			up.genDirectoryList()
			up.lastSuc = False
			if(up.testingParser == False):
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
			if(up.testingParser == False):
				up.upgradeIp()
			print "building file list"
			up.lastSuc = False
			up.openQsfFile()
			if(up.lastSuc == False):
				return
			up.lastSuc = False			
			up.parsQsf()
			if(up.lastSuc == False):
				return
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
				# individually upgrade each ip
				if(up.testingParser == False):
					up.individualFileUpgrade()
				# clear the file list
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
				up.lastSuc = False
				up.parsQsf()
				if(up.lastSuc == False):
					return
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
			up.checkForUpgradInEditor()
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
			if(up.testingParser == False):
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
					logging.debug("ERROR: failed to change working directory to the test directory")
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
				logging.debug("ERROR: given path is not a directory")
				up.lastSuc = False
				return
			if(os.path.exists(up.mainDir) == False):
				print "given path does not exsist"
				logging.debug("ERROR: given path does not exsist")
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
			logging.debug(up.directoryList)
		
		#***********************************************
		#needs some work!
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
		#***********************************************
		
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
				print "error extracting par"
				logging.debug("ERROR: extracting par")
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
				# up.cmdOut = subprocess.check_output((up.updateIpCommand + up.qpfFileName), shell=True)
				# logging.debug("updated IP successfully")
				# print "pdated IP successfully"
				up.blanketUpGrade = False
			except subprocess.CalledProcessError as testExcept:
				logging.debug("WARNNING: upgrading IP with blanket statement will try individual files")
				logging.debug("WARNNING message: " + str(testExcept))
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
				logging.debug("opening qsf file: " + up.qsfFileName)
				print "project name: ", up.projName
				up.qsfFile = open(up.qsfFileName, "r")
				up.lastSuc = True
			except:
				logging.debug("ERROR: failed to open qsf file: " + up.projName)
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
			for col in up.repairQsfLines:
				logging.debug("repair 2d list: " + str(col))
			for line in up.qsfFile:
				if(up.repairQsfBool == False):
					file.write(line)
				else:
					for i in range(len(up.repairQsfLines)):
						if (re.sub('\n', '', line) != ""):
							if (re.sub('\n', '', line) == str(up.repairQsfLines[i][0])):
								logging.debug("repair line here")
								line = str(up.repairQsfLines[i][1]) + "\n"
								#line = re.sub("['", "", line)
								#line = re.sub("']", "", line)
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
						excludeBreak = False
						for exclude in up.excludeDictionary:
							if (exclude in str(line)):
								excludeBreak = True
						if(excludeBreak == True):
							break
						if(".." in line):
							logging.debug("WARNNING: Bad QSF syntax found")
							line = up.repairQsf(line)
							if(line == False):
								up.lastSuc = False
								return
						line = up.parsFileNameFromQsf(fileType, line)
						up.fileList.append(line)
						if(fileType == 'QIP_FILE'):
							logging.debug("found qip file. qip flag set true")
							up.foundQip = True
							up.qipList.append(line)
						if(fileType == 'QSYS_FILE'):
							logging.debug("found qsys file in qsf. setting qsys flag to true")
							up.qsysFlag = True #qsys flag
							up.qsysFiles.append(line) #adde it to qsys list
						logging.debug("found file: " + line)
						break
			up.lastSuc = True
				
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
			line = re.sub('\n', '', line)
			line = line.split(fileType)[1]
			if("-" in line):
				line = line.split("-")[0]
			line = re.sub('\n', '', line)
			line = re.sub(' ', '', line)
			return line
		
		'''
		* def name:			repairQsf
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def attempts to repair any broken qsf syntax. occationally files will be
		*					included in the project that are ouside of the project directory. This causes
		*					a .. infront of the file. However when the project is archived the file is
		*					is moved into the project directory. After this happens the project will not
		*					be able to find the file. This def finds the file in the project directory.
		*					then it fixes the broken line in the qsf.
		*
		* dependantcies:	
		'''	
		def repairQsf(up, line):
			logging.debug("def: repairQsf")
			logging.debug(str(os.getcwd()))
			outsideFileLocation = ""
			splitString = []
			newLine = ""
			line = re.sub("\n", "", line)
			splitString = line.split("..")
			for strings in splitString:
				logging.debug("split string: " + str(strings))
			outsideFile = os.path.basename(splitString[len(splitString)-1]) #use the last split string to find the file name to look for
			logging.debug("outside File: " + str(outsideFile))
			outsideFileLocation = up.findFile(outsideFile)
			if outsideFileLocation == False:
				logging.debug("ERROR: Unable to repair QSF file.")
				logging.debug("ERROR: File not found: \"" + outsideFile + "\"")
				return False
			outsideFileLocation = re.sub("./", "", outsideFileLocation)
			newLine = splitString[0] + outsideFileLocation
			logging.debug("old qsf line: \"" + line + "\"")
			logging.debug("new qsf line: \"" + newLine + "\"")
			up.repairQsfBool = True
			up.repairQsfLines.append([line, newLine])
			return newLine
		
		'''
		* def name:			findFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def searches for a file by name and returns its location with the file name attached. 
		*					for example if you are looking for a file named pll.v and it finds it in /ip/pll/pll.v 
		*					the def will return /ip/pll/pll.v
		*
		* dependantcies:	This def is dependant on the working directory set to directory you would like to search
		*					for the file in. Additionally the full name of the file needs to be passed to the function
		*					Last, this def will only return the first instance of the file it finds.
		'''	
		def findFile(up, searchForName):
			foundLocation = ""
			for dirpath, dirnames, filenames in os.walk("."):
				for filename in filenames:
					if searchForName == filename:
						foundLocation = os.path.join(dirpath, searchForName)
						logging.debug("found outside file location: " + str(foundLocation))
						return foundLocation
			return False
		
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
		*					It runs thought each file in the list. This def also callse another def to identify the parent
		*					directory of the file parsed from the qip file.
		*
		* dependantcies:	up.qipList needs to contain anny qip files used by the project. 
		'''	
		def parsQips(up):
			logging.debug("def: parsQuips")
			for file in up.qipList:
				logging.debug("qipList item: " + str(file))
			if not up.qipList:
				logging.debug("no qip files returning lastSuc True")
				up.lastSuc = True
				return
			for file in up.qipList:
				try:
					up.parsQuipParent(file)
					logging.debug("opening file: " + str(file))
					file = open(file, "r") #'ip/bemicro_max10_serial_flash_controller/bemicro_max10_serial_flash_controller.qip'
					logging.debug('file opened successfully')
					up.readQip(file)
					logging.debug('closing qip file')
					file.close()
					up.lastSuc = True
				except:
					logging.debug("ERROR: failed to open qip file")
					up.lastSuc = False
		
		'''
		* def name:			parsQuipParent
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is responcible for identifing the parent directory of the files contained in the qip.
		*					If the qip file is in the project directory this def will return "/"
		* 
		* dependantcies:	this def requiers that the name of the qip file be passed into it.
		'''	
		def parsQuipParent(up, file):
			logging.debug("def: parsQuipParent")
			print os.path.dirname(file) + '/'
			up.quipParentDirectory = os.path.dirname(file) + '/'
			logging.debug("quip parent: " + str(up.quipParentDirectory))
		
		'''
		* def name:			readQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		this def runs thrugh the qip file line by line looking for any source file that need to be included
		*					for the project. It relys on several other defs that pars the names for the files from the tcl
		*					syntax used used in the qip files. Additionally it flags nested QIP files. nested quip files will
		*					cause an error because the script currently does not support it. 
		* 
		* dependantcies:	This def is dependant on the up.filesDictionary being preloaded with the file types it should be looking
		*					for. Additionally it needs sub defs to pars the name of the file from the tcl syntax.
		'''	
		def readQip(up, file):
			logging.debug("def: readQip")
			for line in file:
				for fileType in up.filesDictionary:
					if fileType in line:
						line = up.parsFileNameFromQip(fileType, line)
						line = up.checkForParentDir(line)
						if ("../" in line):
							line = os.path.basename(line)
							line = up.findFile(line)
							if(line == False):
								logging.debug("could not find the file in the qip removing it from list")
								break
							line = line.lstrip("./")
						up.fileList.append(line)
						if(fileType == 'QIP_FILE'):
							logging.debug("found qip file. qip flag set true")
							up.nestedQuip = True
						logging.debug("found file: " + str(line))
						break
		
		'''
		* def name:			checkForParentDir
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def parses the parent directory of the file found in the QIP. If the file is in the project
		*					directory it will return "/"
		* 
		* dependantcies:	the name of the quip file needs to be passed in as line.
		'''	
		def checkForParentDir(up, line):
			logging.debug("def: checkForParentDir")
			if(up.quipParentDirectory != '/'):
				if(up.quipParentDirectory == line[:len(up.quipParentDirectory)]):
					return line
				else:
					return up.quipParentDirectory + line
			else:
				return line
		
		'''
		* def name:			parsFileNameFromQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def parses the name of the file called by the qip from the tcl syntax. It does this by deleting
		*					the surounding tcl syntax.
		* 
		* dependantcies:	The file type and line of tcl code need to be passed to this def. The file tupe is the tag that the
		*					qip uses to tag what type of file it is. The line is the full line of text that comes form the sip file
		'''	
		def parsFileNameFromQip(up, fileType, line):
			logging.debug("def: parsFileNameFromQip")
			line = re.sub("\n", "", line)
			if(line.find('$::quartus(qip_path)') == -1):
				line = up.parsFileNameFromQsf(fileType, line)
			else:
				line = line[line.find('$::quartus(qip_path)')+22:]
				if '"]' in line:
					line = re.sub('"]', '', line)
				if '\n' in line:
					line = re.sub('\n', '', line)
			line = re.sub("\n", "", line)
			line = re.sub(" ", "", line)
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
						#print "qsys :", re.sub('.qsys', '', qsysFile)
						#print "qip  :", re.sub('.qip', '', qipFile)
						if (os.path.basename(re.sub('.qsys', '', qsysFile)) == os.path.basename(re.sub('.qip', '', qipFile))):
							#print "match"
							logging.debug("removing " + qipFile + " from qipList")
							up.qipList.remove(qipFile)
						#print "\n"
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
					logging.debug("ERROR: Failed to find IP file in the directory: " + qipFile)
			if(failedFlag == True):
				logging.debug("ERROR: error upgrading IP")
		
		def checkForUpgradInEditor(up):
			logging.debug("def: checkForUpgradInEditor")
			if not up.qipList:
				logging.debug("no quip files to be checked.")
				up.lastSuc = True
				return
			for file in up.qipList:
				try:
					up.parsQuipParent(file)
					logging.debug("opening file: " + str(file))
					file = open(file, "r")
					logging.debug('file opened successfully')
					for line in file:
						if("IP_TOOL_VERSION" in line):
							line = up.parsQipVersion(line)
							logging.debug("Found QIP version for " + str(file) + " " + str(line))
					logging.debug('closing qip file')
					file.close()
					up.lastSuc = True
				except:
					logging.debug("ERROR: failed to open qip file")
					up.lastSuc = False
		
		def parsQipVersion(up, line):
			line = line[line.find('IP_TOOL_VERSION "')+17:]
			if('"' in line):
				line = re.sub('"', '', line)
			if('\n' in line):
				line = re.sub('\n', '', line)
			return line
		
		'''
		* def name:			checkForReadMe
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def finds any files that could be directions or read me files in the project.
		*					To do this it searches for different file types.
		* 
		* dependantcies:	This def is dependant on the up.nonQuartusFileList to be populated with different
		*					file exensions that could be read me files. example .docx, .txt, .pdf, ect.
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
		* description:		This def is the final check of the files list before it is written to the
		*					filelist.txt file. This file checks for violations by comparing to list to
		*					the up.excludeDictionary list. If any of the file list items match they are
		*					removed from the list.
		* 
		* dependantcies:	This is dependant on having the up.excludeDictionary list populated with any
		*					files that need to not be included in the file list.
		'''	
		def checkFileList(up):
			logging.debug("def: checkFileList")
			up.fileList = list(set(up.fileList)) #remove duplicate files in file list
			for line in up.fileList:
				for exclude in up.excludeDictionary:
					if(exclude in str(line)):
						up.fileList.remove(line)
		
		'''
		* def name:			generateFileList
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def writes the filelist.txt from the up.filelist list. Additionally if
		*					the filelist.txt does not already exsist it creates the file. If for some 
		*					reason this def fails it will cause the sript to error out and exit.
		* 
		* dependantcies:	Before this is run all the files that need to be archived need to be included
		*					in the up.filelist list.
		'''	
		def generateFileList(up):
			logging.debug("def: generateFileList")
			try:
				file = open("filelist.txt", "w")
				for line in up.fileList:
					file.write(str(line) + '\n')
				file.close()
				logging.debug("successfully wrote filelist.txt")
				print "successfully wrote filelist.txt"
				up.lastSuc = True
			except:
				logging.debug("ERROR: failed to write filelist.txt")
				print "failed to write filelist.txt"
				up.lastSuc = False
		
		'''
		* def name:			archive
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def launches the command that archives the project using the fileist.txt
		*					The command syntax is sotred in the inital of the class to make the script
		*					esier to edit. 
		* 
		* dependantcies:	This is dependant on the filelist.txt containing all files that need to be
		*					packaged into the archive file. Additionally, this def is dependant on the
		*					up.archiveComand containg the proper syntax to initiate the archive process
		*					in the quartus shell.
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
				logging.debug("ERROR: error archived project")
				logging.debug("error message: " + str(testExcept))
				up.lastSuc = False
	
		'''
		* def name:			createTestDirectory
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def creates a directory with the name from the string up.testDirName.
		*					The name is stored in up.testDirName to make editing the scirpt easier for
		*					users.
		* 
		* dependantcies:	This definithinon is dependant on up.testDirName being populated with a string
		*					that is legal for the name of a direrectory.
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
				logging.debug("ERROR: failed to create test directory")
				up.lastSuc = False
		
		'''
		* def name:			copyArchive
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def copies the archive file created by the scirpt to the test directory.
		*					It does this by using the cp command in unix. If the name of the name of the
		*					archive file or the test directory is changed this up.copyArchiveCommand also
		*					needs to be updated.
		* 
		* dependantcies:	This def is dependant on using a Unix system because it uses the cd command.
		*					Additionally, this def is dependant on up.copyArchiveCommand being initialised.
		*					with a string that contains the cd command. The command is initialised in the
		*					initial of the class.
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
				logging.debug("ERROR: copping archive file to test directory")
				up.lastSuc = False
		
		'''
		* def name:			extractArchiveFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def extracts the upgraded archive file in the test directory. It does
		*					this by using the platform install comand in the quartus shell.
		* 
		* dependantcies:	This def is dependant on the up.extracParCommand containing a string that
		*					uses the platform install command from the quartus shell. Additionally this
		*					def is dependant on the archive file beeing in the test directory and the
		*					current wroking drectory being the test directory.
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
				logging.debug("ERROR: extracting archive file")
				up.lastSuc = False
		
		'''
		* def name:			compileProject
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def compiles the extracted upgraded archive file generated by the
		*					script. It does this using the quartus shell flow command. If the 
		*					compilation is succeful the upgrade is considered a succes.
		* 
		* dependantcies:	This def is dependant on the up.compileCommand beeing initialled with
		*					a string that contains the quartus shell flow command. Additionally,
		*					the current working directory needs to be the test directory wehre the
		*					upgraded arcive file was extracted.
		'''	
		def compileProject(up):
			logging.debug("def: compileProject")
			try:
				print "compiling test project"
				logging.debug("compiling test project")
				up.cmdOut = subprocess.check_output(up.compileCommand, shell=True)
				#print up.cmdOut
				#logging.debug(up.cmdOut)
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "Error compiling test project"
				logging.debug("ERROR: compiling test project")
				up.lastSuc = False
		
	runClass = upgradeClass()

	
def multiUpgrade(mainDir):
	print "Multiple upgrade initiating in: ", mainDir
	
	class multipleClass:
		def __init__(mult):
			mult.initDirectoryList = []
			mult.lastSuc = False
			mult.postDirectoryList = []
			mult.multMainDef()
		
		'''
		* def name:			multMainDef
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is the main for the multi upgrade prcesses. All of the def calls
		*					for the multipleClass happen here. Additionally any return logic due to 
		*					an error take place here.
		* 
		* dependantcies:	The only dependantcies for this def is the data sturcture for the class
		*					that it utilises to call all sub defs.
		'''
		def multMainDef(mult):
			print "Finding PAR files"
			mult.getFilesList()
			mult.removeNonPar()
			if(len(mult.initDirectoryList) < 1):
				print "no par files found"
				return
			print "Creating folders for projects"
			mult.makeDirAndMoveFiles()
			if(mult.lastSuc == False):
				return
			print "Launching upgrades"
			mult.launchUpgrades()
		
		'''
		* def name:			getFilesList
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def creates a list of all sub directories in the mainDir if there are any
		* 
		* dependantcies:	Is populated with the file path the user intends to use.
		'''
		def getFilesList(mult):
			for x in os.listdir('.'):
				mult.initDirectoryList.append(x)
		
		
		'''
		* def name:			removeNonPar
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def iterates all the files found in the mult.initDirectoryList list
		*					and removes any files that do not end with the .par extention.
		* 
		* dependantcies:	This is dependant on the mult.initDirectoryList containing the list of
		*					all files and or directories in the main directory passed to the class
		*					by the user arguments.
		'''
		def removeNonPar(mult):
			for file in mult.initDirectoryList:
				if(".par" not in file):
					mult.initDirectoryList.remove(file)
		
		'''
		* def name:			makeDirAndMoveFiles
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def moves the par files into individual folders for upgrading.
		*					To do this the def creates a file with the same name as the par with
		*					a number after it. Additionally, this def moves the par file into its
		*					individual file.
		* 
		* dependantcies:	This is def is dependant on the mult.initDirectoryList containing only
		*					par files. Additionally, the user running the script needs to have read
		*					and write privlages in the main directory passed to the script. Last,
		*					this def is dependant on using the os python library.
		'''	
		def makeDirAndMoveFiles(mult):
			counter = 0
			for file in mult.initDirectoryList:
				try:
					os.makedirs(re.sub('.par', '', file) + str(counter))
					mult.postDirectoryList.append(re.sub('.par', '', file) + str(counter))
					os.rename(file, re.sub('.par', '', file) + str(counter) + "/" + file)
					mult.lastSuc = True
				except subprocess.CalledProcessError as errorCode:
					print "Error creating directory for: ", file
					mult.lastSuc = False
					return
				counter = counter + 1
	
		'''
		* def name:			makeDirAndMoveFiles
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def calls the upgrade
		* 
		* dependantcies:	This is def
		'''	
		def launchUpgrades(mult):
			for directory in mult.postDirectoryList:
				updateProcess((mainDir + "/" + directory), False)
	
	runMultClass = multipleClass()
	
	
	
'''
* def name:			main
* 
* creator:			Dustin Henderson
* 
* description:		This def recives all arcuments and commands from the comand line and parses
*					what class to run with the arguments parsed and passed to it. To accomplish
*					this the def uses the optparse.OptionParser() library from python.
* 
* dependantcies:	This def is dependant on the user fallowing the insturctions in the user guide.
'''
def main (argv):
	option_parser = optparse.OptionParser()

	option_parser.set_defaults(singleUpgradeOpt = None, multiUpgradeOpt = None, packageOpt = None)
	
	option_parser.add_option("-s", "--single_upgrade", dest="singleUpgradeOpt", action="store",
		help="This option will upgrade all the ip in a project")
	
	option_parser.add_option("-m", "--multiple_upgrade", dest="multiUpgradeOpt", action="store",
		help="This option will upgrade all the ip in a project")
		
	option_parser.add_option("-p", "--package", dest="packageOpt", action="store",
		help="This option will package a project into an arcive file that can be uploaded to the design store")
		
	options, args = option_parser.parse_args(argv)
	
	if options.singleUpgradeOpt != None:
		os.chdir(options.singleUpgradeOpt)
		updateProcess(mainDir = options.singleUpgradeOpt, packageBool = False)
		exit()
	
	if options.multiUpgradeOpt != None:
		os.chdir(options.multiUpgradeOpt)
		multiUpgrade(mainDir = options.multiUpgradeOpt)
		exit()
		
	if options.packageOpt != None:
		print "package feature coming soon"
		updateProcess(mainDir = options.packageOpt, packageBool = True)
		exit()
	
if __name__ == '__main__':
	running = main(sys.argv)
	sys.exit(running)