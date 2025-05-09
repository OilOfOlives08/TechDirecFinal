import maya.cmds as cmds

def should_mirror(joints):
    return any(j.lower().startswith(('l_', 'left')) for j in joints)

def auto_skin_weights(selected_joints, selected_meshes, max_influences=4):
    if not selected_joints or not selected_meshes:
        cmds.warning("Please select at least one joint and one or more meshes.")
        return

    cmds.undoInfo(openChunk=True)
    try:
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
                bindMethod=0,  # Closest Distance
                skinMethod=0,  # Classic Linear
                dropoffRate=4.0,
                maximumInfluences=max_influences
            )
            cmds.inViewMessage(amg=f"<hl>Skinned:</hl> {mesh}", pos='midCenter', fade=True)

            if should_mirror(selected_joints):
                try:
                    cmds.mirrorSkinWeights(
                        mesh,
                        mirrorMode='YZ',
                        direction='leftToRight',
                        surfaceAssociation='closestPoint',
                        influenceAssociation=['name']
                    )
                    cmds.inViewMessage(amg=f"<hl>Mirrored:</hl> {mesh}", pos='midCenter', fade=True)
                except Exception as e:
                    cmds.warning(f"Could not mirror skin weights for {mesh}: {e}")
            else:
                cmds.inViewMessage(amg=f"<hl>Skipped mirroring for:</hl> {mesh}", pos='midCenter', fade=True)

    finally:
        cmds.undoInfo(closeChunk=True)

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

    # Pre-fill selection fields on launch
    load_selection_to_field("jointField", multi=True)
    load_selection_to_field("meshField", multi=True)

def load_selection_to_field(field_name, multi=True):
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("Nothing selected.")
        return
    if not multi and len(selection) > 1:
        cmds.warning("Please select only one item.")
        return
    cmds.textFieldButtonGrp(field_name, edit=True, text=",".join(selection))

def run_auto_skin():
    joints_text = cmds.textFieldButtonGrp("jointField", query=True, text=True)
    meshes_text = cmds.textFieldButtonGrp("meshField", query=True, text=True)
    max_influences = cmds.intSliderGrp("influenceSlider", query=True, value=True)

    if not joints_text or not meshes_text:
        cmds.warning("Please load joints and meshes.")
        return

    selected_joints = [j.strip() for j in joints_text.split(",") if j.strip()]
    selected_meshes = [m.strip() for m in meshes_text.split(",") if m.strip()]

    auto_skin_weights(selected_joints, selected_meshes, max_influences)

# Run the UI
build_ui()
