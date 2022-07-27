import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from geo.Geoserver import Geoserver

# GLOBAL VARIABLES
geo  = None
fn = None
class DlgMain(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("geoserver-rest.ui", self)

        # CREATE SIGNALS
        self.authenticateGeoserverBtn.clicked.connect(self.evt_authenticateGeoserver_clicked)
        self.createWorkspaceBtn.clicked.connect(self.evt_createWorkspace_clicked)
        self.publishBtn.clicked.connect(self.evt_publish_clicked)
        self.openShapefileBtn.clicked.connect(self.evt_openShapefile_clicked)


    def evt_authenticateGeoserver_clicked(self):
        global geo
        geo = Geoserver(self.geoserverUrl.text(), username=self.geoserverUsername.text(), password=self.geoserverPassword.text())
        self.workspaceGbx.setEnabled(True)

    def evt_createWorkspace_clicked(self):
        msg = QMessageBox()
        msg.setText(geo.create_workspace(workspace=self.workspaceName.text()))
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        self.geoserverPublishGbx.setEnabled(True)

    def evt_openShapefile_clicked(self):
        global fn
        fn, chk = QFileDialog.getOpenFileName(self, "Open Shapefile", "/Users/saimanojappalla/Desktop", "Shape Files (*.shp)")
        self.shapefilePath.setText(fn)

    def evt_publish_clicked(self):
        name = fn.split('/')[-1].split('.')[0]
        geo.create_datastore(name=self.storeName.text(),
                             path=self.shapefilePath.text(),
                             workspace=self.workspaceNameCreatedBefore.text())

        geo.publish_featurestore(workspace=self.workspaceNameCreatedBefore.text(), store_name=self.storeName.text(), pg_table=name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlgMain = DlgMain()
    dlgMain.show()
    sys.exit(app.exec_())