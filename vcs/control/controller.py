''' Controller used by the test executive
'''
import os
import shutil
import threading
import time
import traceback

from util import power_supply
from util import timing
from util.fsm import FSM
from util.threading import BackgroundWorkerGeneric
from vcs.model import application
from vcs.model import camera
from vcs.model import images
from vcs.model import log
from vcs.model import report
from vcs.model import vcu
from vcs.model.bgstates import BGStates
from vcs.model.equipment import Equipment
from vcs.model.resources import VCSResources
from vcs.model.session import Session


EXPECTED_NUMBER_OF_IMAGES = 8
fsm = FSM() # instance of finite state machine definition


class ExecutorController():
    """ Business logic for Test Executor.
    """
    DWELL_STANDARD = .1
    def __init__(self, parent, update, final):
        self.worker = BackgroundWorkerGeneric(parent, update, final, func=self._main)

        #TODO: Update to use two state machines, one for state, one for step.
        #NOTE: states --> IDLE, RUNNING, CANCELLING, WAITING
        #NOTE: steps --> SETUP, CONNECTING, CAPTURE, ANALYSIS, CLEANUP, ERROR
        #NOTE: Perhaps FSM could have a _state_lock, self.state
        #NOTE: states FSM would eliminate need for self.running, self._cancelled.
        #NOTE: If the running state was separate from step, no need to track previous
        #   state and response could be made to be an input rather than something that is stored.
        #NOTE: In new model, state handlers don't deal with transitions internally.
        self.running = False
        self.state = BGStates.IDLE
        self._previous_state = BGStates.IDLE
        self._response = None

        self._cancelled = False
        self._equipment = None
        self._state_lock = threading.Lock()

        self.camera_position_lookup = {}
        self._session: Session = Session()
        self._enable_transaction_log = False

        self.worker.start()


    def _main(self):
        self.running = True
        while self.running:
            if self.state not in fsm.handlers:
                raise NotImplementedError(f'Support for {self.state} not added yet!')

            try:
                fsm.handlers[self.state](self)
            except Exception:                               #pylint: disable=broad-except
                self._log(f"An error has occurred: {traceback.format_exc()}")
                try:
                    self.system.cleanup()
                except Exception:                           #pylint: disable=broad-except
                    pass
                self._update_state(BGStates.IDLE)


    def shutdown(self):
        """ Stop the running background worker.

        Intended for use when the program is executing as it helps cancel
        any current loops as well.
        """
        self._cancelled = True
        self.running = False


    def abort(self):
        """ Aborts the current process and sets the next state to ABORT.

        The ABORT state is useful in handling and specific cleanup actions
        needed by front or back end.
        """
        self._cancelled = True
        self._update_state(BGStates.ABORT)


    def start(self, resources: VCSResources):
        """ Starts the Camera Test procedure on the background worker thread.

        Args:
            resources (dict): a set of equipment and parameters passed by the UI
                for use on BG thread.
        """
        if self.state == BGStates.IDLE:
            self._session = Session()
            self._enable_transaction_log = resources.enable_transaction_log
            self._response = None
            self._vcresources = resources
            self._set_resources(resources)
            self._cancelled = False
            self._update_state(BGStates.SETUP)


    def resume(self, value):
        """ Restarts the background process after it has been paused to wait on user input.

        Args:
            value (object): the answer form the UI in response to a request issued from the
                backend.  Requests are issued using the self._request() method.
        """
        if self.state == BGStates.WAITING:
            self._response = value
            self._update_state(self._previous_state)


    def open_logging_dir(self):
        """ Opens logging directory in file explorer.
        """
        path = application.settings.values.logging_path
        if not os.path.exists(path):
            os.makedirs(path)
        os.system(f'start "VCS Logs" "{path}"')
        self._log(f"Opening logging directory: {path}")


    def update_baseline_images(self, path):
        """ Updates the baseline images with those from a provided directory.

        Args:
            path (str): path to directory to pull new baseline images from.
        """
        if path:
            image_list = [os.path.join(path, i) for i in os.listdir(path) if i.endswith(".png")]

            if len(image_list) >= EXPECTED_NUMBER_OF_IMAGES:
                self._log(f"Updated baseline images with those from {path}")
                # Delete destination contents
                for oldfile in os.listdir(images.PATH_TO_BASELINES):
                    os.remove(os.path.join(images.PATH_TO_BASELINES, oldfile))

                # Copy images from source
                for image in image_list:
                    shutil.copy2(
                        image,
                        os.path.join(
                            images.PATH_TO_BASELINES,
                            os.path.basename(image))
                    )

            else:
                self._log(
                    f"{path} does not have the expected {EXPECTED_NUMBER_OF_IMAGES} images!")


    def _ask(self, statement: str, question: str):
        """ Issue a request to answer a yes/no question to the user via the messaging queue.

        The User Interface will display this (usually as a dialog box with a Yes/No buttons)

        Args:
            statement (str): text to use as the header in a dialog box provided by the UI.
            question (str): Yes/No question and additional details to provide the user.
        """
        self._update_state(BGStates.WAITING)
        self.worker.queue.put({'ask':(statement, question)})


    def _prompt(self, statement: str, details: str):
        """ Issue an alert to the user via the messaging queue.

        The User Interface will display this (usually as a dialog box with a Ok/Canel buttons)

        Args:
            statement (str): text to use as the header in a dialog box provided by the UI.
            details (str): additional details that may prove useful to the user.
        """
        self._update_state(BGStates.WAITING)
        self.worker.queue.put({'prompt':(statement, details)})


    @property
    def system(self) -> Equipment:
        """ Accessor for the euipment

        Returns:
            _type_: _description_
        """
        return self._equipment


    @property
    def _batch_dir(self) -> str:
        assert self._session.timestamp is not None, "Timestamp not set before usage!"
        return log.batch_dir(application.settings.values.logging_path, self._session.timestamp)

    def _set_resources(self, resources: VCSResources):
        try:
            vcu_instance = vcu.VCU(resources.deserializer_lookup)
            self._equipment = Equipment(resources, vcu_instance)
        except Exception as err:                            #pylint: disable=broad-except
            self._equipment = None
            self._log(f'Error!  An issue occured while trying to update resources: {err}')
            raise


    def _update_state(self, target):
        log.logging.info(f"Step: {target}")
        self.worker.queue.put({
            'state':target,
        })
        with self._state_lock:
            self._previous_state = self.state
            self.state = target


    def _log(self, msg, newline=True):
        log.logging.info(msg)
        self.worker.queue.put({'msg':(msg,newline)})


    def _display_camera_images(self):
        self.worker.queue.put(
            {'cameras':self._equipment.camera_list}
        )


    def _mark_camera(self, status, index):
        if status is not None:
            if status:
                self.worker.queue.put(
                    {'pass':index}
                )
            else:
                self.worker.queue.put(
                    {'fail':index}
                )


    @fsm.state_handler(BGStates.IDLE)
    def _state_idle(self):
        """ Handler for the IDLE state waits for next state input.
        """
        time.sleep(self.DWELL_STANDARD)


    @fsm.state_handler(BGStates.WAITING)
    def _state_waiting(self):
        """ Handler for the WAITING state waits for resume
        """
        time.sleep(self.DWELL_STANDARD)


    @fsm.state_handler(BGStates.SETUP)
    def _state_setup(self):
        """ Setup the equipment used to interact with the VCU:
                * Power Supply
                * DHCP Server (optional?)
                *
        """
        self._session.start()
        log.open_log(self._batch_dir)
        log.makedirs(self._batch_dir)
        if self._response is None or self._response is True:
            try:
                self.system.setup()
            except power_supply.NoSupply:
                self._prompt(
                    'Unable to detect a power supply!',
                    'Check that a power supply is powered on and connected to the system and try again.',   #pylint: disable=line-too-long
                )
                return
            self._update_state(BGStates.CONNECTING)
            self._response = None
        else:
            self._update_state(BGStates.ABORT)
            self._log("Unable to setup system; cancelling operation.")


    @fsm.state_handler(BGStates.CONNECTING)
    def _state_connecting(self):
        self.system.enable_supply()

        # Wait for IP address?
        time.sleep(1)
        self._log('    Establishing connection', newline=True)
        self._log(application.settings.values.vcu_hostname, newline=True)
        self._log(application.settings.values.vcu_password)

        timer = timing.Timer()
        timer.start()
        for _ in range(20):
            self._log('.', newline=False)
            try:
                self.system.vcu.connect()
                self._log(' done')
                break
            except Exception:                             #pylint: disable=broad-except
                time.sleep(1)
        timer.stop()
        self._log('', newline=True)
        if _ < 18:
            boot_time = self.system.vcu.get_boot_time()
            self._log(f"    Boot time:\t{boot_time}\tPASS")
            self._log(f"    Connect time:\t{timer.total_in_minutes_and_seconds}\tPASS")
            self._session.add_section_details('boot time', boot_time)
            self._session.add_section_details('connect time', timer.total_in_minutes_and_seconds)
