"""
Model exported as python.
Name : PPK tags
Group : Dron
With QGIS : 32201
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PpkTags(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('eventpos', 'Event_pos', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('nmeronombreprimerafoto', 'Número nombre primera foto', type=QgsProcessingParameterNumber.Integer, defaultValue=1))
        self.addParameter(QgsProcessingParameterRasterLayer('geoideenformatoraster', 'Geoide en formato raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('estilo', 'Estilo', optional=True, behavior=QgsProcessingParameterFile.File, fileFilter='Archivo de estilo (*.qml*)', defaultValue='D:\\QGIS Datos\\PPK_tags.qml'))
        self.addParameter(QgsProcessingParameterFeatureSink('Ppk_tags', 'PPK_tags', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Aplicar estilo condicional
        alg_params = {
        }
        outputs['AplicarEstiloCondicional'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Muestra de valores ráster
        alg_params = {
            'COLUMN_PREFIX': 'REDNAP',
            'INPUT': parameters['eventpos'],
            'RASTERCOPY': parameters['geoideenformatoraster'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MuestraDeValoresRster'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Rehacer campos
        alg_params = {
            'FIELDS_MAPPING': [{'expression': "concat('DJI_', if(  @nmeronombreprimerafoto+$id-1 <10,'000',if(  @nmeronombreprimerafoto+$id-1 <100,'00',if(  @nmeronombreprimerafoto+$id-1 <1000,'0',''))),@nmeronombreprimerafoto+$id-1,'.JPG')",'length': 12,'name': 'Foto','precision': 0,'type': 10},{'expression': '"latitude(deg)"','length': 0,'name': 'latitude(deg)','precision': 0,'type': 6},{'expression': '"longitude(deg)"','length': 0,'name': 'longitude(deg)','precision': 0,'type': 6},{'expression': ' "height(m)"- "REDNAP1" ','length': 0,'name': 'height(m)','precision': 0,'type': 6},{'expression': '0','length': 0,'name': 'phi','precision': 0,'type': 6},{'expression': '0','length': 0,'name': 'omega','precision': 0,'type': 6},{'expression': '0','length': 0,'name': 'lambda','precision': 0,'type': 6},{'expression': 'if("Q"=1, sqrt("sdn(m)"^2+ "sde(m)" ^2)+0.01, sqrt("sdn(m)"^2+ "sde(m)" ^2)+5)','length': 0,'name': 'p_h','precision': 4,'type': 6},{'expression': 'IF("Q"=1, "sdu(m)"+0.01, "sdu(m)"+5)','length': 0,'name': 'p_v','precision': 4,'type': 6}],
            'INPUT': outputs['MuestraDeValoresRster']['OUTPUT'],
            'OUTPUT': parameters['Ppk_tags']
        }
        outputs['RehacerCampos'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ppk_tags'] = outputs['RehacerCampos']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Establecer el estilo de capa
        alg_params = {
            'INPUT': outputs['RehacerCampos']['OUTPUT'],
            'STYLE': parameters['estilo']
        }
        outputs['EstablecerElEstiloDeCapa'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'PPK tags'

    def displayName(self):
        return 'PPK tags'

    def group(self):
        return 'Dron'

    def groupId(self):
        return 'Dron'

    def createInstance(self):
        return PpkTags()
