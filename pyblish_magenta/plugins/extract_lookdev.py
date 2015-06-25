# stdlib
import os

# maya & pyblish lib
import pyblish.api
import maya.cmds as mc

# local lib
from pyblish_magenta.utils.maya.exporter import MayaExporter
import pyblish_magenta.schema


@pyblish.api.log
class ExtractLookdev(pyblish.api.Extractor):
    """ Exports all nodes """
    hosts = ["maya"]
    families = ["lookdev"]
    optional = True

    def process(self, instance):

        raise NotImplementedError()

        # Get instance data
        data = {'root': instance.data('root'),
                'container': instance.data('container'),
                'asset': instance.data('asset')}

        # Get output directory
        schema = pyblish_magenta.schema.load()
        dir_path = schema.get("lookdev.asset").format(data)

        # TODO: Version up

        # Get output filename
        filename = "{0}.ma".format(instance.name)

        path = os.path.join(dir_path, filename)

        export_nodes = mc.ls(instance, long=True)

        if not export_nodes:
            raise RuntimeError("Nothing to export")

        MayaExporter.export(path, export_nodes,
                            preserveReferences=False,
                            constructionHistory=False,
                            expressions=False,
                            channels=True,
                            constraints=False,
                            shader=True,
                            objectSets=True,
                            displayLayers=False,
                            smoothPreview=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(instance.name, path))


# REFERENCE
# =========
import os
import shutil
import json
import logging

import maya.cmds as mc


