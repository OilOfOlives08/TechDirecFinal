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
