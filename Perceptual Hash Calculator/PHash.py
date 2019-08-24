# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This jython autopsy module can calculate perceptual hash value of jpg files 
# in the data source with pHash. If there is an import of perceptual hash value, 
# it also can calculate the difference between the import and other pictures' value 
# and look for similar pictures.
#
# Contact: Yuming Chen [ychen54@gmu.edu]
#
# Data source-level ingest module for Autopsy to calculate perceptual hash value.
# April 4 2019
# Version 1.4

import jarray
import inspect
import os
import sys

from javax.swing import JCheckBox
from javax.swing import JLabel
from javax.swing import JList
from javax.swing import JTextArea
from javax.swing import BoxLayout
from java.awt import GridLayout
from java.awt import BorderLayout
from javax.swing import BorderFactory
from javax.swing import JToolBar
from javax.swing import JPanel
from javax.swing import JFrame
from javax.swing import JScrollPane
from javax.swing import JComponent
from java.awt.event import KeyListener
from java.awt.event import KeyEvent
from java.awt.event import KeyAdapter
from javax.swing.event import DocumentEvent
from javax.swing.event import DocumentListener

from java.lang import Class
from java.lang import System
from java.sql  import DriverManager, SQLException
from java.util.logging import Level
from java.util import ArrayList
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.datamodel import ContentUtils
sys.path.append(r"D:\Files\Course\772\Final\phash.jar")
from phash import PHash


# Factory that defines the name and details of the module and allows Autopsy
# to create instances of the modules that will do the analysis.
class PerceptualHashIngestModuleFactory(IngestModuleFactoryAdapter):

    moduleName = "PHash Module"
    
    def getModuleDisplayName(self):
        return self.moduleName
    
    def getModuleDescription(self):
        return "PHash Module"
    
    def getModuleVersionNumber(self):
        return "4.0"
    
    def getDefaultIngestJobSettings(self):
        return GenericIngestModuleJobSettings()

    def hasIngestJobSettingsPanel(self):
        return True

    # TODO: Update class names to ones that you create below
    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, GenericIngestModuleJobSettings):
            raise IllegalArgumentException("Expected settings argument to be instanceof GenericIngestModuleJobSettings")
        self.settings = settings
        return PerceptualHashSettingsPanel(self.settings)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return PerceptualHashIngestModule(self.settings)


