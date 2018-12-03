#design store automated upgrade script
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
scriptDir = os.getcwd()
print "script directory: ", scriptDir

'''*********************************************************************************************'''
'''**  Main upgrade class                                                                      *'''
'''** Description: 	This class is used to upgrade existing project from the design store      *'''
'''** 				archived in a .par extension. Almost all variables passed from one def to    *'''
'''**				to another are initialed or instantiated in the ___init___ def of the class*'''
'''** 				See the developer section of the documentation to see how to edit this     *'''
'''** 				variables to update, change, or fix the functionality of the script*		   *'''
'''**                                                                                          *'''
'''** Dependencies: This class is dependant on having the main directory parsed and passed to  *'''
'''** 				The main directory needs to point to the directory containing the par fill *'''
'''** 				that needs to be upgraded.												   *'''
'''*********************************************************************************************'''
def updateProcess(mainDir, packageBool=False):
	logging.basicConfig(filename=(mainDir+'/LOGOUT.log'),level=logging.DEBUG)
	logging.debug("------------------------------------------------------------------------------")
	logging.debug("def: updateProcess")
	logging.debug("------------------------------------------------------------------------------")
	print "------------------------------------------------------------------------------"
	print "								STARTING INFO"
	print "------------------------------------------------------------------------------"
	print "Main Directory:\t", mainDir
	logging.debug("Main Directory:\t" + mainDir)

	class upgradeClass:
		
		
		def __init__(up):
			'''****************'''
			'''initiate logging'''
			'''****************'''
			print("Logging File: " + mainDir + '/LOGOUT.log')
			logging.debug("def: main")
			
			'''****************'''
			'''*testing flags *'''
			'''****************'''
			up.testingParser = False	#disables extracting par upgrading ip and testing the newly created file if set to to True
			
			'''****************'''
			'''**** flags *****'''
			'''****************'''
			up.lastSuc = False			#this bool is used to tell if the last function that was run was successful
			up.foundQpf = False			#this bool is used to tell if a qpf was found in the main directory
			up.foundPar = False			#this bool is used to tell if there is a par in the main directory
			up.foundQip = False			#bool used to flag if there is qip files in the project
			up.nestedQip = False		#this bool flags if there is a qip file called in a qip file (currently not supported by the script)
			up.qsysFlag = False			#this bool is used to indicate whether or not a qsys file is found in the project directory
			up.blanketUpGrade = False	#this bool is used to indicate if the blanket upgrade was successful.
			up.repairQsfBool = False

			up.foundIp = False          #this bool is used to tell if there is an ip file in the main directory
			up.foundSip = False			#this bool is used to tell if there is an sip file in the main directory

			up.foundFailedUpgrade = False
			
			'''****************'''
			'''generated lists '''
			'''****************'''
			up.qipList = []											#stores a list of all the qip files. populated after the qsf is parsed
			up.directoryList = []									#This list stores every directory in the directory passed to the script
			up.qsysFiles = []										#
			up.fileList = ['platform_setup.tcl', 'filelist.txt']	#this list stores all the files that will be written to the file list.txt used for archiving the project
			up.repairQsfLines = [] #2d

			up.ipList = []
			up.sipList = []
			
			'''****************'''
			'''** user lists **'''
			'''****************'''
			#list of the tags used in the settings file for files that need to be included in the file list
			up.filesDictionary = ["SYSTEMVERILOG_FILE", "QIP_FILE", "SOURCE_FILE", "VHDL_FILE", "SDC_FILE", "VERILOG_FILE", "EDA_TEST_BENCH_FILE", "TCL_SCRIPT_FILE", "QSYS_FILE", "USE_SIGNALTAP_FILE", "SIGNALTAP_FILE", "SLD_FILE", "MISC_FILE", "BDF_FILE", "SIP_FILE", "IP_FILE"] #Aaron Added "IP_FILE" & "SIP_FILE"
			# up.excludeDictionary = {".qprs", ".qsf", ".qpf", "None", ".BAK."}	#This list is all the file typse and strings that are not allowed in the file list. If they are found in the fileList they will be removed.
			up.excludeDictionary = {".qprs", ".qsf", ".qpf", "None", ".BAK.", ".stp"}  # This list is all the file typse and strings that are not allowed in the file list. If they are found in the fileList they will be removed.
			up.nonQuartusFileList = ["txt", "doc", "docx", "xls", "xlsx", "pdf", "zip", "tar.gz", "gz"]#This list stores all file types that are possibly documentation or read me file in the project directory.
			# up.masterImageFileTypes = ["sof", "pof", "elf", "iso", ".hex", "c", "cpp", "h", "sdc"]		#***TODO:*** add hex files for memory configuration
			up.masterImageFileTypes = ["sof", "pof", "elf", "iso", "hex", "c", "cpp", "h", "sdc", "mif"]  # ***TODO:*** add hex files for memory configuration
			'''****************'''
			'''** user names **'''
			'''****************'''
			# up.qpfFileName = "top"				#stores the name of the quartus project file
			# up.qsfFileName = "top.qsf" 			#currently not detected just hard set stores the name of the quartus setting file
			# up.testDirName = 'testDirectory'	#this string stores the name of the directory that will be created to test the upgraded project. It needs to be a legal dir name and unique

			# Aaron Added
			up.qpfFileName = ""  # stores the name of the quartus project file
			up.qsfFileName = up.qpfFileName + ".qsf"  # currently not detected just hard set stores the name of the quartus setting file
			up.testDirName = 'testDirectory'  # this string stores the name of the directory that will be created to test the upgraded project. It needs to be a legal dir name and unique

			up.parFilename = ""
			up.updateParFilename = False

			up.quartusVer = ""
			up.quartusVerType = ""

			# up.upgradedQarFile = up.parFilename + "_q_" + up.quartusVer.replace(".","_") + up.quartusVerType + ".qar"
			up.upgradedQarFile = ""

			'''****************'''
			'''generated names '''
			'''****************'''
			# up.projName = ""			#this string is used to store the name of the project
			up.packageBool = packageBool#sets the package bool
			up.mainDir = mainDir		#set the main directory the same as the one passed in to the class this is used to store the location of the
			up.qsfFile = ''				#string stores the name of the project qsf file
			up.qipParentDirectory = ''	#This string is used to store the directory a qip file that is beeing parsed is stored in
			up.cmdOut = ""				#this sting sotres output of the cmd after a comand is run


			'''****************'''
			'''*** Commands ***'''
			'''****************'''
			#example qextract syntax
			#"quartus_sh --platform_install -package audio_monitor.par; quartus_sh --platform -name audio_monitor -search_path \."
			up.extractParCommand = "" # will get filled in when the name is detected
			#the three
			up.extractParCommand1 = "quartus_sh --platform_install -package "	#part one of the extract command
			up.extractParCommand2 = "; quartus_sh --platform -name " 			#part two of the extract command
			up.extractParCommand3 = " -search_path \."							#part three of the extract command
			# up.archiveCommand = "quartus_sh --archive -input filelist.txt -output upgrade.qar"	#This string is the archive command used to package the upgraded project
			up.archiveCommand = "quartus_sh --archive -input filelist.txt -output " # This string is the archive command used to package the upgraded project
			up.updateIpCommand = "quartus_sh --ip_upgrade -mode all "			#the command used to complete the blanket upgrade
			# up.copyArchiveCommand = "cp upgrade.qar " + up.testDirName + "/upgrade.qar"	#This sting stores the command for coping upgraded archive file to the test directory
			# up.extractArchiveCommand = "quartus_sh --platform -name upgrade.qar"#this string contains the command to extract the archived project created by the script
			# up.copyArchiveCommand = "cp upgrade.qar " + up.testDirName + "/upgrade.qar"  # This sting stores the command for coping upgraded archive file to the test directory
			up.extractArchiveCommand = "quartus_sh --platform -name upgrade.qar"  # this string contains the command to extract the archived project created by the script
			up.compileCommand = "quartus_sh --flow compile top.qpf"				#this string contains the command for compiling the upgraded project in the test directory


			up.getQuartusVersion()

			print "------------------------------------------------------------------------------"
			print "							STARTING PACKAGER/UPGRADE"
			print "------------------------------------------------------------------------------"
		
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
		* def name:			getQuartusVersion
		*
		* creator:			Dustin Henderson
		*
		* description:		This is the main def for packaging projects this def only calls other defs used to package projects.
		*					no upgrade happens during this process. The packager works biased off the same parsers that are used
		*					to find and package the files in the upgrade process.
		*
		* dependencies:	Dependant on the up data structure containing the defs responsible for parsing files from the project
		'''

		def getQuartusVersion(up):
			# Gets the Quartus Version
			up.quartusVer = subprocess.check_output("which quartus", shell=True)
			logging.debug(up.quartusVer)
			up.quartusVer = up.quartusVer.split("/")
			up.quartusVer = up.quartusVer[3]
			if "std" in up.quartusVer:
				up.quartusVerType = " std"
			else:
				up.quartusVerType = " pro"
			up.quartusVer = up.quartusVer.replace("std", "")
			print "Quartus Version: ", up.quartusVer, up.quartusVerType

		
		'''
		* def name:			packagerMain
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This is the main def for packaging projects this def only calls other defs used to package projects.
		*					no upgrade happens during this process. The packager works biased off the same parsers that are used
		*					to find and package the files in the upgrade process.
		* 
		* dependencies:	Dependant on the up data structure containing the defs responsible for parsing files from the project
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
						# print "Failed to open qsf file"
						# logging.debug("Failed to open qsf file")
						return
					up.lastSuc = False			
					up.parsQsf()
					if(up.lastSuc == False):
						# print "Failed to parse qsf file"
						# logging.debug("Failed to parse qsf file")
						return
					up.closeQsfFile()
					up.lastSuc = False
					up.openQsfFile()
					if(up.lastSuc == False):
						# print "Failed to open qsf file"
						# logging.debug("Failed to open qsf file")
						return
					up.createPlatformSetUpFile()
					up.closeQsfFile()
					up.findQsysFiles()
					up.findMasterImage()
					up.lastSuc = False
					up.parsQips()
					if(up.lastSuc == False):
						# print "Failed to parse qip files"
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

					if up.updateParFilename :
						print ""
						print "Please update the updated qar's filename before uploading to the design store"
						print "Current updated qar filename: " + up.upgradedQarFile
						print "The name should be in like so:"
						print "\t<product family>_<project title>_q_<Quartus Version>_<Quartus Type>.qar"
						print "\tEx: C10_nios_hello_world_q_18_0_std.qar"
					return
				else:
					print "Did not find or found too many qpf(s) in the project"
					return
		
		'''
		* def name:			classMain
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is the main for the upgrade class
		* 
		* dependencies:	This def is only dependant on the class existing and all variables 
		*					in the classes being initialised. Also this def should be called 
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
				up.nestedQip = False
				up.qipParentDirectory = ''
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
			up.checkForUpgradeInEditor()

			# Aaron Added (Check for all upgraded ip)
			if (up.lastSuc == False):
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

			if up.updateParFilename:
				print ""
				print "Please update the updated qar's filename before uploading to the design store"
				print "Current updated qar filename: " + up.upgradedQarFile
				print "The name should be in like so:"
				print "\t<product family>_<project title>_q_<Quartus Version>_<Quartus Type>.qar"
				print "\tEx: C10_nios_hello_world_q_18_0_std.qar"
		
		'''
		* def name:			checkDir
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def checks that the entered directory exists and is not a specific file
		* 
		* dependencies:	up.mainDir is populated with the file path the user intends to use.
		'''
		def checkDir(up):
			logging.debug("def: checkDir")
			if(os.path.isdir(up.mainDir) == False):
				print "given path is not a directory"
				logging.debug("ERROR: given path is not a directory")
				up.lastSuc = False
				return
			if(os.path.exists(up.mainDir) == False):
				print "given path does not exist"
				logging.debug("ERROR: given path does not exist")
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
		* dependencies:	up.mainDir is populated with the file path the user intends to use.
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
				logging.debug("Found more than one par file")
				print "Found more than one par file"
				for par_file in projectList:
					print "\t" + up.mainDir + "/" + par_file
					logging.debug("\t" + up.mainDir + "/" + par_file)
				return
			if(len(projectList) == 1):
				up.foundPar = True
				# up.projName = projectList[0]
				if not("_q_" in projectList[0]):
					up.parFilename = projectList[0]
					up.parFilename = up.parFilename.split(".")
					up.parFilename = up.parFilename[0]
					up.upgradedQarFile = up.parFilename + "_q_" + up.quartusVer.replace(".", "_") + up.quartusVerType.replace(" ", "_") + ".qar"
					up.updateParFilename = True
				else:
					# Need to test
					up.parFilename = projectList[0]
					up.parFilename = up.parFilename.split("_q_")
					up.parFilename = up.parFilename[0]
					up.upgradedQarFile = up.parFilename + "_q_" + up.quartusVer.replace(".","_") + up.quartusVerType.replace(" ", "_") + ".qar"

			projectList = up.findAllFilesOfType("qpf")
			if(len(projectList) > 1):
				logging.debug("Found more than one qpf file")
				print "Found more than one qpf file"
				for qpf_file in projectList:
					print "\t" + up.mainDir + "/" + qpf_file
					logging.debug("\t" + up.mainDir + "/" + qpf_file)
				return
			if(len(projectList) == 1):
				up.lastSuc = False
				up.foundQpf = True
				# up.projName = projectList[0]
				# up.qpfFileName = projectList[0]
				# up.qpfFileName = up.qpfFileName.split(".")
				# up.qpfFileName = up.qpfFileName[0]



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
		* dependencies:	mainDir must be a valid directory containing a par file. 
		'''
		def extractPar(up):
			logging.debug("def: extractPar")
			logging.debug("Changing directory to " + mainDir)
			os.chdir(mainDir)
			# up.extractParCommand = up.extractParCommand1+ up.projName + up.extractParCommand2 + re.sub('.par', '', up.projName) + up.extractParCommand3
			up.extractParCommand = up.extractParCommand1 + up.parFilename + ".par" + up.extractParCommand2 + up.parFilename + up.extractParCommand3
			logging.debug("command: " + str(up.extractParCommand))
			print "command: " + str(up.extractParCommand)
			print "extracting par file"
			try:
				up.cmdOut = subprocess.check_output(up.extractParCommand, shell=True)
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
		* dependencies:	up.mainDir is populated with the file path the user intends to use. The qsysFlag
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
		* description:		This Def is responsible for finding the master image files that are often included in 
		*					design examples. It uses a list of file extensions to find completed synthesis files.
		*					for example the most common master image file is an sof file. The file extensions are
		*					listed at the top of the script in the initial block for easy editing.
		* 
		* dependencies:	up.masterImageFileTypes needs to be an initialised list containing the file extensions
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
		* dependencies:		The command for this def is sorted in the initial as up.updateIpCommand. It's initialised
		*					there for easy future editing.
		'''		
		def upgradeIp(up):
			logging.debug("def: upgradeIp")
			try:
				# up.cmdOut = subprocess.check_output((up.updateIpCommand + up.qpfFileName), shell=True)
				# logging.debug("updated IP successfully")
				# print "updated IP successfully"
				up.blanketUpGrade = False
			except subprocess.CalledProcessError as testExcept:
				logging.debug("WARNING: upgrading IP with blanket statement will try individual files")
				logging.debug("WARNING message: " + str(testExcept))
				up.blanketUpGrade = False
		
		'''
		* def name:			openQsfFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def opens the qsf file in order for it to be parsed. If it fails to open for any reason
		*					it will set the up.lastSuc to false
		*
		* dependencies:		up.lastsuc is a bool used to indicate failure to open the file
		'''	
		def openQsfFile(up):
			logging.debug("def: openQsfFile")
			projectList = up.findAllFilesOfType("qpf")
			up.qpfFileName = projectList[0]
			up.qpfFileName = up.qpfFileName.split(".")
			up.qpfFileName = up.qpfFileName[0]
			up.qsfFileName = up.qpfFileName + ".qsf"
			try: 
				print "opening qsf file"
				logging.debug("opening qsf file: " + up.qsfFileName)
				# print "project name: ", up.projName
				print "project name: ", up.qpfFileName
				up.qsfFile = open(up.qsfFileName, "r")
				up.lastSuc = True
			except:
				# logging.debug("ERROR: failed to open qsf file: " + up.projName)
				logging.debug("ERROR: failed to open qsf file: " + up.qpfFileName)
				print "failed to open qsf file"
				up.lastSuc = False
				
		'''
		* def name:			createPlatformSetUpFile
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def uses the open qsf file and copies the contents into the platform_setup tcl file
		*					the def also adds proc ::setup_project{}{ to the beginning of the file and the closing }
		*					at the end of the file.
		*
		* dependencies:		This module depends on the up.qsfFile = open(qsfFile r) being executed starting at the
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
		* description:		This module is responsible for finding any files used by the project and appending them
		*					to the project files list. It works by reading the tcl syntax in the qsf file. In the 
		*					init of the class there is a dictionary of filetypes the parser looks for. This dictionary
		*					is used to identify qip, verilog, vhdl, and ect files that need to be included in the filelist.
		*
		* dependencies:		The initial of the class needs to include a dictionary pre populated with the file types the
		*					parser needs to Identify. Additionally, parsFileNameFromQip def needs to exist and return
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
							logging.debug("WARNING: Bad QSF syntax found")
							line = up.repairQsf(line)
							if(line == False):
								up.lastSuc = False
								return
						# line = up.parsFileNameFromQsf(fileType, line)
						filename = up.parsFileNameFromQsf(fileType, line)
						# up.fileList.append(line)
						# if(fileType == 'QIP_FILE'):
						# 	logging.debug("found qip file. qip flag set true")
						# 	up.foundQip = True
						# 	up.qipList.append(line)
						# if(fileType == 'QSYS_FILE'):
						# 	logging.debug("found qsys file in qsf. setting qsys flag to true")
						# 	up.qsysFlag = True #qsys flag
						# 	up.qsysFiles.append(line) #added it to qsys list
						# if(fileType == "IP_FILE"): # Aaron Added
						# 	logging.debug("found ip file in qsf. setting ip flag to true")
						# 	logging.debug("filetype = ", fileType)
						# 	up.foundIp = True
						# 	up.ipList.append(line)
						# logging.debug("found file: " + line)
						# break
						up.fileList.append(filename)
						if (fileType == 'QIP_FILE'):
							logging.debug("found qip file. qip flag set true")
							up.foundQip = True
							up.qipList.append(filename)
						if (fileType == 'QSYS_FILE'):
							logging.debug("found qsys file in qsf. setting qsys flag to true")
							up.qsysFlag = True  # qsys flag
							up.qsysFiles.append(filename)  # added it to qsys list
						if (fileType == "SIP_FILE"): # Aaron Added
							logging.debug("found sip file in qsf")
							up.foundSip = True
							up.sipList.append(filename)
						elif (fileType == "IP_FILE"):  # Aaron Added # elif due to name conflict with sip/qip file
							logging.debug("found ip file in qsf. setting ip flag to true")
							# logging.debug("filetype = " + fileType)
							up.foundIp = True
							up.ipList.append(filename)
						logging.debug("found file: " + filename)
						break

			for file in up.qsysFiles:
				# print "File in Qsysfile
				if "/" in file:
					file = file.split("/")
					qsys_file = up.getQsysFiles(file[-1])
				else:
					qsys_file = up.getQsysFiles(file)
			up.lastSuc = True

			for file in up.ipList:
				# print "File in Qsysfile
				# if "." in file:
				# 	file = file.split(".")
				# 	qsys_file = up.getIPFiles(file[0])
				# else:
				# 	qsys_file = up.getIPFiles(file)

				qsys_file = up.getIPFiles(file)

			for file in up.sipList:
				up.fileList.append(file)
			up.lastSuc = True

				
		'''
		* def name:			parsFileNameFromQsf
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def parses the location and name from a line of tcl code in the qsf file. The def
		*					can only accept one line of code at a time.
		*
		* dependencies:		Only one line of tcl code at a time (passed in as a string) as line. fileType needs to be
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
		* description:		This def attempts to repair any broken qsf syntax. Occasionally, files will be
		*					included in the project that are outside of the project directory. This causes
		*					a .. in front of the file. However when the project is archived the file is
		*					is moved into the project directory. After this happens the project will not
		*					be able to find the file. This def finds the file in the project directory.
		*					then it fixes the broken line in the qsf.
		*
		* dependencies:	
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
		* dependencies:	This def is dependant on the working directory set to directory you would like to search
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
		* dependencies:	the up.qsfFile needed to the the project qsf file opened
		'''	
		def closeQsfFile(up):
			logging.debug("def: closeQsfFile")
			up.qsfFile.close()

		'''
		* def name:			getQsysFiles
		*
		* creator:			Aaron Arenas
		*
		* description:		This def takes in a qsys file and searches for every file in the
		*					qsys directory. The result/output is a list with every file's
		*					filepath with respect to the qsys directory
		*
		* dependencies:		This def is dependant the qsys file and qsys directory existing
		'''

		def getQsysFiles(up, qsys_filename):
			logging.debug("Def: getQsysFiles")
			# qsys_files = []
			qsys_files_w_path = []
			qsys_filename_list = qsys_filename.split(".")
			qsys_dir = qsys_filename_list[0]
			file_types = []
			try:
				# Check if qsys_dir exist
				if (os.path.isdir(qsys_dir) == False):
					print "\tQsys file directory doesn't exist: " + qsys_dir
					print "\tMay need to generate IP first"
					logging.debug("\tQsys file directory doesn't exist: " + qsys_dir)
					logging.debug("\t\tqsys_filename = " + qsys_filename)
					logging.debug("\tMay need to generate IP first")
					return
			except:
				print "getQsysFiles failed: qsys directory doesn't exist"
				return

			try:
				# Walk inside qsys_dir to search for files
				for root, directories, filenames in os.walk(qsys_dir):
				# for root, directories, filenames in os.walk(up.mainDir):
					# if "platform" in root:
					# 	continue
					# if qsys_dir in root:
					# for i in range(0, len(directories)):
					# 	directories[i] = up.mainDir + "/" + directories[i]
					#
					# for directory in directories:
					# 	for sub_root, sub_directories, sub_filenames in os.walk(directory):
					# 		if len(sub_directories):
					# 			break
					#
					# 		for i in range(0, len(sub_directories)):
					# 			directories.append(directory + "/" + sub_directories[i])
					#
					# 		if qsys_dir in sub_directories:

					for filename in filenames:

						# Searches for Filetypes inside of qsys_dir
						# To-do: check which filetypes are needed
						filename_split_list = filename.split(".")
						file_type = filename_split_list[1]
						if not (file_type in file_types):
							file_types.append(file_type)

						# # Gets filename only inside qsys_dir and subdirectories
						# qsys_files.append(filename)
						# print filename

						# # Gets filename with path inside qsys_dir
						filename_path = os.path.join(root, filename)
						# qsys_files_w_path.append(filename_path)
						up.fileList.append(filename_path)
					# break
						# print filename_path

					# # Prints file types (could delete)
					# print "\nFile Types\n"
					# for file_type in file_types:
					# 	print file_type
					# print "\n"

					# return qsys_files_w_path

			except:
				print "getQsysFiles failed: Unable to walk in Qsys directory"
				return

		'''
		* def name:			getIPFiles
		*
		* creator:			Aaron Arenas
		*
		* description:		This def takes in a ip file (w/ path) and searches for every file in the
		*					ip's directory. The result/output is a list with every file's
		*					filepath with respect to the ip's directory
		*
		* dependencies:		This def is dependant the ip file and ip's directory existing
		'''

		def getIPFiles(up, ip_filename):
			logging.debug("Def: getIPFiles")
			# qsys_files = []
			ip_files_w_path = []
			ip_filename_list = ip_filename.split(".")
			ip_dir = ip_filename_list[0]
			file_types = []
			try:
				# Check if qsys_dir exist
				if (os.path.isdir(ip_dir) == False):
					print "\tIP file directory doesn't exist: " + ip_dir
					print "\tMay need to generate IP first"
					logging.debug("\tIP file directory doesn't exist: " + ip_dir)
					logging.debug("\t\tip_filename = " + ip_filename)
					logging.debug("\tMay need to generate IP first")
					return
			except:
				print "getIPFiles failed: ip's directory doesn't exist"
				return

			try:
				# Walk inside ip_dir to search for files
				for root, directories, filenames in os.walk(ip_dir):
					# for root, directories, filenames in os.walk(up.mainDir):
					# if "platform" in root:
					# 	continue
					# if qsys_dir in root:
					# for i in range(0, len(directories)):
					# 	directories[i] = up.mainDir + "/" + directories[i]
					#
					# for directory in directories:
					# 	for sub_root, sub_directories, sub_filenames in os.walk(directory):
					# 		if len(sub_directories):
					# 			break
					#
					# 		for i in range(0, len(sub_directories)):
					# 			directories.append(directory + "/" + sub_directories[i])
					#
					# 		if qsys_dir in sub_directories:

					for filename in filenames:

						# Searches for Filetypes inside of qsys_dir
						# To-do: check which filetypes are needed
						filename_split_list = filename.split(".")
						file_type = filename_split_list[1]
						if not (file_type in file_types):
							file_types.append(file_type)

						# # Gets filename only inside qsys_dir and subdirectories
						# qsys_files.append(filename)
						# print filename

						# # Gets filename with path inside qsys_dir
						filename_path = os.path.join(root, filename)
						# qsys_files_w_path.append(filename_path)
						up.fileList.append(filename_path)
					# break
					# print filename_path

					# # Prints file types (could delete)
					# print "\nFile Types\n"
					# for file_type in file_types:
					# 	print file_type
					# print "\n"

					# return qsys_files_w_path

			except:
				print "getIPFiles failed: Unable to walk in IP's directory"
				return


		'''
		* def name:			parsQips
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This module parses any qip found in the qsf file for files that need to be included for ip.
		*					It runs thought each file in the list. This def also calls another def to identify the parent
		*					directory of the file parsed from the qip file.
		*
		* dependencies:	up.qipList needs to contain anny qip files used by the project. 
		'''	
		def parsQips(up):
			logging.debug("def: parsQips")
			for file in up.qipList:
				logging.debug("qipList item: " + str(file))
			if not up.qipList:
				logging.debug("no qip files returning lastSuc True")
				up.lastSuc = True
				return
			for file in up.qipList:
				try:
					up.parsQipParent(file)
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
		* def name:			parsQipParent
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is responsible for identifying the parent directory of the files contained in the qip.
		*					If the qip file is in the project directory this def will return "/"
		* 
		* dependencies:		this def requires that the name of the qip file be passed into it.
		'''	
		def parsQipParent(up, file):
			logging.debug("def: parsQipParent")
			print os.path.dirname(file) + '/'
			up.qipParentDirectory = os.path.dirname(file) + '/'
			logging.debug("qip parent: " + str(up.qipParentDirectory))
		
		'''
		* def name:			readQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		this def runs through the qip file line by line looking for any source file that need to be included
		*					for the project. It relies on several other defs that pars the names for the files from the tcl
		*					syntax used used in the qip files. Additionally it flags nested QIP files. nested qip files will
		*					cause an error because the script currently does not support it. 
		* 
		* dependencies:	This def is dependant on the up.filesDictionary being preloaded with the file types it should be looking
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
							up.nestedQip = True
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
		* dependencies:	the name of the qip file needs to be passed in as line.
		'''	
		def checkForParentDir(up, line):
			logging.debug("def: checkForParentDir")
			if(up.qipParentDirectory != '/'):
				if(up.qipParentDirectory == line[:len(up.qipParentDirectory)]):
					return line
				else:
					return up.qipParentDirectory + line
			else:
				return line
		
		'''
		* def name:			parsFileNameFromQip
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def parses the name of the file called by the qip from the tcl syntax. It does this by deleting
		*					the surrounding tcl syntax.
		* 
		* dependencies:		The file type and line of tcl code need to be passed to this def. The file type is the tag that the
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
		* description:		This def gets skipped if the blanket upgrade works (upgradeIp). If it is needed this
		*					def upgrades each piece of ip detected in the project one at a time. Ip in a project is
		*					detected by the presence of a qip file. Every qip file corresponds to a .qsys, .v, .vhd,
		*					or .sv file. The def starts by upgrading the qsys files in the up.qsysFiles list. While
		*					each file in the up.qsysFiles list is upgraded the file is removed from the up.qipList
		*					list. This prevents trying to upgrade the same file twice. Last the def locates the 
		*					corresponding hdl file to the qip file then runs the upgrade command. 
		*					Example:
		*						pll.qip => quartus_sh -ip_upgrade -variation_files pll.v top
		*						niosSys.qip => quartus_sh -ip_upgrade -variation_files niosSys.qip top
		* 
		* dependencies:		This def is dependant on up.qsysFiles and up.qipList. The up.qsysFiles needs to list
		*					all qsys files used by the project. the up.qipList needs to list all qip files used
		*					by the project.
		'''	
		def individualFileUpgrade(up):
			failedFlag = False
			updateCommand = ""
			logging.debug("def: individualFileUpgrade")
			logging.debug("qsysFlag status: " + str(up.qsysFlag))

			# listOutdatedIPCommand = "quartus_sh --ip_upgrade --list_ip_cores " + up.qpfFileName
			#
			# try:
			# 	up.cmdOut = subprocess.check_output(listOutdatedIPCommand, shell=True)
			# 	print up.cmdOut
			# except:
			# 	# failedFlag = True
			# 	logging.debug("Problem getting list of outdated IP's")
			# 	print "Problem getting list of outdated IP's"
			# # print "Need to manually upgrade Qsys file"


			if(up.qsysFlag == True):
				# for qipFile in up.qipList: # Original
				for qipFile in list(up.qipList): # Iterate over copy of list to make sure you look at all elements in list
					for qsysFile in up.qsysFiles:
						# print "qsysFile : " + qsysFile
						# print "qipFile : " + qipFile
						# print "re.sub('.qsys', '', qsysFile) :", re.sub('.qsys', '', qsysFile) # if "qsys" in filename, it will remove it (i.e. adc_qsys.qsys => adc)
						# print "re.sub('.qip', '', qipFile)  :", re.sub('.qip', '', qipFile)
						# print "os.path.basename(re.sub('.qsys', '', qsysFile)) :" + os.path.basename(re.sub('.qsys', '', qsysFile))
						# print "os.path.basename(re.sub('.qip', '', qipFile)) :" + os.path.basename(re.sub('.qip', '', qipFile))

						# Original
						# if (os.path.basename(re.sub('.qsys', '', qsysFile)) == os.path.basename(re.sub('.qip', '', qipFile))):
						# 	#print "match"
						# 	logging.debug("removing " + qipFile + " from qipList")
						# 	up.qipList.remove(qipFile)

						qsysFile_manual = qsysFile.split(".")
						qsysFile_manual = qsysFile_manual[0].split("/")
						qsysFile_manual = qsysFile_manual[-1]

						# print "qsysFile_manual : " + qsysFile_manual

						if(qsysFile_manual == re.sub('.qsys', '', qsysFile)):
							if (os.path.basename(re.sub('.qsys', '', qsysFile)) == os.path.basename(re.sub('.qip', '', qipFile))):
								#print "match"
								logging.debug("removing " + qipFile + " from qipList")
								up.qipList.remove(qipFile)
						else:
							logging.debug("Using manually extracted qsys filename")
							if (os.path.basename(qsysFile_manual) == os.path.basename(re.sub('.qip', '', qipFile))):
								# print "match"
								logging.debug("removing " + qipFile + " from qipList")
								up.qipList.remove(qipFile)
								#print "\n"

				up.numOfIPUpgrades = len(up.qsysFiles) + len(up.qipList) + len(up.ipList)
				up.currentIPUpgrade = 1
				print "Need to upgrade " + str(up.numOfIPUpgrades) + " IP's"

				for qsysFile in up.qsysFiles:
					# print "quartus_sh -ip_upgrade -variation_files " + qsysFile + " top"

					# Aaron Added
					updateCommand = "quartus_sh --ip_upgrade -variation_files " + qsysFile + " " + up.qpfFileName
					# print "quartus_sh -ip_upgrade -variation_files " + qsysFile + " " + up.qpfFileName

					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " top"

					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) +") Upgrading: " + qsysFile
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
						logging.debug("Problem upgrading " + qsysFile)
						print "Problem upgrading " + qsysFile + " (Need to manually upgrade)"
						# print "Need to manually upgrade Qsys file"
					up.currentIPUpgrade = up.currentIPUpgrade + 1


			for qipFile in up.qipList:
				if os.path.isfile(re.sub('.qip', '.v', qipFile)):
					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " top"
					# logging.debug("command: " + "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " top")
					# print updateCommand

					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.v', qipFile) + " " + up.qpfFileName
					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) + ") Upgrading: " + re.sub('.qip', '.v', qipFile)
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
						logging.debug("Problem upgrading " + re.sub('.qip', '.v', qipFile))
						print "Problem upgrading " + re.sub('.qip', '.v', qipFile)

				elif os.path.isfile(re.sub('.qip', '.vhd', qipFile)):
					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					# print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " top"
					# logging.debug("command: " + updateCommand)

					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhd', qipFile) + " " + up.qpfFileName
					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) + ") Upgrading: " + re.sub('.qip', '.vhd', qipFile)
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
						logging.debug("Problem upgrading " + re.sub('.qip', '.vhd', qipFile))
						print "Problem upgrading " + re.sub('.qip', '.vhd', qipFile)

				elif os.path.isfile(re.sub('.qip', '.vhdl', qipFile)):
					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					# print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " top"
					# logging.debug("command: " + updateCommand)

					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.vhdl', qipFile) + " " + up.qpfFileName
					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) + ") Upgrading: " + re.sub('.qip', '.vhdl', qipFile)
					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
						logging.debug("Problem upgrading " + re.sub('.qip', '.vhdl', qipFile))
						print "Problem upgrading " + re.sub('.qip', '.vhdl', qipFile)

				elif os.path.isfile(re.sub('.qip', '.sv', qipFile)):
					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"
					# logging.debug("command: " + "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top")
					# print "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " top"

					updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.qip', '.sv', qipFile) + " " + up.qpfFileName
					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) + ") Upgrading: " + re.sub('.qip', '.sv', qipFile)

					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						failedFlag = True
						logging.debug("Problem upgrading " + re.sub('.qip', '.sv', qipFile))
						print "Problem upgrading " + re.sub('.qip', '.sv', qipFile)
				else:
					print ("Failed to find IP file in the directory: " + qipFile)
					logging.debug("ERROR: Failed to find IP file in the directory: " + qipFile)
				up.currentIPUpgrade = up.currentIPUpgrade + 1

			if(up.foundIp == True):
				for ipFile in up.ipList:
					# print ipFile
					# updateCommand = "quartus_sh -ip_upgrade -variation_files " + re.sub('.ip', '.vhd', ipFile) + " top"
					updateCommand = "quartus_sh -ip_upgrade -variation_files " + ipFile + " " + up.qpfFileName
					# print "quartus_sh -ip_upgrade -variation_files " + re.sub('.ip', '.vhd', ipFile) + " top"
					logging.debug("command: " + updateCommand)
					# print updateCommand
					print "(" + str(up.currentIPUpgrade) + " of " + str(up.numOfIPUpgrades) + ") Upgrading: " + ipFile

					try:
						up.cmdOut = subprocess.check_output(updateCommand, shell=True)
					except:
						logging.debug("Failed to file .ip file: " + ipFile)
						failedFlag = True
					up.currentIPUpgrade = up.currentIPUpgrade + 1

			if(failedFlag == True):
				logging.debug("ERROR: error upgrading IP")
		
		def checkForUpgradeInEditor(up):
			logging.debug("def: checkForUpgradeInEditor")
			if not up.qipList:
				logging.debug("no qip files to be checked.")
				up.lastSuc = True
				return
			for file in up.qipList:
				try:
					up.parsQipParent(file)
					logging.debug("opening file: " + str(file))
					file = open(file, "r")
					logging.debug('file opened successfully')
					for line in file:
						if("IP_TOOL_VERSION" in line):
							# line = up.parsQipVersion(line) # original
							qipVersionOfLine = up.parsQipVersion(line)

							# logging.debug("Found QIP version for " + str(file) + " " + str(line)) # Original
							logging.debug("Found QIP version for " + str(file) + " " + str(qipVersionOfLine))

							#Aaron Added
							if (qipVersionOfLine != up.quartusVer):
								logging.debug("IP Verison (" + str(qipVersionOfLine) + ") not the same as Project Quartus Verison (" + str(up.quartusVer) + ")")
								logging.debug("IP: "+ str(line))
								logging.debug("Is that ok? (y/n)\nInput: ")
								print "IP Verison (" + str(qipVersionOfLine) + ") not the same as Project Quartus Verison (" + str(up.quartusVer) + ")"
								print "IP: "+ str(line)
								userResponse = raw_input("Is that ok? (y/n)\nInput: ")
								logging.debug("userResponse: '" + userResponse + "'")
								if userResponse == "y":
									up.foundFailedUpgrade = False
								else:
									up.foundFailedUpgrade = True
					logging.debug('closing qip file')
					file.close()

					if (up.foundFailedUpgrade == True):
						logging.debug("Found IP file(s) that were not upgraded")
						print "Found IP file(s) that were not upgraded"
						up.lastSuc = False
						# return
					else:
						up.lastSuc = True

					# Original
					# up.lastSuc = True

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
		* dependencies:	This def is dependant on the up.nonQuartusFileList to be populated with different
		*					file extensions that could be read me files. example .docx, .txt, .pdf, ect.
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
		* dependencies:	This is dependant on having the up.excludeDictionary list populated with any
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
		*					the filelist.txt does not already exist it creates the file. If for some 
		*					reason this def fails it will cause the script to error out and exit.
		* 
		* dependencies:	Before this is run all the files that need to be archived need to be included
		*					in the up.filelist list.
		'''	
		def generateFileList(up):
			logging.debug("def: generateFileList")
			try:
				file = open("filelist.txt", "w")

				# Added to generate sorted filelist
				up.fileList = sorted(up.fileList)


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
		* description:		This def launches the command that archives the project using the filelist.txt
		*					The command syntax is sorted in the initial of the class to make the script
		*					easier to edit. 
		* 
		* dependencies:	This is dependant on the filelist.txt containing all files that need to be
		*					packaged into the archive file. Additionally, this def is dependant on the
		*					up.archiveCommand containing the proper syntax to initiate the archive process
		*					in the quartus shell.
		'''	
		def archive(up):
			logging.debug("def: archive")

			up.archiveCommand = up.archiveCommand + up.upgradedQarFile

			logging.debug("command: " + str(up.archiveCommand))
			print "archiving project file"
			try:
				up.cmdOut = subprocess.check_output(up.archiveCommand, shell=True)
				logging.debug("extracted par successfully")
				print "archived project successfully"
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "error archiving project"
				# print "\tRemove upgrade.qar, upgrade.qarlog, and LOGOUT.log and try to re-package"

				# filelist.txt may have a file in it that doesn't exist and will not archive project
				# run up.archiveCommand and see what file is missing/causing the error
				print "Check filelist.txt and upgraded qarlog file to see which file(s) is missing"

				logging.debug("ERROR: error archived project")
				logging.debug("error message: " + str(testExcept))
				logging.debug("Check filelist.txt and upgraded qarlog file to see which file(s) is missing")

				up.lastSuc = False
	
		'''
		* def name:			createTestDirectory
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def creates a directory with the name from the string up.testDirName.
		*					The name is stored in up.testDirName to make editing the script easier for
		*					users.
		* 
		* dependencies:	This definition is dependant on up.testDirName being populated with a string
		*					that is legal for the name of a directory.
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
		* description:		This def copies the archive file created by the script to the test directory.
		*					It does this by using the cp command in unix. If the name of the name of the
		*					archive file or the test directory is changed this up.copyArchiveCommand also
		*					needs to be updated.
		* 
		* dependencies:	This def is dependant on using a Unix system because it uses the cd command.
		*					Additionally, this def is dependant on up.copyArchiveCommand being initialised.
		*					with a string that contains the cd command. The command is initialised in the
		*					initial of the class.
		'''	
		def copyArchive(up):
			logging.debug("def: copyArchive")
			up.copyArchiveCommand = "cp " + up.upgradedQarFile + " " + up.testDirName + "/" + up.upgradedQarFile
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
		*					this by using the platform install command in the quartus shell.
		* 
		* dependencies:	This def is dependant on the up.extractParCommand containing a string that
		*					uses the platform install command from the quartus shell. Additionally this
		*					def is dependant on the archive file being in the test directory and the
		*					current working directory being the test directory.
		'''	
		def extractArchiveFile(up):
			logging.debug("def: extractArchiveFile")
			up.extractArchiveCommand = "quartus_sh --platform -name " + up.upgradedQarFile
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
		*					compilation is successful the upgrade is considered a success.
		* 
		* dependencies:	This def is dependant on the up.compileCommand being initialled with
		*					a string that contains the quartus shell flow command. Additionally,
		*					the current working directory needs to be the test directory where the
		*					upgraded archive file was extracted.
		'''	
		def compileProject(up):
			logging.debug("def: compileProject")
			try:
				print "compiling test project"
				logging.debug("compiling test project")
				up.cmdOut = subprocess.check_output(up.compileCommand, shell=True)
				# print up.cmdOut
				# logging.debug(up.cmdOut)
				up.lastSuc = True
			except subprocess.CalledProcessError as testExcept:
				print "Error compiling test project"
				logging.debug("ERROR: compiling test project")
				# logging.debug(up.cmdOut)
				up.lastSuc = False



	runClass = upgradeClass()

	
def multiUpgrade(mainDir, scriptDir):
	print "Multiple upgrade initiating in: ", mainDir
	
	class multipleClass:
		def __init__(mult):
			mult.initDirectoryList = []
			mult.lastSuc = False
			mult.postDirectoryList = []
			mult.scriptDir = scriptDir	#this string stores the location of the python scirpt. This is saved so the script can call upon itself for mulit upgrade.
			print "script Directory ", mult.scriptDir
			logging.debug("script Directory " + mult.scriptDir)
			mult.multMainDef()
		
		'''
		* def name:			multMainDef
		* 
		* creator:			Dustin Henderson
		* 
		* description:		This def is the main for the multi upgrade processes. All of the def calls
		*					for the multipleClass happen here. Additionally any return logic due to 
		*					an error take place here.
		* 
		* dependencies:	The only dependencies for this def is the data structure for the class
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
		* dependencies:	Is populated with the file path the user intends to use.
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
		*					and removes any files that do not end with the .par extension.
		* 
		* dependencies:	This is dependant on the mult.initDirectoryList containing the list of
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
		* dependencies:	This is def is dependant on the mult.initDirectoryList containing only
		*					par files. Additionally, the user running the script needs to have read
		*					and write privileges in the main directory passed to the script. Last,
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
		* dependencies:	This is def
		'''	
		def launchUpgrades(mult):
			cmdOut = ""
			for directory in mult.postDirectoryList:
				#updateProcess((mainDir + "/" + directory), False)	#old comand that was causing logging problems
				print "Launching single upgrade on project found in the multi directory"
				print "It may take several minutes for the results to print..."
				print "launch command: " + "python " + mult.scriptDir + "/upgradeScript.py --single_upgrade=" + mainDir + "/" + directory
				cmdOut = subprocess.check_output("python " + mult.scriptDir + "/upgradeScript.py --single_upgrade=" + mainDir + "/" + directory, shell=True)
				print cmdOut
	
	runMultClass = multipleClass()
	
	
	
'''
* def name:			main
* 
* creator:			Dustin Henderson
* 
* description:		This def receives all arguments and commands from the command line and parses
*					what class to run with the arguments parsed and passed to it. To accomplish
*					this the def uses the optparse.OptionParser() library from python.
* 
* dependencies:	This def is dependant on the user fallowing the instructions in the user guide.
'''
def main (argv):
	option_parser = optparse.OptionParser()

	option_parser.set_defaults(singleUpgradeOpt = None, multiUpgradeOpt = None, packageOpt = None)
	
	option_parser.add_option("-s", "--single_upgrade", dest="singleUpgradeOpt", action="store",
		help="This option will upgrade all the ip in a project")
	
	option_parser.add_option("-m", "--multiple_upgrade", dest="multiUpgradeOpt", action="store",
		help="This option will upgrade all the ip in a project")
		
	option_parser.add_option("-p", "--package", dest="packageOpt", action="store",
		help="This option will package a project into an archive file that can be uploaded to the design store")
		
	options, args = option_parser.parse_args(argv)
	
	if options.singleUpgradeOpt != None:
		os.chdir(options.singleUpgradeOpt)
		updateProcess(mainDir = options.singleUpgradeOpt, packageBool = False)
		exit()
	
	if options.multiUpgradeOpt != None:
		os.chdir(options.multiUpgradeOpt)
		multiUpgrade(mainDir = options.multiUpgradeOpt, scriptDir = scriptDir)
		exit()
		
	if options.packageOpt != None:
		print "package feature coming soon"
		updateProcess(mainDir = options.packageOpt, packageBool = True)
		exit()
	
if __name__ == '__main__':
	running = main(sys.argv)
	sys.exit(running)