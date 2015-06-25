# stdlib
import itertools

# maya lib
from maya import cmds


def get_shading_engines(nodes):
    """ Return the related shadingEngines for given node shapes.

    We can get the shadingEngine by doing:
        - maya.cmds.listSets(object=shape, t=1) # t=1 will filter to render sets only
        - maya.cmds.listConnections(shape, type='shadingEngine')

    Invoking a command many times in Maya can often result in a big performance hit.
    The `listSets` is per object whereas listConnections can run on a full list of nodes.
    Yet `listConnections` returns the same shadingEngine multiple times (a lot; especially with face assignments!).
    In practice I've found listSets to be the winner in both speed and ease of use.

    .. note:: I've seen some issues with listSets and namespaces, like not giving the full name with namespace.
              Need to do some more investigation to that.
    """
    shapes = cmds.ls(nodes, dag=1, lf=1, o=1, s=1)
    if shapes:
        sg = set()
        for shape in shapes:
            render_sets = cmds.listSets(object=shape, t=1, extendToShape=False)
            if render_sets:
                for shading_engine in render_sets:
                    sg.add(shading_engine)

        sg = list(sg)
        return sg
    else:
        return []


def get_shader_assignment(shapes):
    shapes = cmds.ls(shapes, dag=1, shapes=1, long=1)
    if not shapes:
        return {}

    shading_engines = get_shading_engines(shapes)

    assignments = {}
    object_lookup = set(shapes)     # set for faster look-up table
    for sg in shading_engines:
        # Since sg_members can also contain components we need to check whether the member (either component or full
        # shape) is related to the shapes we want information about. Because component (eg. face) assignments are listed
        # with the transform name (eg. '|pSphere1.f[141:146]') it's easiest to enforce it towards the full shape
        # names using cmds.ls(o=True)
        sg_members = cmds.sets(sg, q=1)
        sg_members_objects = cmds.ls(sg_members, o=True, long=True)
        if not sg_members:
            continue

        assignments[sg] = [] # initialize with empty list (we could also use defaultdict!)
        for member, member_object in itertools.izip(sg_members, sg_members_objects):
            if member_object in object_lookup:
                assignments[sg].append(member)

    return assignments


def get_material_from_shading_engine(shading_engine):
    """ Returns a uniqified list of materials connected to the shadingEngine/shadingGroup """
    results = cmds.ls(cmds.listConnections(shading_engine) or [], mat=True)
    return list(set(results))


def get_shading_engine_from_material(material):
    """ Returns a uniqified list of shadingEngines/shadingGroups connected to the material """
    results = cmds.listConnections(material, type="shadingEngine") or []
    return list(set(results))


def perform_shader_assignment(assignmentDict):
    for shadingGroup, members in assignmentDict.iteritems():
        if members:
            cmds.sets(members, e=True, forceElement=shadingGroup)


def get_sets_from_nodes(nodes, type=None, exactType=None, excludeType=None, excludeExactType=None, extendToShape=False):
    """
        Returns all sets the nodes are included in.

        :param extendToShape:   When requesting a transform's sets also walk down to the shape immediately below it for
                                its sets.
        :type  extendToShape:   bool

        :param type:            Return these set types only. (including inherited types)
        :type  type:            None, list or str

        :param excludeType:      Filter out all sets of this these. (including inherited types)
        :type  excludeType:      None, list or str

        :param exactType:       Return these set types only.
        :type  exactType:       None, list or str

        :param excludeExactType: Filter out all sets of this these.
        :type  excludeExactType: None, list or str
    """
    # Make sure we have a list of nodes
    if not isinstance(nodes, (list, tuple)):
        if isinstance(nodes, basestring):
            nodes = [nodes]
        else:
            raise TypeError("nodes must be a list or str of object name(s).")

    if excludeType is not None:
        if not isinstance(excludeType, (list, tuple)):
            if isinstance(excludeType, basestring):
                excludeType = (excludeType,)
            else:
                raise TypeError("filterType must be a list or str of node type(s) or None.")

    lsKwargs = {}
    if not type is None:
        lsKwargs['type'] = type
    if not exactType is None:
        lsKwargs['exactType'] = exactType

    lsExcludeKwargs = {}
    if not excludeType is None:
        lsExcludeKwargs['type'] = excludeType
    if not excludeExactType is None:
        lsExcludeKwargs['exactType'] = excludeExactType

    allSets = set()
    for node in nodes:
        sets = cmds.listSets(object=node, ets=extendToShape)

        if sets and type:
            sets = cmds.ls(sets, **lsKwargs)

        if sets and excludeType:
            # Preserve sets list order by using list comprehension instead of set(sets).difference()
            exclude = set(cmds.ls(sets, **lsExcludeKwargs))
            if exclude:
                sets = [x for x in sets if x not in exclude]

        if sets:
            allSets.update(sets)

    return list(allSets)