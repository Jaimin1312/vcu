''' Launch the Vision Control Unit (VCU) Test Application
'''
import sys
from util.gui import AppTemplate
from vcs.control.controller import ExecutorController
from vcs.model import application
import vcs.view.main

APPLICATION_TITLE = f"Symbotic Test Application v{application.VERSION} for {application.NRN_VPCB}"
DEFAULT_DIMENSIONS = (1400, 850)
ICON_PATH = 'assets/symbotic_logo.ico'

def main():
    """ Launch GUI utility

    Returns:
        int: return code where 0 indicated success
    """
    app = AppTemplate(APPLICATION_TITLE, DEFAULT_DIMENSIONS, ICON_PATH)
    view = vcs.view.main.MainLayout(app.root, mapper=application.MapperForVCUTest)
    controller = ExecutorController(app.root, view.update_handler, view.reset_handler)
    view.controller = controller
    app.root.mainloop()

    # close out the long-running background thread
    controller.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
