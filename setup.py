#!/usr/bin/env python
#
# sen2cor setup script
# 
# usage: 
# to build distribution for windows:
# 	'python setup.py sdist --formats=zip'
# else:
# 	'python setup.py sdist --formats=gztar'
# to install at target system:
#	'python setup.py install' and follow the instructions ...
#

from setuptools import setup, find_packages
from distutils.dir_util import mkpath, copy_tree
from distutils.file_util import copy_file
import os, sys, platform
import urllib
import zipfile, tarfile

name = 'sen2cor'
#
# This needs to be changed with each new version:
#------------------------------------------------
version = '2.0.5'
longVersion = '02.00.05'
#
# Do not change anything below:
#----------------------------------------------------------------------------
consoleScript1 = 'L2A_Process = sen2cor.L2A_Process:main'
consoleScript2 = 'L2A_Process-' + version + ' = sen2cor.L2A_Process:main'
consoleScript3 = 'L2A_Process-' + longVersion + ' = sen2cor.L2A_Process:main'

L2A_Process = 'L2A_Process'
L2A_Process_Version = L2A_Process + '-' + version

def copyConfiguration():
	sys.stdout.write('\nSEN2COR ' + version + ' setup script:\n')
	sys.stdout.write('This will finish the configuration of the environment settings.\n')
	user_input = raw_input('\nOK to continue? [y/n]: ')
	if user_input == 'n':
		return False
	
	cfgf = 'L2A_GIPP.xml'
	srcf = os.path.join(modulefolder, os.path.join('cfg', cfgf))
	SEN2COR_HOME = os.path.join(cfghome, 'sen2cor')
	break_condition = True
	while True:
		sys.stdout.write('\nPlease input a path for the sen2cor home directory:\n')
		sys.stdout.write('default is: ' + SEN2COR_HOME + '\n')
		user_input = raw_input('Is this OK? [y/n]: ')
		if user_input == 'n':
			SEN2COR_HOME = raw_input('New path: ')
			sys.stdout.write('New path is: ' + SEN2COR_HOME +'\n')
			user_input = raw_input('Is this OK? [y/n]: ')
			if user_input == 'y':
				break_condition = True
			else:
				break_condition = False
		else:
			break_condition = True

		if break_condition == True:
			os.environ['SEN2COR_HOME'] = SEN2COR_HOME
			s2l2appcfg = os.path.join(SEN2COR_HOME, 'cfg')
			mkpath(s2l2appcfg)
			copy_file(srcf, os.path.join(s2l2appcfg, cfgf))
			break

	sys.stdout.write('Setting environment for sen2cor ...\n')
	if system == 'Windows':
		# setting the environments for the application under Windows:
		try:
			path = os.environ['PATH']
			osgeo = sys.prefix + '\\Lib\\site-packages\osgeo'
			if ('osgeo' in path) == False:

				path = '"' + path + '";' + osgeo
				setPath = 'setx PATH ' + path
				sys.stdout.write('Adding GDAL binaries to PATH:')
				os.system(setPath)
			setGDAL_DATA = 'setx GDAL_DATA ' + osgeo + '\\data\\gdal'
			sys.stdout.write('Setting environment variable GDAL_DATA:')
			os.system(setGDAL_DATA)
			setSEN2COR_HOME = 'setx SEN2COR_HOME ' + SEN2COR_HOME
			sys.stdout.write('Setting environment variable SEN2COR_HOME:')
			os.system(setSEN2COR_HOME)
			setSEN2COR_BIN = 'setx SEN2COR_BIN ' + modulefolder
			sys.stdout.write('Setting environment variable SEN2COR_BIN:')
			os.system(setSEN2COR_BIN)
		except:
			sys.stderr.write('Error in environment settings!\n')
			return False
		sys.stdout.write('Congratulations, you are done!\n')
	else:
		# setting the environments for the application into L2A_Bashrc (Linux and MacOSX):
		L2A_Bashrc = '#!/usr/bin/env bash\n'
		L2A_Bashrc += '# BEGIN\n'
		L2A_Bashrc += '# Sen2Cor environmental setup, version ' + version +'\n'
		L2A_Bashrc += '# settings automatically generated by setup.py\n'
		L2A_Bashrc += '# source this script either manually via: "source L2A_Bashrc"\n'
		L2A_Bashrc += '# or call it from your .bashrc or .profile script\n#\n'
		if system == 'Darwin':
			L2A_Bashrc += 'export LC_ALL=en_US.UTF-8\n'
			L2A_Bashrc += 'export LANG=en_US.UTF-8\n'
		L2A_Bashrc += 'export SEN2COR_HOME=' + SEN2COR_HOME + '\n'
		L2A_Bashrc += 'export SEN2COR_BIN=' + modulefolder + '\n'
		gdaldata = sys.prefix + '/share/gdal'
		L2A_Bashrc += 'export GDAL_DATA=' + gdaldata + '\n'
		L2A_Bashrc += '# END\n'
		sys.stdout.write('Creating L2A_Bashrc script under:\n' + SEN2COR_HOME + '\n')
		try:
			textFile = open(SEN2COR_HOME + '/L2A_Bashrc', 'w')
			textFile.write(L2A_Bashrc)
			textFile.close()
		except:
			sys.stderr.write('Cannot create the L2A_Bashrc script under:\n' + SEN2COR_HOME + '\n')
			return False
		# creating the L2A_Process.bash script:
		CONDA_BIN = sys.prefix + '/bin'
		L2A_Process_bash = '#!/usr/bin/env bash\n'
		L2A_Process_bash += '# BEGIN\n'
		L2A_Process_bash += '# Sen2Cor L2A_Process.bash, version ' + version +'\n'
		L2A_Process_bash += '# settings automatically generated by setup.py\n#\n'
		L2A_Process_bash += 'export PATH=' + CONDA_BIN + ':$PATH\n'
		L2A_Process_bash += 'source ./L2A_Bashrc\n'
		L2A_Process_bash += 'L2A_Process-$1 $2 $3 $4\n'
		L2A_Process_bash += '# END\n'
		sys.stdout.write('Creating L2A_Process.bash script under:\n' + SEN2COR_HOME + '\n')
		try:
			textFile = open(SEN2COR_HOME + '/L2A_Process.bash', 'w')
			textFile.write(L2A_Process_bash)
			textFile.close()
		except:
			sys.stderr.write('Cannot create the L2A_Process.bash script under:\n' + SEN2COR_HOME + '\n')
			return False
		# create the glymur configuration file for OpenJPEG2:
		glymurrc = '[library]\n'
		glymurrc += 'openjp2: ' + libOpj2Target + '\n'
		glymurrcPath = os.path.join(cfghome, '.config/glymur')
		glymurrcFile = os.path.join(glymurrcPath, 'glymurrc')
		sys.stdout.write('Creating the configuration file for OpenJPEG2 under:\n' + glymurrcPath + '\n\n')
		try:
			mkpath(glymurrcPath)
		except:
			sys.stdout.write('Path already exists ...')
		try:
			textFile = open(glymurrcFile, 'w')
			textFile.write(glymurrc)
			textFile.close()
		except:
			sys.stderr.write('Cannot create the configuration file for OpenJPEG2 under:\n ' + glymurrcPath + '\n\n')
			return False
	
		sys.stdout.write('Congratulations, you are nearly done ...\n')
		sys.stdout.write('Last step: cd to ' + SEN2COR_HOME + ',\n')
		sys.stdout.write('source the <L2A_Bashrc> script either manually via: "source L2A_Bashrc"\n')
		sys.stdout.write('or integrate this call in your .bashrc or .profile script. Afterwards,\n')

	sys.stdout.write('- you can call the processor from everywhere via: "L2A_Process"\n')
	sys.stdout.write('- you will find the default configuration called "L2A_GIPP.xml" under:\n' + s2l2appcfg + '\n\n')		
	return True

