import adsk.core, adsk.fusion
import math

def run(context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        print("Error: No active Fusion design")
        return
        
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    rootComp = design.rootComponent
    
    for occ in list(rootComp.occurrences):
        if occ.component.name.startswith("Prototype11"):
            occ.deleteMe()
            
    occurrences = rootComp.occurrences
    subCompOcc = occurrences.addNewComponent(adsk.core.Matrix3D.create())
    subComp = subCompOcc.component
    subComp.name = "Prototype11_FireFly"
    
    sketches = subComp.sketches
    xzPlane = subComp.xZConstructionPlane
    xyPlane = subComp.xYConstructionPlane
    revolves = subComp.features.revolveFeatures
    extrudes = subComp.features.extrudeFeatures
    moves = subComp.features.moveFeatures
    combines = subComp.features.combineFeatures
    fillets = subComp.features.filletFeatures
    mirrors = subComp.features.mirrorFeatures

    def create_sphere(name, center_point, radius):
        sk = sketches.add(xzPlane)
        lines = sk.sketchCurves.sketchLines
        arcs = sk.sketchCurves.sketchArcs
        
        c = center_point
        r = radius
        p1 = adsk.core.Point3D.create(c.x, c.z - r, 0)
        p2 = adsk.core.Point3D.create(c.x - r, c.z, 0)
        p3 = adsk.core.Point3D.create(c.x, c.z + r, 0)
        
        axis = lines.addByTwoPoints(p1, p3)
        axis.isConstruction = True
        arcs.addByThreePoints(p1, p2, p3)
        lines.addByTwoPoints(p3, p1)
        
        prof = sk.profiles.item(0)
        rev_in = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rev_in.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        rev = revolves.add(rev_in)
        b = rev.bodies.item(0)
        b.name = name
        
        if c.y != 0:
            t_mat = adsk.core.Matrix3D.create()
            t_mat.translation = adsk.core.Vector3D.create(0, c.y, 0)
            b_coll = adsk.core.ObjectCollection.create()
            b_coll.add(b)
            moves.add(moves.createInput(b_coll, t_mat))
        return b

    # 1. 胴体 (BODY SPHERE)
    print("Creating Body Sphere...")
    body_center = adsk.core.Point3D.create(0, 0, 0)
    body_abdomen = create_sphere("Body_Sphere", body_center, 2.8)

    # 2. 頭部 (HEAD SPHERE)
    print("Creating Head Sphere...")
    head_center = adsk.core.Point3D.create(-1.6, 0, 2.2)
    body_head = create_sphere("Head_Sphere", head_center, 1.6)

    # 3. 目 (EYES)
    print("Creating Eyes...")
    eye_radius = 0.48
    eye_left = create_sphere("Eye_Left", adsk.core.Point3D.create(-2.7, 1.05, 2.4), eye_radius)
    eye_right = create_sphere("Eye_Right", adsk.core.Point3D.create(-2.7, -1.05, 2.4), eye_radius)

    # 4. 内部コアピラー
    print("Creating Inner Core...")
    sk_c = sketches.add(xzPlane)
    l_c = sk_c.sketchCurves.sketchLines
    ax_c = l_c.addByTwoPoints(adsk.core.Point3D.create(0, -2.5, 0), adsk.core.Point3D.create(0, 2.5, 0))
    ax_c.isConstruction = True
    l_c.addByTwoPoints(adsk.core.Point3D.create(0, -2.4, 0), adsk.core.Point3D.create(0.8, -2.4, 0))
    l_c.addByTwoPoints(adsk.core.Point3D.create(0.8, -2.4, 0), adsk.core.Point3D.create(1.2, 1.8, 0))
    l_c.addByTwoPoints(adsk.core.Point3D.create(1.2, 1.8, 0), adsk.core.Point3D.create(0, 1.8, 0))
    l_c.addByTwoPoints(adsk.core.Point3D.create(0, 1.8, 0), adsk.core.Point3D.create(0, -2.4, 0))
    
    prof_c = sk_c.profiles.item(0)
    rev_in_c = revolves.createInput(prof_c, ax_c, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    rev_in_c.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
    rev_c = revolves.add(rev_in_c)
    body_core = rev_c.bodies.item(0)
    body_core.name = "Inner_Core"

    # 5. 胸部首元カバー (Thorax Collar)
    print("Creating Thorax Collar...")
    sk_th = sketches.add(xzPlane)
    l_th = sk_th.sketchCurves.sketchLines
    a_th = sk_th.sketchCurves.sketchArcs
    
    p_t1 = adsk.core.Point3D.create(-1.8, 2.2, 0)
    p_t2 = adsk.core.Point3D.create(-0.2, 3.4, 0)
    p_t3 = adsk.core.Point3D.create(1.0, 2.4, 0)
    a_th.addByThreePoints(p_t1, p_t2, p_t3)
    l_th.addByTwoPoints(p_t3, p_t1)
    
    prof_th = sk_th.profiles.item(0)
    ext_th_in = extrudes.createInput(prof_th, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_th_in.setSymmetricExtent(adsk.core.ValueInput.createByReal(2.3), True)
    ext_th = extrudes.add(ext_th_in)
    body_thorax = ext_th.bodies.item(0)
    body_thorax.name = "Thorax_Cover"

    # 6. 3D曲面羽: 首元は緊密、計測中のお尻側先端の距離を大幅に開く (Tail Gap Widen to ~30-35mm)
    print("Creating Wings with Wide Tail Spread...")
    
    outer_sphere = create_sphere("Outer_Shell", body_center, 3.30)
    inner_cut_sphere = create_sphere("Inner_Cut_Sphere", body_center, 2.90)
    
    tools_coll = adsk.core.ObjectCollection.create()
    tools_coll.add(inner_cut_sphere)
    comb_in = combines.createInput(outer_sphere, tools_coll)
    comb_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combines.add(comb_in)
    wing_shell_body = outer_sphere

    sk_cut = sketches.add(xzPlane)
    arcs_cut = sk_cut.sketchCurves.sketchArcs
    
    pc1 = adsk.core.Point3D.create(-1.2, 2.8, 0)
    pc2 = adsk.core.Point3D.create(3.4, 0.6, 0)
    pc3 = adsk.core.Point3D.create(1.5, -3.2, 0)
    arcs_cut.addByThreePoints(pc1, pc2, pc3)
    
    # Inner opening arc: Widens significantly towards tail
    pc4 = adsk.core.Point3D.create(2.2, 0.2, 0)
    arcs_cut.addByThreePoints(pc1, pc4, pc3)
    
    prof_cut = sk_cut.profiles.item(0)
    
    ext_wing_in = extrudes.createInput(prof_cut, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_wing_in.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(3.5)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext_wing_box = extrudes.add(ext_wing_in)
    wing_box_body = ext_wing_box.bodies.item(0)
    
    tools_comb = adsk.core.ObjectCollection.create()
    tools_comb.add(wing_box_body)
    comb_wing_in = combines.createInput(wing_shell_body, tools_comb)
    comb_wing_in.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    combines.add(comb_wing_in)
    
    body_wing_left = wing_shell_body
    body_wing_left.name = "Wing_Left"

    # Shift Wing_Left slightly in Y (1 mm offset at top)
    t_wl = adsk.core.Matrix3D.create()
    t_wl.translation = adsk.core.Vector3D.create(0.0, 0.10, 0.0)
    coll_wl = adsk.core.ObjectCollection.create()
    coll_wl.add(body_wing_left)
    moves.add(moves.createInput(coll_wl, t_wl))

    # Rotate Wing_Left by 22 degrees around top anchor point (-1.2, 0.1, 2.8) to flare open tail tips
    pivot_anchor = adsk.core.Point3D.create(-1.2, 0.1, 2.8)
    hinge_axis = adsk.core.Vector3D.create(1, 0, 0.35)
    rot_tail_wide = adsk.core.Matrix3D.create()
    rot_tail_wide.setToRotation(math.radians(22), hinge_axis, pivot_anchor)
    moves.add(moves.createInput(coll_wl, rot_tail_wide))

    # Apply fillets for smooth rounded edges
    edge_coll_wl = adsk.core.ObjectCollection.create()
    for e in body_wing_left.edges:
        edge_coll_wl.add(e)
    if edge_coll_wl.count > 0:
        try:
            f_in = fillets.createInput()
            f_in.addConstantRadiusEdgeSet(edge_coll_wl, adsk.core.ValueInput.createByReal(0.12), True)
            fillets.add(f_in)
        except Exception as ex:
            print(f"Wing fillet note: {ex}")

    # Mirror Wing_Left across XZ plane for Wing_Right
    coll_w_mirror = adsk.core.ObjectCollection.create()
    coll_w_mirror.add(body_wing_left)
    mirror_input = mirrors.createInput(coll_w_mirror, xzPlane)
    mirror_w = mirrors.add(mirror_input)
    body_wing_right = mirror_w.bodies.item(0)
    body_wing_right.name = "Wing_Right"

    # 7. 全体の傾き調整
    rot_mat = adsk.core.Matrix3D.create()
    rot_mat.setToRotation(math.radians(-25), adsk.core.Vector3D.create(0, 1, 0), adsk.core.Point3D.create(0, 0, 0))
    subCompOcc.transform = rot_mat

    app.activeViewport.fit()
    print("Prototype11 Wide Tail Spread Wing Model Created Successfully!")