# 10/6/22, SL, toggle comment for next state: VERSION_CHECK | CAMERA_CHECK
#        self._update_state(BGStates.VERSION_CHECK)
            self._update_state(BGStates.CAMERA_CHECK)
        else:
            self._log("    Boot time:       FAIL")
            self._log("    Connect time:    FAIL")
            self._update_state(BGStates.REVIEW)


    @fsm.state_handler(BGStates.VERSION_CHECK)
    def _state_version_check(self):
        hashes, server_version = self.system.vcu.software_version_check()

        self._log("    Hashes:")
        for key, value in hashes.items():
            self._log(f"        {key+':': <30} {value}")
        self._log(f"    Server Version: {server_version}")

        self._session.add_section_details(
            'version check', {
                'hashes':hashes,
                'server version':server_version,
            }
        )
        self._update_state(BGStates.CAMERA_CHECK)


    @fsm.state_handler(BGStates.CAMERA_CHECK)
    def _state_camera_presence_check(self):
        self.camera_position_lookup = self.system.vcu.generate_camera_position_lookup()

        for key, value in self.camera_position_lookup.items():
            self._log(f"    Camera {key+1} == Device {value}")

# 10/7/22, SL, output FAIL for incorrect camera count.
        if len(self.camera_position_lookup) == 8:
            self._log(f"    Camera detection count:    {len(self.camera_position_lookup)} / {EXPECTED_NUMBER_OF_IMAGES}    PASS")
        else:
            self._log(f"    Camera detection count:    {len(self.camera_position_lookup)} / {EXPECTED_NUMBER_OF_IMAGES}    FAIL")

        self._session.add_section_details(
            'camera check', {
                'camera position lookup':self.camera_position_lookup,
            }
        )
        self._update_state(BGStates.THERMAL_CHECK)


    @fsm.state_handler(BGStates.THERMAL_CHECK)
    def _state_thermal_check(self):
        temperatures = self.system.vcu.get_thermal_data()

        for key, value in temperatures.items():
            self._log(f"    {key+':':<20} {value:.2f}")

        self._session.add_section_details(
            'thermal check', {
                'temperatures':temperatures,
            }
        )