setup(
	name = name,
	version = version,
	description = 'sen2cor: Sentinel 2 Level 2A Prototype Processor',
	long_description = open('README.md').read(),
	author = 'Telespazio VEGA Deutschland GmbH',
	author_email = 'sen2cor@telespazio-vega.de',
	url = 'www.telespazio-vega.de',
	packages = ['sen2cor'],
	include_package_data = True,
	platforms=['linux-x86_64', 'macosx-10.5-x86_64', 'win-amd64'],
	entry_points={
		'console_scripts' : [consoleScript1, consoleScript2, consoleScript3,]
	},
	zip_safe = False,
)

try:
	sys.argv[1] == True
except:
	sys.stderr.write('argument must either be "sdist" or "install ..."\n')
	sys.exit(0)
if (sys.argv[1] != 'install'):
	sys.exit(0)

system = platform.system()
if system == 'Darwin':
	cmdstr = 'conda install --yes gdal=1.11.2'
	prefix = sys.prefix + '/lib/python2.7/site-packages'
	modulefolder = prefix + '/' + name + '-' + version + '-py2.7.egg/sen2cor'
	buildfolder = modulefolder + '/build'
	platform = '/lib.macosx-10.5-x86_64-2.7'
	libopj2 = '/libopenjp2.dylib'
	libAtmCor = '/L2A_AtmCorr.so'
	targetfolder = sys.prefix + '/lib'
	try:
		cfghome =  os.environ['XDG_CONFIG_HOME']
	except:
		cfghome = os.environ['HOME']