# Data Source-level ingest module.  One gets created per data source.
class PerceptualHashIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(PerceptualHashIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self, settings):
        self.context = None
        self.local_settings = settings
        self.pHashToCheck = ""
       
    def startUp(self, context):
        self.context = context
        # self.pHashToCheck = "1001000011001000110100001101001001001010001011010001011000001110"
		# self.pHashToCheck = "90c8d0d24a2d160e"

        if self.local_settings.getSetting('Flag') == 'true':
            self.pHashToCheck = self.local_settings.getSetting('pHash')
        else:
            self.pHashToCheck = ""

    def process(self, dataSource, progressBar):

        # we don't know how much work there is yet
        progressBar.switchToIndeterminate()

        # Use blackboard class to index blackboard artifacts for keyword search
        blackboard = Case.getCurrentCase().getServices().getBlackboard()
        
        # Find files named contacts.db, regardless of parent path
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "%.jpg")

        numFiles = len(files)
        self.log(Level.INFO, "found " + str(numFiles) + " files")
        progressBar.switchToDeterminate(numFiles)
        fileCount = 0
        for file in files:

            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1

            # Make an artifact on the blackboard.  TSK_INTERESTING_FILE_HIT is a generic type of
            # artifact.  Refer to the developer docs for other examples.
            art = file.newArtifact(
                BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT)
            att = BlackboardAttribute(
                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SET_NAME,
                PerceptualHashIngestModuleFactory.moduleName,
                "Picture Files")
            art.addAttribute(att)

            try:
                # index the artifact for keyword search
                blackboard.indexArtifact(art)
            except Blackboard.BlackboardException as e:
                self.log(Level.SEVERE,
                         "Error indexing artifact " + art.getDisplayName())

            # Fire an event to notify the UI and others that there is a new artifact
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(
                    PerceptualHashIngestModuleFactory.moduleName,
                    BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT,
                    None))

            Temp_Dir = Case.getCurrentCase().getTempDirectory()
            self.log(Level.INFO, "Create Directory " + Temp_Dir)
            try:
                temp_dir = os.path.join(Temp_Dir, "Pictures")
                os.mkdir(temp_dir)
            except:
                self.log(Level.INFO,
                         "Pictures Directory already exists " + temp_dir)

            # Save the File locally in a user-defined temp folder.
            lclDbPath = os.path.join(temp_dir, file.getName())
            ContentUtils.writeToFile(file, File(lclDbPath))

            # This code will use the phash library to calculate perceptual hash value and difference.
            phash = PHash()
            path_img = os.path.join(temp_dir, file.getName())
            bit_phash = phash.getHash(path_img)
            hex_phash = PHash.binaryString2hexString(bit_phash)
            self.log(Level.INFO,
                     file.getName() + ":Path ==> " + path_img + "  ")
            #self.log(Level.INFO,
                     #file.getName() + ":pHash(bit) ==> " + bit_phash + "  ")
            self.log(Level.INFO,
                     file.getName() + ":PHash ==> " + hex_phash + "  ")
            if (self.pHashToCheck != ""):
                self.log(Level.INFO,
                         "pHashToCheck ==> " + self.pHashToCheck + "  ")
                differ_phash = PHash.distance(PHash.hexString2binaryString(self.pHashToCheck), bit_phash)
                self.log(Level.INFO,
                         file.getName() + ":Difference ==> " + str(
                             differ_phash) + "  ")
                if (differ_phash < 20):
                    self.log(Level.INFO,
                             file.getName() + ":Similar? ==> True  ")
                else:
                    self.log(Level.INFO,
                             file.getName() + ":Similar? ==> False  ")

        # After all databases, post a message to the ingest messages in box.
        message = IngestMessage.createMessage(
            IngestMessage.MessageType.DATA,
            "PerceptualHash Analyzer", "Found %d files" % fileCount)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK

       
class PerceptualHashSettingsPanel(IngestModuleIngestJobSettingsPanel):
    # TODO: Update this for your UI
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()
    
    # TODO: Update this for your UI
    def checkBoxEvent(self, event):
        if self.checkbox.isSelected():
            self.local_settings.setSetting('Flag', 'true')
            self.local_settings.setSetting('pHash', self.area.getText());
        else:
            self.local_settings.setSetting('Flag', 'false')

    # TODO: Update this for your UI
    def initComponents(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))
        self.setAlignmentX(JComponent.LEFT_ALIGNMENT)
        self.panel1 = JPanel()
        self.panel1.setLayout(BoxLayout(self.panel1, BoxLayout.Y_AXIS))
        self.panel1.setAlignmentY(JComponent.LEFT_ALIGNMENT)
        self.checkbox = JCheckBox("Check to activate/deactivate pHashToCheck",
                                  actionPerformed=self.checkBoxEvent)
        self.label0 = JLabel(" ")
        self.label1 = JLabel("Input your phash value for checking: ")
        self.label2 = JLabel(" ")
        self.panel1.add(self.checkbox)
        self.panel1.add(self.label0)
        self.panel1.add(self.label1)
        self.panel1.add(self.label2)
        self.add(self.panel1)
 
        self.area = JTextArea(5,25)
        self.area.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0))
        self.pane = JScrollPane()
        self.pane.getViewport().add(self.area)
        self.add(self.pane)

    # TODO: Update this for your UI
    def customizeComponents(self):
        self.checkbox.setSelected(
            self.local_settings.getSetting('Flag') == 'true')
        self.area.setText(self.local_settings.getSetting('pHash'))

    # Return the settings used
    def getSettings(self):
        return self.local_settings