def extract_reference():
    """
    Extract
    =======
    4. ShadingEngines to export (including textures!):
        - Copy the textures and temporary relink file locations for export.
        - Export the shaders (shadingEngines) to .mb together with a related JSON file for shaderRelations.
        - Only objects with objectIds are included in the JSON file.

    5. UserAttributes to export:
        - Export the attribute relations (attr-type, attr-name, attr-values, attr-connections?) to JSON file.
        - Only objects with objectIds are included in the JSON file.
        - If attribute has an incoming connection then include that into an .mb file that gets exported.
            (This connected node then will require objectIds for linking in the lighting file.)

    6. Sets to export:
        - Export sets to "{shader_variation}_objectSets.mb"
        - Export member relationships to JSON file. "{shader_variation}_objectSetsJSON.json"
        - Create objectIds on the sets
        - Allow referenced sets to be included (only sets made in this scene are allowed)
        - Only objects/members with objectIds are included in the JSON file.
    """
    confirm = mc.promptDialog(title='Publish LookDev',
                              message="Export selected materials for {0}\n\nShader Variation:".format(assetInfo['assetName']),
                              text='default',
                              button=['Yes', 'Increment Dev Version', 'No'],
                              defaultButton='Yes', cancelButton='No', dismissString='No')

    if confirm != 'No':
        # Save current scene
        if confirm == "Increment Dev Version":
            saveSceneIncremental()
        else:
            mc.file(save=True)
            logger.info("-- Saved scene")

        shaderVariationName = mc.promptDialog(query=True, text=True)
        shaderFileName = "{0}_{1}".format(assetInfo['assetName'], shaderVariationName)

        # Create objectIds on the shadingEngines/shadingGroups
        objectIds.createObjectId(shadingEngines)

        # -- Acquire scene information and update scene
        # region get shader relations from shadingEngines
        # -- SHADER RELATIONS
        shadingInfoList = []
        hasAnyNonIdContainingNode = False

        for sg in shadingEngines:

            # Get the shaderInfo from the shading engine
            s = shaderRelations.ShaderInfo()
            s.setObject(sg)
            s.updateShaderAssignments()

            # -- HERE WE CLEANUP THE SHADER ASSIGNMENTS INFO THAT WE EXPORT TO JSON --
            # We change the shaderInfo in such a way that we only keep the remaining data about objects that we're
            # interested in. That are the ones with both "cbAssetName" and "cbAssetObjectId". (nodes WITH objectsIds)
            # Also we remove duplicate entries of a certain cbAssetName + cbAssetObjectId combination. This could
            # happen if lookDev is being done on multiple assets of same type at the time (to see how they look in
            # bigger groups)

            combinations = set()
            shaderAssignments = []
            for o in s['shaderAssignments']:

                if o['cbAssetName'] is None or o["cbAssetObjectId"] is None:
                    logger.warning("{0} is being influenced by {1}, yet it doesn't have assetIds.".format(o['name'], s['name']))
                    hasAnyNonIdContainingNode = True
                    continue # skip it, we only want those with asset information.

                currentCombination = (o['cbAssetName'], o["cbAssetObjectId"])
                if currentCombination in combinations:
                    continue # skip it, info is already there

                combinations.add(currentCombination)
                shaderAssignments.append(o)

            s['shaderAssignments'] = shaderAssignments # Update the shaderAssignments list

            shadingInfoList.append(s)

        if hasAnyNonIdContainingNode:
                raise logger.error("Problem with shaderRelations. See script editor for details. Make sure to use a published model/rig before publishing lookDev!")
        # endregion

        # region acquire used file nodes + texture information and change to 'newPaths' temporarily
        # -- TEXTURES
        texNodes = coreShaderUtils.getRelatedTextureNodes(materials)
        textureNodePaths = dict([(node, mc.getAttr(node+".fileTextureName")) for node in texNodes])     # {node: path}
        for node in texNodes:
            oldPath = mc.getAttr(node + ".fileTextureName")
            oldPathFull = oldPath if os.path.isabs(oldPath) else os.path.normpath(mc.workspace(expandName=oldPath))
            oldPathFull.replace("\\", "/")  # force forward slashes
            newPath = oldPathFull.replace(texturesDevPath, texturesPath)
            textureNodePaths[node] = {'oldPath': oldPath, 'oldPathFull': oldPathFull, 'newPath': newPath}

            # Copy the texture
            if oldPathFull != newPath:
                if (not os.path.exists(newPath) or                                            # if destination not exists
                   abs(os.stat(oldPathFull).st_mtime - os.stat(newPath).st_mtime) > 0.1 or    # or if more than 0.1 second time difference
                   os.stat(oldPathFull).st_size != os.stat(newPath).st_size):                 # or difference in size
                    pathUtils.create_path(os.path.dirname(newPath))                           # create destination directory if not exists
                    logger.info("Copying file {0} to {1}".format(oldPathFull, newPath))
                    shutil.copyfile(oldPathFull, newPath)                                         # copy the file

        # Set nodes to new paths
        for node, pathDict in textureNodePaths.iteritems():
            mc.setAttr("{0}.fileTextureName".format(node), pathDict['newPath'], type="string")
        # endregion

        # -- Export data
        # region EXPORT shadingEngines to shaderVariationName_shader.mb
        # On export `preserve references` is set to True as it is more convenient to allow for some sort of nesting of
        # look development variations. (eg. using referenced shaders from a resources folder that is used throughout a
        # project or a shader for proxies that is a layer on top of the normal shader (eg. VRayMeshMaterial))

        exportNodes = shadingEngines
        # TODO: Check if publish still export correct data with the lines below commented. (First tests: seems fine!)
        #exportNodes.extend(mc.listHistory(shadingEngines))
        #shapesInList = mc.ls(exportNodes, s=True)
        #exportNodes = list(set(exportNodes).difference(set(shapesInList)))      # filter out any shapes in the list

        mc.select(exportNodes, r=1, noExpand=True)
        shaderFilePath = os.path.join(shadersPath, "{0}_shader.mb".format(shaderFileName))

        mc.file(shaderFilePath, force=True, options="v=0;", typ="mayaBinary", pr=True, es=True)
        logger.info("-- Exported shader selection to {0}".format(shaderFilePath))
        # endregion

        # region EXPORT shadingInfoList to shaderVariationName_JSON.json
        shaderRelationsFilePath = os.path.join(shadersPath, "{0}_shaderRelations.json".format(shaderFileName))
        shadingInfoListJson = json.dumps(shadingInfoList, cls=ShadingInfoEncoder)
        pathUtils.write_file(shaderRelationsFilePath, shadingInfoListJson, overwrite=True)
        logger.info("-- Exported shaderRelations-JSON to {0}".format(shaderRelationsFilePath))
        # endregion

        # region EXPORT userAttributes relations to :shaderVariation:_attributeRelations.json
        errorMsg = "NOT IMPLEMENTED YET: EXPORT userAttributes relations to :shaderVariation:_attributeRelations.json"
        QtGui.QMessageBox.warning(None, errorTitle, errorMsg)
        logger.warning(errorMsg)
        # endregion

        # region EXPORT sets + sets relations to :shaderVariation:_objectSets.mb and :shaderVariation:_objectSetsJSON.json

        # Add objectIds to the sets that will be exported
        for objectSet in objectSetsMembers.iterkeys():
            logger.info('Adding objectIds to set {0}'.format(objectSet))
            objectIds.createObjectId(objectSet)

        # TODO: Temporarily remove all members of a set and then export the sets as selection
        # TODO: >> This way we can still export with connections and avoid exporting the set members to the .mb file.

        errorMsg = "NOT IMPLEMENTED YET: EXPORT sets + sets relations to :shaderVariation:_objectSets.mb and :shaderVariation:_objectSetsJSON.json"
        QtGui.QMessageBox.warning(None, errorTitle, errorMsg)
        logger.warning(errorMsg)
        # endregion

        # -- REVERT CHANGES TO SCENE
        # region revert changes to textures
        # Revert nodes to oldPaths (easier to make an undo queue chunk and undo afterwards?)
        for node, pathDict in textureNodePaths.iteritems():
            mc.setAttr("{0}.fileTextureName".format(node), pathDict['oldPath'], type="string")
        # endregion

        logger.info("Published LookDev succesfully.")