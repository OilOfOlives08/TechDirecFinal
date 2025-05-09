import maya.cmds as cmds

PLUGIN_NAME = "autoSkinWin"

# --- Utility Functions ---
def is_left_joint(joint):
    return joint.lower().startswith(('l_', 'left'))

def is_right_joint(joint):
    return joint.lower().startswith(('r_', 'right'))

def get_mirror_direction(joints):
    if any(is_left_joint(j) for j in joints):
        return 'leftToRight'
    elif any(is_right_joint(j) for j in joints):
        return 'rightToLeft'
    return None

def is_valid_mesh(obj):
    if cmds.objectType(obj) != 'transform':
        return False
    shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
    return bool(shapes)

def is_valid_joint(obj):
    return cmds.objectType(obj) == 'joint'

def auto_skin_weights(selected_joints, selected_meshes, max_influences=4, mirror_axis='YZ'):
    if not selected_joints or not selected_meshes:
        cmds.warning("Please select at least one joint and one or more meshes.")
        return

    valid_joints = [j for j in selected_joints if is_valid_joint(j)]
    invalid_joints = [j for j in selected_joints if not is_valid_joint(j)]
    valid_meshes = [m for m in selected_meshes if is_valid_mesh(m)]
    invalid_meshes = [m for m in selected_meshes if not is_valid_mesh(m)]

    if invalid_joints:
        cmds.warning("Invalid joints: {}".format(", ".join(invalid_joints)))
    if invalid_meshes:
        cmds.warning("Invalid meshes: {}".format(", ".join(invalid_meshes)))

    if not valid_joints or not valid_meshes:
        cmds.warning("Aborting due to invalid selections.")
        return

    mirror_direction = get_mirror_direction(valid_joints)

    cmds.undoInfo(openChunk=True)
    try:
        for mesh in valid_meshes:
            try:
                existing_skin = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
                if existing_skin:
                    result = cmds.confirmDialog(
                        title="Replace SkinCluster?",
                        message=f"{mesh} already has a skinCluster. Delete and replace?",
                        button=["Yes", "No"], defaultButton="Yes", cancelButton="No", dismissString="No"
                    )
                    if result == "No":
                        continue
                    cmds.delete(existing_skin)

                cmds.skinCluster(
                    valid_joints,
                    mesh,
                    toSelectedBones=True,
                    normalizeWeights=1,
                    bindMethod=0,
                    skinMethod=0,
                    dropoffRate=4.0,
                    maximumInfluences=max_influences
                )
                cmds.inViewMessage(amg=f"<hl>Skinned:</hl> {mesh}", pos='midCenter', fade=True)

                if mirror_direction:
                    try:
                        cmds.mirrorSkinWeights(
                            mesh,
                            mirrorMode=mirror_axis,
                            direction=mirror_direction,
                            surfaceAssociation='closestPoint',
                            influenceAssociation=['name']
                        )
                        cmds.inViewMessage(amg=f"<hl>Mirrored:</hl> {mesh}", pos='midCenter', fade=True)
                    except Exception as e:
                        cmds.warning(f"Could not mirror skin weights for {mesh}: {e}")
                else:
                    cmds.inViewMessage(amg=f"<hl>Skipped mirroring for:</hl> {mesh}", pos='midCenter', fade=True)
            except Exception as e:
                cmds.warning(f"Error skinning {mesh}: {e}")
    finally:
        cmds.undoInfo(closeChunk=True)

# --- UI Functions ---
def build_ui():
    if cmds.window(PLUGIN_NAME, exists=True):
        cmds.deleteUI(PLUGIN_NAME)

    window = cmds.window(PLUGIN_NAME, title="\u2728 Auto Skin Weights Plugin", widthHeight=(300, 350))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAlign="center")

    cmds.text(label="1. Select Joints\n2. Select Meshes\n3. Click Auto Skin!", align='center')
    cmds.separator(height=10, style='in')

    cmds.text(label="Selected Joints:", align='left')
    cmds.textFieldButtonGrp("jointField", buttonLabel="Load", text="", buttonCommand=lambda: load_selection_to_field("jointField", multi=True))

    cmds.text(label="Selected Meshes:", align='left')
    cmds.textFieldButtonGrp("meshField", buttonLabel="Load", text="", buttonCommand=lambda: load_selection_to_field("meshField", multi=True))

    cmds.separator(height=10, style='in')

    cmds.text(label="Max Influences per Vertex:", align='left')
    cmds.intSliderGrp("influenceSlider", field=True, minValue=1, maxValue=8, fieldMinValue=1, fieldMaxValue=20, value=4)

    cmds.text(label="Mirror Axis:", align='left')
    cmds.optionMenu("mirrorAxisMenu", label="", width=100)
    for axis in ["YZ", "XY", "XZ"]:
        cmds.menuItem(label=axis)

    cmds.separator(height=10, style='in')

    cmds.button(label="\ud83c\udfaf Auto Skin All Meshes!", height=40, command=lambda *args: run_auto_skin())

    cmds.setParent('..')
    cmds.showWindow(window)

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
    mirror_axis = cmds.optionMenu("mirrorAxisMenu", query=True, value=True)

    if not joints_text or not meshes_text:
        cmds.warning("Please load joints and meshes.")
        return

    selected_joints = [j.strip() for j in joints_text.split(",") if j.strip()]
    selected_meshes = [m.strip() for m in meshes_text.split(",") if m.strip()]

    auto_skin_weights(selected_joints, selected_meshes, max_influences, mirror_axis)

# --- Entry Point for Maya ---
def launch_auto_skin_plugin():
    build_ui()

# Call this to start UI if script is run directly
if __name__ == '__main__':
    launch_auto_skin_plugin()
