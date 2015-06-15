import os.path

from maya import cmds
import pyblish.api

import pyblish_magenta.schema

import pyblish_magenta.utils.maya.shaders as shader_utils


def get_all_parents(long_name):
    parents = long_name.split("|")[1:-1]
    return ['|{0}'.format('|'.join(parents[0:i+1])) for i in xrange(len(parents))]


@pyblish.api.log
class SelectLookdevInstance(pyblish.api.Selector):
    """ Inject all assets' for which shader assignments must be published (if in lookdev workspace).

    From objectSet 'PUBLISH' it will take:

            1. Materials/Shaders
            2. Nodes including all children.

        .. note::
            We're including transforms because for some (eg. renderable curve) sets the transforms are members
            instead of the shapes.

    Select
    ======
    1. From nodes it will:
        - Find related shaders to include in `shadingEngines to extract`.
        - Include the nodes in `userAttributes to extract`.

    2. From materials/shaders it will:
        - Include the shadingEngines in `shadingEngines to extract`.
        - Find related objects (assigned objects) to include the nodes in `userAttributes to extract`.

    3. From relatedNodes found from above (outputs of 1+2):
        - Find the sets that these are members of for export to define `SETS TO EXTRACT`
        - Only allow NON-referenced sets to be included in `SETS TO EXTRACT`
    """
    hosts = ["maya"]

    def process(self, context):
        self.log.info("Selecting lookdev..")

        # File Path
        # ---------
        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            self.log.error("Scene has not been saved.")
            return

        # Parse with schema
        schema = pyblish_magenta.schema.load()
        data = schema.get("lookdev.dev").parse(scene_name)
        root = data['root']
        asset = data['asset']
        container = data['container']

        # Scene Nodes
        # --------------
        # Get the PUBLISH objectSet for all materials to be published
        object_set = cmds.ls('PUBLISH', type='objectSet')
        objects = cmds.sets(object_set, q=1)
        if not objects:
            raise RuntimeError("No objects found to be exported. Create an objectSet with the name 'PUBLISH'")

        # Include all children from the `objects`  (extend the list)
        objects.extend(cmds.listRelatives(objects, allDescendents=True, fullPath=True) or [])
        # Replace above line with `mc.ls(sl=1, dag=1, leaf=1, shapes=1, long=True)` to exclude transforms

        # Get all shading engines (also those from materials)
        shading_engines = set(cmds.ls(objects, type='shadingEngine'))
        for material in cmds.ls(objects, mat=True):
            material_shading_engines = shader_utils.get_shading_engine_from_material(material)
            shading_engines.update(material_shading_engines)
        shading_engines = list(shading_engines)

        # Get the shader assigned nodes (from shadingEngines)
        assigned_nodes = set()
        shading_assignments = {}
        for shading_engine in shading_engines:
            shader_assigned_nodes = cmds.sets(shading_engine, q=1)
            shading_assignments[shading_engine] = shader_assigned_nodes
            assigned_nodes.update(shader_assigned_nodes)

        # We will only publish shaders for referenced assets.
        matched = set()
        instances = []

        for node in assigned_nodes:
            if cmds.referenceQuery(node, isNodeReferenced=True):
                ref_node = cmds.referenceQuery(node, referenceNode=True)
                path = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)

                # Process each reference only once.
                if path in matched:
                    continue

                data, template = schema.parse(path)

                instances.append(data)

        for data in instances:

            # Create the instance
            label = "{0} ({1})".format(data['asset'], data['container'])
            instance = context.create_instance(name=data['asset'],
                                               label=label,
                                               family='lookdev')

            # TODO: Add the related nodes/data that is required for the export

            # Set Pipeline data
            instance.set_data("root", root)
            instance.set_data("source_file", scene_name)
            instance.set_data("asset", asset)
            instance.set_data("container", container)


# Reference
# =========

