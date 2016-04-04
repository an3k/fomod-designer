#!/usr/bin/env python

# Copyright 2016 Daniel Nunes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PyQt5 import QtWidgets, QtGui
from .templates import mainframe as template


class MainFrame(QtWidgets.QMainWindow, template.Ui_MainWindow):
    def __init__(self):
        super(MainFrame, self).__init__()
        self.setupUi(self)

        icon_open = QtGui.QIcon()
        icon_open.addPixmap(QtGui.QPixmap("fomod/gui/logos/1456477639_file.png"),
                            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open.setIcon(icon_open)

        icon_save = QtGui.QIcon()
        icon_save.addPixmap(QtGui.QPixmap("fomod/gui/logos/1456477689_disc-floopy.png"),
                            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Save.setIcon(icon_save)

        icon_options = QtGui.QIcon()
        icon_options.addPixmap(QtGui.QPixmap("fomod/gui/logos/1456477700_configuration.png"),
                               QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionO_ptions.setIcon(icon_options)

        icon_refresh = QtGui.QIcon()
        icon_refresh.addPixmap(QtGui.QPixmap("fomod/gui/logos/1456477730_refresh.png"),
                               QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Refresh.setIcon(icon_refresh)

        icon_delete = QtGui.QIcon()
        icon_delete.addPixmap(QtGui.QPixmap("fomod/gui/logos/1456477717_error.png"),
                              QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Delete.setIcon(icon_delete)

        icon_about = QtGui.QIcon()
        icon_about.addPixmap(QtGui.QPixmap("fomod/gui/logos/1457582962_notepad.png"),
                             QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_About.setIcon(icon_about)

        icon_help = QtGui.QIcon()
        icon_help.addPixmap(QtGui.QPixmap("fomod/gui/logos/1457582991_info.png"),
                            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHe_lp.setIcon(icon_help)

        self.action_Open.triggered.connect(self.open)
        self.action_Save.triggered.connect(self.save)
        self.actionO_ptions.triggered.connect(self.options)
        self.action_Refresh.triggered.connect(self.refresh)
        self.action_Delete.triggered.connect(self.delete)
        self.actionHe_lp.triggered.connect(self.help)
        self.action_About.triggered.connect(self.about)

        self.original_title = self.windowTitle()
        self.package_path = ""
        self.info_root = None
        self.config_root = None
        self.model = QtGui.QStandardItemModel()
        self.object_tree_view.setModel(self.model)

    def open(self):
        from os.path import expanduser, normpath, basename
        from ..parser import parse

        open_dialog = QtWidgets.QFileDialog()
        self.package_path = open_dialog.getExistingDirectory(self, "Select package root directory:", expanduser("~"))

        if self.package_path:
            self.info_root, self.config_root = parse(normpath(self.package_path))

            self.model.appendRow(self.info_root.model_item)
            self.model.appendRow(self.config_root.model_item)

            title = basename(normpath(self.package_path)) + " - " + self.original_title
            self.setWindowTitle(title)

    def save(self):
        from ..serializer import serialize

        if self.info_root and self.config_root:
            serialize(self.info_root, self.config_root, self.package_path)

    def options(self):
        from . import generic
        generic.main()

    def refresh(self):
        from . import generic
        generic.main()

    def delete(self):
        from . import generic
        generic.main()

    def help(self):
        from . import generic
        generic.main()

    def about(self):
        from . import generic
        generic.main()


def main():
    window = MainFrame()
    window.exec_()


# For testing and debugging.
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainFrame()
    window.show()
    sys.exit(app.exec_())