elif system == 'Linux':
	cmdstr = 'conda install --yes gdal=1.11.2'
	prefix = sys.prefix + '/lib/python2.7/site-packages'
	modulefolder = prefix + '/' + name + '-' + version + '-py2.7.egg/sen2cor'
	buildfolder = modulefolder + '/build'
	platform = '/lib.linux-x86_64-2.7'
	libopj2 = '/libopenjp2.so'
	libAtmCor = '/L2A_AtmCorr.so'
	targetfolder = sys.prefix + '/lib'
	try:
		cfghome =  os.environ['XDG_CONFIG_HOME']
	except:
		cfghome = os.environ['HOME']
elif system == 'Windows':
	cmdstr = 'conda install --yes gdal=1.11.1'
	prefix = sys.prefix + '\\Lib\\site-packages'
	modulefolder = prefix + '\\' + name + '-' + version + '-py2.7.egg\\sen2cor'
	buildfolder = modulefolder + '\\build'
	platform = '\\lib.win-amd64-2.7'
	libopj2 = '\\openjp2.dll'
	libAtmCor = '\\L2A_AtmCorr.pyd'
	targetfolder = sys.prefix + '\\Scripts'
	cfghome =  os.environ['USERPROFILE'] + '\\documents'

os.system(cmdstr)
os.system('conda install --yes --channel https://conda.binstar.org/s2tbx proj4')
os.system('conda install --yes --channel https://conda.binstar.org/s2tbx contextlib2')
os.system('conda install --yes --channel https://conda.binstar.org/s2tbx glymur')
os.system('conda update --yes --channel https://conda.binstar.org/s2tbx pytables')

# better to do this manually, see SUM section uninstall:
#os.system('conda clean --yes --tarballs --index-cache --packages --source-cache')

libOpj2Source = buildfolder + platform + libopj2
libAtmSource = buildfolder + platform + libAtmCor
libOpj2Target = targetfolder + libopj2
libAtmTarget = modulefolder + libAtmCor
copy_file(libOpj2Source, libOpj2Target)
copy_file(libAtmSource, libAtmTarget)
if copyConfiguration() == True:
	sys.stdout.write('Installation sucessfully performed.\n')
else:
	sys.stdout.write('Errors during installation occurred.\n')
sys.exit(0)

if __name__ == '__main__':
	pass
