import maya.cmds as cmds

def auto_skin_weights(selected_joints, selected_meshes, max_influences=4):
    if not selected_joints or not selected_meshes:
        cmds.warning("Please select at least one joint and one or more meshes.")
        return

    for mesh in selected_meshes:
        # Delete old skinCluster if it exists
        existing_skin = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
        if existing_skin:
            cmds.delete(existing_skin)
        
        skin_cluster = cmds.skinCluster(
            selected_joints,
            mesh,
            toSelectedBones=True,
            normalizeWeights=1,
            bindMethod=0,
            skinMethod=0,
            dropoffRate=4.0,
            maximumInfluences=max_influences
        )
        print(f"Skinned: {mesh} → {skin_cluster}")
        
def build_ui():
    if cmds.window("autoSkinWin", exists=True):
        cmds.deleteUI("autoSkinWin")
    
    window = cmds.window("autoSkinWin", title="✨ Auto Skin Weights (Multi Mesh)", widthHeight=(300, 300))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAlign="center")
    
    cmds.text(label="1. Select Joints\n2. Select One or More Meshes\n3. Click Auto Skin!", align='center')
    cmds.separator(height=10, style='in')
    
    cmds.text(label="Selected Joints:", align='left')
    cmds.textFieldButtonGrp(
        "jointField",
        buttonLabel="Load",
        text="",
        buttonCommand=lambda: load_selection_to_field("jointField", multi=True)
    )
    
    cmds.text(label="Selected Meshes:", align='left')
    cmds.textFieldButtonGrp(
        "meshField",
        buttonLabel="Load",
        text="",
        buttonCommand=lambda: load_selection_to_field("meshField", multi=True)
    )
    
    cmds.separator(height=10, style='in')
    
    cmds.text(label="Max Influences per Vertex:", align='left')
    cmds.intSliderGrp(
        "influenceSlider",
        field=True,
        minValue=1,
        maxValue=8,
        fieldMinValue=1,
        fieldMaxValue=20,
        value=4
    )
    
    cmds.separator(height=10, style='in')
    
    cmds.button(label="🎯 Auto Skin All Meshes!", height=40, command=lambda *args: run_auto_skin())

    cmds.setParent('..')
    cmds.showWindow(window)