# 10/6/22, SL, toggle comment for next state: ACQUIRE_IMAGES | REVIEW
        self._update_state(BGStates.ACQUIRE_IMAGES)
#        self._update_state(BGStates.REVIEW)

    @fsm.state_handler(BGStates.ACQUIRE_IMAGES)
    def _state_acquire_images(self):
        self.system.vcu.acquire_images(self._batch_dir)
        camera.assign_images_to_cameras(
            self.system.camera_list, self._batch_dir, self.camera_position_lookup)
        self._display_camera_images()
# 10/6/22, SL, toggle comment for next state: PROCESS_IMAGES | REVIEW
#        self._update_state(BGStates.PROCESS_IMAGES)
        self._update_state(BGStates.REVIEW)


    @fsm.state_handler(BGStates.PROCESS_IMAGES)
    def _state_process_images(self):
        baselines = images.Baselines(images.PATH_TO_BASELINES)

        reports_from_all_cameras = {}
        for target_camera in self.system.camera_list:
            status, image_report = images.evaluate_camera_images(target_camera, baselines)
            reports_from_all_cameras[f"Camera {target_camera.index + 1}"] = image_report

            self._mark_camera(status, target_camera.index)
            self._log(target_camera.get_status_message())

            # Format and writout log files (Camera test only)
            if self._enable_transaction_log:
                assessment_report = report.CameraAssessmentReport(
                    target_camera.index, status, image_report)
                assessment_report.write(
                    log.get_transaction_log_path(
                        application.ITEM_NUM_VCAMENC,
                        target_camera.serial_number,
                        application.settings.values.logging_path,
                    )
                )

        self._session.add_section_details("process images", reports_from_all_cameras)
        self._update_state(BGStates.REVIEW)


    @fsm.state_handler(BGStates.REVIEW)
    def _state_review(self):
        self._update_state(BGStates.CLEANUP)


    @fsm.state_handler(BGStates.ABORT)
    def _state_abort(self):
        self._update_state(BGStates.CLEANUP)


    @fsm.state_handler(BGStates.CLEANUP)
    def _state_cleanup(self):
        total_time = self._session.stop()
        self._log(f'Total time: {total_time}')
        report.write(
            os.path.join(self._batch_dir, "measurements.log"),
            self._session.get_report(),
        )
        self.system.vcu.disconnect()
        self.system.cleanup()

        #NOTE: While this is where a log transfer would have originally
        #   occurred. Based on lack of connectivity to our network from the CM
        #   site, an explicit export model seems more appropriate. This means
        #   that, on request, the operator would click an option to export the
        #   the logging folder to something like an external thumb drive.

        self._update_state(BGStates.IDLE)