def select_reference():
    # TODO: Figure out a way to publish lookDev for different assets at the same time. (So publish to location based on
    # TODO: >> objectIds on the nodes.)
    # TODO: >> >> Do we allow multiple assets to be export into a single sets-relationship? How would we do this?
    ###################
    # TODO: Figure out a way to keep the published textures clean after testing with many different textures.
    # TODO: >> Currently it copies over all the textures on publish, but doesn't remove what has been unlinked.
    # TODO: >> Maybe also write out data (JSON?) on what textures are used by a variation, then on publish lookDev
    # TODO: >> it can go over all these JSON files and see if any textures in the published folder are unused.
    ###################
    # TODO: Implement show existing shader variations from older publishLookDev()
    ###################

    texturesPath = 'asset/textures'
    texturesDevPath = 'dev/textures'
    shadersPath = 'asset/shaders'

    # Get related materials from objects
    materialsFromObjects = coreShaderUtils.getMaterialFromObject(objects)

    # endregion

    # region (2) Get Selected Materials (and related objects)
    selectedMaterials = cmds.ls(sl=1, mat=1, long=True)

    # Get related objects from materials
    if selectedMaterials:
        for shadingEngine in coreShaderUtils.shadingEngineFromMaterial(selectedMaterials):
            objectsFromMaterials = cmds.ls(coreShaderUtils.getSetMembers(shadingEngine), long=True)
            if objectsFromMaterials:
                objects.extend(objectsFromMaterials)

    # Materials from selection and from selected meshes
    materials = selectedMaterials + materialsFromObjects
    if not materials:
        errorMsg = "No materials found to export.\nSelect materials or objects that have materials assigned."
        QtGui.QMessageBox.information(None, errorTitle, errorMsg)
        raise RuntimeError(errorMsg)

    shadingEngines = coreShaderUtils.shadingEngineFromMaterial(materials)
    if not shadingEngines:
        errorMsg = "No shadingEngines found for the given materials.\nMake sure they are assigned to objects."
        QtGui.QMessageBox.information(None, errorTitle, errorMsg)
        raise RuntimeError(errorMsg)

    # Skip shadingEngines that have no members (like often 'initialParticleSE') otherwise unexpected can happen
    # Filter to shadingEngines that actually have any members
    shadingEngines = [sg for sg in shadingEngines if coreShaderUtils.getSetMembers(sg)]

    # endregion

    objects = list(set(objects)) # keep unique only, and order doesn't matter
    objectsWithIds = objectIds.getNodesWithObjectIds(objects) # keep track of objects that have objectIds (going forward)

    print '-- shadingEngines\n    ', shadingEngines
    print '-- materials\n    ', materials
    print '-- objects\n    ', objects
    print '-- objects with ids\n    ', objectsWithIds

    # region (3) Get related sets
    # ObjectSets
    # Get all sets related to the objects (that are not shadingEngines)

    print '-- ObjectSets\n'
    objectSets = coreShaderUtils.getSetsFromNodes(objects, excludeType="shadingEngine")

    # Only allow sets that are NOT referenced! So they need to have been created in the current scene.
    objectSets = [node for node in objectSets if not cmds.referenceQuery(node, isNodeReferenced=True)]
    objectSetsMembers = {}
    for objectSet in objectSets:
        members = coreShaderUtils.getSetMembers(objectSet)

        # We can only re-assign members/sets for nodes with objectIds.
        # So this is only useful for members that have objectIds, thus we keep only those.
        members = objectIds.getNodesWithObjectIds(members)

        # If we still have members then we add it to the 'export set with set members` dictionary: `objectSetsMembers`.
        if members:
            objectSetsMembers[objectSets] = members

    # Clean-up so we avoid using it later in the script (avoid confusion)
    del objectSets #  This is the unfiltered objectSets list. We don't need it anymore, we now have the filtered dict.
    # endregion

    # region (??) Get UserAttributes from objects
    print '-- UserAttributes\n'
    # We only get UserAttributes (UserDefined or FromPlugin) that start with one of `exportAttrPrefixes` prefixes
    # and filter attributes that have exact names
    exportAttrPrefixes = ["vray", "ai"]
    attributeBlackList = set() # search `in` often (so optimize by making it a set).

    # Validate attribute function
    validAttr = lambda attr: any(attr.startswith(prefixAttr) for prefixAttr in exportAttrPrefixes) and \
                             attr not in attributeBlackList
    for node in cmds.ls(objects, o=1, long=True):
        nodeAttrs = []

        # Get attributes from plug-ins that are in-use (altered from default value or changing the current scene in some way)
        attrs = [attr for attr in cmds.listAttr(node, inUse=True, fromPlugin=True) or [] if validAttr(attr)]
        nodeAttrs.extend(attrs)

        # Get attributes that are user defined (not created with the node by default)
        attrs = [attr for attr in cmds.listAttr(node, userDefined=True) or [] if validAttr(attr)]
        nodeAttrs.extend(attrs)

        # If the node we're operating on is referenced then only include attributes that were changed/edited.
        # So check attribute changes for reference edits! (check referenceEdits)
        if cmds.referenceQuery(node, isNodeReferenced=True):
            refNode = referenceUtils.getRefNode(node)
            refEditedAttrs = cmds.referenceQuery(en=True, editAttrs=True, showDagPath=True, showNamespace=True)
            if not refEditedAttrs:
                nodeAttrs = []
                continue

            refEditedAttrs = set(refEditedAttrs) # optimize for search if x is in it.
            nodeAttrs = [x for x in nodeAttrs if x in refEditedAttrs]
    # endregion