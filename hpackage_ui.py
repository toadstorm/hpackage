import os
import sys
import hpackagelib
import settings
from PySide2 import QtWidgets, QtGui, QtCore
import logging
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s -- %(levelname)s: %(message)s', level=logging.DEBUG, filename=os.path.join(os.path.expanduser("~"), "hpackage.log"), filemode="w", datefmt="%Y/%m/%d %H:%M:%S")

# TODO: if user doesn't want package files copied elsewhere, don't run shutil

class HPackageUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(HPackageUI, self).__init__(parent)
        self.setWindowTitle(settings.TITLE)

        logging.info("Initializing UI.")

        """ persistent widgets """
        prev_btn = QtWidgets.QPushButton("< Prev")
        next_btn = QtWidgets.QPushButton("Next >")
        finish_btn = QtWidgets.QPushButton("Finish")
        finish_btn.setVisible(False)
        prev_btn.setEnabled(False)

        """ intro dialog """
        intro_dialog = QtWidgets.QFrame()
        intro_layout = QtWidgets.QHBoxLayout()
        intro_dialog.setLayout(intro_layout)
        intro_image = QtGui.QImage(hpackagelib.get_resource(settings.IMAGE))
        intro_map = QtGui.QPixmap(intro_image)
        intro_label_image = QtWidgets.QLabel()
        intro_label_image.setPixmap(intro_map)
        intro_image_layout = QtWidgets.QVBoxLayout()
        intro_image_layout.addWidget(intro_label_image)
        intro_image_layout.addStretch()
        intro_layout.addLayout(intro_image_layout)
        intro_text_layout = QtWidgets.QVBoxLayout()
        intro_text = QtWidgets.QLabel(settings.INTRO)
        intro_text.setMaximumWidth(settings.LABELWIDTH)
        intro_text.setWordWrap(True)
        intro_text_layout.addWidget(intro_text)
        intro_text_layout.addStretch()
        intro_layout.addLayout(intro_text_layout)
        intro_layout.addStretch()

        """ configs dialog """
        configs_dialog = QtWidgets.QFrame()
        configs_layout = QtWidgets.QVBoxLayout()
        configs_dialog.setLayout(configs_layout)
        configs_text = QtWidgets.QLabel(settings.CHOOSER)
        configs_text.setMaximumWidth(settings.LABELWIDTH)
        configs_text.setWordWrap(True)
        configs_layout.addWidget(configs_text)
        # multilist for houdini installations
        configs_list = QtWidgets.QListWidget()
        configs_layout.addWidget(configs_list)

        """ destination dialog """
        dest_dialog = QtWidgets.QFrame()
        dest_layout = QtWidgets.QVBoxLayout()
        dest_dialog.setLayout(dest_layout)
        dest_label = QtWidgets.QLabel(settings.LOCATION)
        dest_label.setMaximumWidth(settings.LABELWIDTH)
        dest_label.setWordWrap(True)
        dest_layout.addWidget(dest_label)
        dest_chooser = QtWidgets.QLineEdit()
        # default path for installation is different if we're dealing with an exe with an embedded payload.
        try:
            payload_path = os.path.join(sys._MEIPASS, 'payload')
            # if this doesn't throw an exception, the payload is embedded
            default_path = os.path.join(os.path.expanduser("~"), settings.NAME)
        except Exception:
            default_path = hpackagelib.find_payload_path()
            if not default_path:
                default_path = os.path.join(os.path.expanduser("~"), settings.NAME)

        dest_chooser.setText(default_path)
        dest_btn = QtWidgets.QPushButton("...")
        dest_ctrl_layout = QtWidgets.QHBoxLayout()
        dest_ctrl_layout.addWidget(dest_chooser)
        dest_ctrl_layout.addWidget(dest_btn)
        dest_layout.addLayout(dest_ctrl_layout)
        dest_layout.addStretch()

        """ confirmation dialog """
        ok_dialog = QtWidgets.QFrame()
        ok_layout = QtWidgets.QVBoxLayout()
        ok_dialog.setLayout(ok_layout)
        confs_label = QtWidgets.QLabel("The package will be installed for the following Houdini configurations:")
        confs_label.setMaximumWidth((settings.LABELWIDTH))
        confs_label.setWordWrap(True)
        confs_list = QtWidgets.QListWidget()
        confs_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        ok_layout.addWidget(confs_label)
        ok_layout.addWidget(confs_list)
        dest_label = QtWidgets.QLabel("The package files will be installed to this location:")
        dest_path_label = QtWidgets.QLabel()
        ok_layout.addWidget(dest_label)
        ok_layout.addWidget(dest_path_label)
        conf_label = QtWidgets.QLabel("\nPress Next to complete the installation.")
        ok_layout.addStretch()
        ok_layout.addWidget(conf_label)

        """ result dialog """
        result_dialog = QtWidgets.QFrame()
        result_layout = QtWidgets.QHBoxLayout()
        result_image = QtWidgets.QLabel()
        result_image.setPixmap(intro_map)
        result_image_layout = QtWidgets.QVBoxLayout()
        result_image_layout.addWidget(result_image)
        result_image_layout.addStretch()
        result_layout.addLayout(result_image_layout)
        result_label_layout = QtWidgets.QVBoxLayout()
        result_label = QtWidgets.QLabel("The package has been successfully installed.")
        log_label = QtWidgets.QLabel("Installation log saved to: {}".format(os.path.join(os.path.expanduser("~"), "hpackage.log")))
        result_label.setMaximumWidth(settings.LABELWIDTH)
        result_label.setWordWrap(True)
        result_label_layout.addWidget(result_label)
        result_label_layout.addWidget(log_label)
        result_label_layout.addStretch()
        result_layout.addLayout(result_label_layout)
        result_layout.addStretch()
        result_dialog.setLayout(result_layout)

        """ persistent layouts """
        main_dialog = QtWidgets.QDialog()
        main_layout = QtWidgets.QVBoxLayout()
        main_dialog.setLayout(main_layout)
        btns_layout = QtWidgets.QHBoxLayout()
        btns_layout.addStretch()
        btns_layout.addWidget(prev_btn)
        btns_layout.addWidget(next_btn)
        btns_layout.addWidget(finish_btn)

        main_layout.addWidget(intro_dialog)
        main_layout.addWidget(configs_dialog)
        main_layout.addWidget(dest_dialog)
        main_layout.addWidget(ok_dialog)
        main_layout.addWidget(result_dialog)
        main_layout.addLayout(btns_layout)

        status = QtWidgets.QStatusBar()
        status.showMessage("HPackage developed by Henry Foster, www.toadstorm.com")
        self.setMinimumWidth(500)
        self.setStatusBar(status)

        self.setCentralWidget(main_dialog)

        dialogs = [intro_dialog, configs_dialog, dest_dialog, ok_dialog, ok_dialog, result_dialog]

        # persistent data
        self.data = {
            "state": 0,
            "aborted": False,
            "dialogs": dialogs,
            "default_path": default_path,
            "controls": {
                "prev": prev_btn,
                "next": next_btn,
                "finish": finish_btn,
                "configs": configs_list,
                "destination": dest_chooser,
                "confirmation": confs_list,
                "confirmation_dest": dest_path_label
            }
        }

        # signals/slots
        next_btn.clicked.connect(self.next_state)
        prev_btn.clicked.connect(self.prev_state)
        dest_btn.clicked.connect(self.pick_install_path)
        finish_btn.clicked.connect(self.success)

        self.refresh()

    def refresh(self):
        self.state_changed()
        self.get_configs()
        self.show()

    def next_state(self):
        self.data["state"] += 1
        self.state_changed()

    def prev_state(self):
        self.data["state"] -= 1
        self.state_changed()

    def state_changed(self):
        # hide all subdialogs
        for i in self.data["dialogs"]:
            i.setVisible(False)
        # show dialog matching current state
        self.data["dialogs"][self.data["state"]].setVisible(True)

        # enable/disable buttons
        if self.data["state"] == 0:
            self.data["controls"]["prev"].setEnabled(False)
        else:
            self.data["controls"]["prev"].setEnabled(True)
        if self.data["state"] == 2:
            pass
        if self.data["state"] == 3:
            self.load_confs_list()
            self.data["controls"]["confirmation_dest"].setText(self.data["controls"]["destination"].text())
        if self.data["state"] == 4:
            self.data["controls"]["prev"].setEnabled(False)
            self.data["controls"]["next"].setEnabled(False)
            self.do_install()
        if self.data["state"] == 5:
            self.data["controls"]["next"].setVisible(False)
            self.data["controls"]["prev"].setEnabled(False)
            self.data["controls"]["finish"].setVisible(True)
        self.adjustSize()

    def get_configs(self):
        # get all houdini config dirs.
        configs = hpackagelib.get_houdini_prefs_paths()
        # clear existing widget.
        widget = self.data["controls"]["configs"]
        widget.clear()
        for c in configs:
            item = QtWidgets.QListWidgetItem(str(c))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            widget.addItem(item)

    def pick_install_path(self):
        # get the path to install to from the user.
        default_path = self.data["controls"]["destination"].text()
        valid_path = False
        while not valid_path:
            new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose installation path...", default_path)
            # validate this path
            if new_path:
                if hpackagelib.is_valid_install_path(new_path.replace("\\", "/")):
                    valid_path = True
                    self.data["controls"]["destination"].setText(new_path)
                    logging.info("User selected installation path: {}".format(new_path))
                    break
                QtWidgets.QMessageBox.warning(self, "Invalid installation path!", "The installation path you specified is invalid. You may not install to existing Houdini preferences directories or to Houdini installation directories.", QtWidgets.QMessageBox.Ok)


    def get_selected_configs(self):
        # get all selected houdini configurations.
        configs = list()
        confs_widget = self.data["controls"]["configs"]
        for x in range(confs_widget.count()):
            if confs_widget.item(x).checkState() == QtCore.Qt.Checked:
                configs.append(confs_widget.item(x).text())
        return configs

    def load_confs_list(self):
        # populate the configurations list for confirmation.
        widget = self.data["controls"]["confirmation"]
        widget.clear()
        configs = self.get_selected_configs()
        for c in configs:
            widget.addItem(c)

    def get_user_payload_path(self):
        # if we can't find the payload relative to the current directory, prompt the user.
        msg = QtWidgets.QMessageBox.warning(self, "Package base directory not found!",
                                            "The installer was unable to find the base directory of the package you want to install. The base directory should at a minimum contain a directory called /otls/. Do you want to locate it manually?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                            QtWidgets.QMessageBox.No)
        if msg == QtWidgets.QMessageBox.StandardButton.Yes:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate package base directory...", os.path.dirname(__file__))
            if path:
                logging.info("User supplied payload directory: {}".format(path))
                if os.path.exists(path):
                    # test to make sure this is a package root
                    if not os.path.exists(os.path.join(path, "otls")):
                        logging.error("User supplied path does not have an otls directory.")
                        QtWidgets.QMessageBox.warning(self, "Package base directory has no otls directory!", "The package base directory you specified does not have an /otls/ subdirectory. Please verify the path and try again.", QtWidgets.QMessageBox.Ok)
                        return None
                    return path
                else:
                    logging.error("User supplied path is invalid.")
                    QtWidgets.QMessageBox.warning(self, "Package base directory does not exist!",
                                                  "The package base directory you specified does not exist. Please verify the path and try again.",
                                                  QtWidgets.QMessageBox.Ok)
                    return None

        else:
            logging.info("User aborted installation.")
            self.data["aborted"] = True
            return None

    def fail(self):
        # appears when installation has failed for whatever reason.
        ret = QtWidgets.QMessageBox.critical(self, "Installation failed!", "Installation failed. Please see the log at {} for details.".format(os.path.join(os.path.expanduser("~"), "hpackage.log")))
        app.quit()

    def success(self):
        # appears when normal installation is completed.
        # ret = QtWidgets.QMessageBox.information(self, "Installation complete", "Installation complete. See installation log at {} for details.".format(os.path.join(os.path.expanduser("~"), "hpackage.log")))
        app.quit()

    def do_install(self):
        configs = self.get_selected_configs()
        destination = self.data["controls"]["destination"].text()
        # if destination == self.data["default_path"]:
        #     destination = None
        package = hpackagelib.find_package_path()
        payload = hpackagelib.find_payload_path()
        # if we can't find the payload, we need to prompt the user.
        if not payload:
            logging.warning("Payload path not found. Prompting user for path.")
            while self.data["aborted"] is False and payload is None:
                payload = self.get_user_payload_path()
        if not payload:
            # fail the installation.
            logging.error("Installation failed!")
            self.fail()
        try:
            hpackagelib.install_package(configs, package=package, destination=destination, payload=payload, debug=settings.DEBUG)
        except Exception:
            logging.error("Unexpected error during installation!")
            logging.error(traceback.format_exc())
            self.fail()
        self.next_state()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = HPackageUI()
    app.exec_()
