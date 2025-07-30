# -*- coding: utf-8 -*-
import maya.cmds as cmds

def clean_influences_ui():
    window_name = "CleanInfluencesWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Clean Weak Influences Tool", sizeable=False, resizeToFitChildren=True)

    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign='center')
    cmds.text(label="Select a skinned mesh before running")

    cmds.floatFieldGrp('weightThreshold', label="Weight Threshold (<=)", value1=0.1)
    cmds.intSliderGrp('percentThreshold', label="Affect Percent (%)", field=True, minValue=0, maxValue=100, value=90)

    cmds.button(label="Start Cleaning", command=lambda x: clean_low_influence_joints_ui())
    cmds.scrollField('outputLog', wordWrap=True, editable=False, height=150)

    cmds.showWindow(window_name)

def clean_low_influence_joints_ui():
    threshold = cmds.floatFieldGrp('weightThreshold', q=True, value1=True)
    percent = cmds.intSliderGrp('percentThreshold', q=True, value=True)
    percent_limit = percent / 100.0

    sel = cmds.ls(sl=True, dag=True, type="mesh")
    if not sel:
        cmds.warning("Please select a skinned mesh")
        return

    mesh = sel[0]
    history = cmds.listHistory(mesh)
    skin = cmds.ls(history, type='skinCluster')

    if not skin:
        cmds.warning("No skinCluster found")
        return

    skin = skin[0]
    influences = cmds.skinCluster(skin, q=True, inf=True)
    vtx_count = cmds.polyEvaluate(mesh, v=True)
    removed = []

    for jnt in influences:
        low_weight_count = 0
        for i in range(vtx_count):
            wt = cmds.skinPercent(skin, "{}.vtx[{}]".format(mesh, i), transform=jnt, q=True)
            if wt <= threshold:
                low_weight_count += 1

        if (float(low_weight_count) / vtx_count) >= percent_limit:
            cmds.skinCluster(skin, e=True, ri=jnt)
            removed.append("{} affected {}/{} vertices (<= {})".format(jnt, low_weight_count, vtx_count, threshold))

    if removed:
        log = "\n".join(removed)
    else:
        log = "No joints matched the criteria. Nothing cleaned."

    cmds.scrollField('outputLog', e=True, text=log)

