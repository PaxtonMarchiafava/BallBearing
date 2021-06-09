#Author-Paxton Marchiafava
#Description-Generates a roller bearing with variable defined parameters

import adsk.core, adsk.fusion, adsk.cam, traceback, math

# get these as input. Math done as cm
insideRadius = 2.5
horizontalThickness = 1
vertThickness = 1
holeRadius = 0.3025
divotClearence = 0.05
elevation = -0.2


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()

        des = adsk.fusion.Design.cast(app.activeProduct)

        # Create a new component by creating an occurrence.
        occs = des.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)        
        newComp = adsk.fusion.Component.cast(newOcc.component)
        newComp.name = "Roller Bearing " + str(round(((insideRadius + horizontalThickness) * 2) * 10)) + "mm OD" # name

        # Create a new sketch on the xz plane and draw a line from 0,0,0 to a defined length away on the x axis.
        home = adsk.core.Point3D.create(0, 0, 0) # create points to make lines

        bottomLeft = adsk.core.Point3D.create(insideRadius, 0, 0) # for outer box
        bottomRight = adsk.core.Point3D.create(insideRadius + horizontalThickness, 0, 0)
        topLeft = adsk.core.Point3D.create(insideRadius, -vertThickness, 0)
        topRight = adsk.core.Point3D.create(insideRadius + horizontalThickness, -vertThickness, 0)

        bottomMid = adsk.core.Point3D.create(insideRadius + horizontalThickness / 2, 0, 0) # for mid line and offsets
        topMid = adsk.core.Point3D.create(insideRadius + horizontalThickness / 2, -vertThickness, 0)

        leftUpper = adsk.core.Point3D.create(insideRadius, -vertThickness / 2 + elevation, 0) # points for elevation lines
        leftCircle = adsk.core.Point3D.create(insideRadius + (horizontalThickness / 2) - holeRadius, -vertThickness / 2, 0)
        circleLeftTop = adsk.core.Point3D.create(((insideRadius + (horizontalThickness / 2) - holeRadius - insideRadius) / 2) + insideRadius, -vertThickness / 2 + elevation, 0)
        circleLeftBottom = adsk.core.Point3D.create(((insideRadius + (horizontalThickness / 2) - holeRadius - insideRadius) / 2) + insideRadius, -vertThickness / 2, 0)

        circleMid = adsk.core.Point3D.create(insideRadius + (horizontalThickness / 2), -vertThickness / 2, 0)
        revolvePoint = adsk.core.Point3D.create(0, -vertThickness, 0)

        sketches = newComp.sketches

        xyPlane = newComp.xZConstructionPlane # make sketch on a given plane
        sketch = sketches.add(xyPlane)

        sketch.sketchCurves.sketchLines.addByTwoPoints(home, bottomLeft) # home to bottom left corner
        sketch.sketchCurves.sketchLines.addByTwoPoints(bottomLeft, bottomRight) # bottom left corner to bottom right corner
        sketch.sketchCurves.sketchLines.addByTwoPoints(bottomLeft, topLeft) # bottom left corner to top left corner
        sketch.sketchCurves.sketchLines.addByTwoPoints(topLeft, topRight) # top left corner to top right
        sketch.sketchCurves.sketchLines.addByTwoPoints(bottomRight, topRight) # bottom right to top right
        sketch.sketchCurves.sketchLines.addByTwoPoints(bottomMid, topMid) # line down the middle for the clearence

        revolveLine = sketch.sketchCurves.sketchLines.addByTwoPoints(home, revolvePoint) # revolve line

        sketch.sketchCurves.sketchCircles.addByCenterRadius(circleMid, holeRadius)

        objectCollection = adsk.core.ObjectCollection.create() # create and add a line to object collection
        objectCollection.add(sketch.sketchCurves.sketchLines.addByTwoPoints(bottomMid, topMid))

        sketch.offset(objectCollection, adsk.core.Point3D.create(insideRadius + (horizontalThickness / 2) + divotClearence / 2, -vertThickness / 2, 0), divotClearence) # offset using object collection
        sketch.offset(objectCollection, adsk.core.Point3D.create(insideRadius + (horizontalThickness / 2) - divotClearence / 2, -vertThickness / 2, 0), divotClearence)

        sketch.sketchCurves.sketchLines.addByTwoPoints(leftUpper, circleLeftTop) # create elevation for assembly
        sketch.sketchCurves.sketchLines.addByTwoPoints(circleLeftTop, circleLeftBottom)
        sketch.sketchCurves.sketchLines.addByTwoPoints(circleLeftBottom, leftCircle)


        
        # revolve, 7 out, 5 in bottom, 4 in top
        profile = sketch.profiles.item(4)
        profiles = adsk.core.ObjectCollection.create()
        profiles.add(sketch.profiles.item(5))
        profiles.add(sketch.profiles.item(7))

        # Create an revolution input to be able to define the input needed for a revolution
        # while specifying the profile and that a new component is to be created
        revolves = newComp.features.revolveFeatures
        revInput = revolves.createInput(profiles, revolveLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        revInputTop = revolves.createInput(profile, revolveLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is 2 * pi cause radians not degrees
        angle = adsk.core.ValueInput.createByReal(math.pi * 2)
        revInput.setAngleExtent(False, angle)
        revInputTop.setAngleExtent(False, angle)

        # Create the extrusion.
        revolves.add(revInput)
        revolves.add(revInputTop)
        

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
