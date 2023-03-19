"""Installation for Vision Control Unit Functional Test Application."""


import sys
from distutils.version import LooseVersion
import cx_Freeze
from vcs.model.application import COMPANY, PRODUCT, VERSION

MIN_CX_FREEZE_VERSION = '4.3.3'

if LooseVersion(cx_Freeze.version) < LooseVersion(MIN_CX_FREEZE_VERSION):
    print("Failed: cx_Freeze version 4.3.3 or higher is required.")
    sys.exit(-1)

PROGRAM = 'test_vcu'
NAME = COMPANY+' '+PRODUCT
REGISTRY_PATH = 'SOFTWARE\\'+COMPANY+'\\'+PRODUCT

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        'requests',
        'torch',
        'PIL',
        'imageio',
        'paramiko',
        'fabric',
        ],
    "include_files": [
        "assets",
        ],
    "excludes": [
        ],
    }


# Create a structure for the registry table
# This will create a value 'InstallDir' in the key
# 'HKEY_LOCAL_MACHINE\<SOFTWARE>\<application.COMPANY>\application.PRODUCT'
registry_table = [
    #('application.PRODUCTKeyLM',      2, REGISTRY_PATH,          '*',          None, 'TARGETDIR'),
    #('application.PRODUCTInstallDir', 2, REGISTRY_PATH, 'InstallDir', '[TARGETDIR]', 'TARGETDIR'),
    ]

# A RegLocator table to find the install directory registry key when upgrading
reg_locator_table = [('application.PRODUCTInstallDirLocate', 2, REGISTRY_PATH, 'InstallDir', 0)]

# An AppSearch entry so that the MSI will search for previous installs
# and update the default install location
app_search_table = [('TARGETDIR', 'application.PRODUCTInstallDirLocate')]

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ('DesktopShortcut',           # Shortcut
     'DesktopFolder',             # Directory_
     NAME,                        # Name
     'TARGETDIR',                 # Component_
     '[TARGETDIR]'+PROGRAM+'.exe',# Target
     None,                        # Arguments
     None,                        # Description
     None,                        # Hotkey
     None,                        # Icon
     None,                        # IconIndex
     None,                        # ShowCmd
     'TARGETDIR'                  # WkDir
    )
    ]

# Now create the table dictionary
msi_data = {
    'Registry': registry_table,
    'RegLocator': reg_locator_table,
    'AppSearch': app_search_table,
    "Shortcut": shortcut_table,
    }

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {
    'add_to_path': True,
    'upgrade_code': '{5E3880B7-74FF-4C3F-BFD8-DB8CE65ADB7A}',
    'initial_target_dir': '[ProgramFilesFolder]\\'+COMPANY+'\\'+PRODUCT,
    'data': msi_data,
    'install_icon':r'assets\symbotic_logo.ico',
    }

cx_Freeze.setup(
    name = NAME,
    description = 'Functional Test for the Vision Control Unit PCBA',
    author = COMPANY,
    version = VERSION,
    options = {
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
        },
    requires = [
        'cx_Freeze',
        'requests',
        ],
    executables = [
        cx_Freeze.Executable(
            PROGRAM+'.py',
            #base=None,
            base="Win32GUI",
            icon=r"assets\symbotic_logo.ico",
            ),
        ],
    )
