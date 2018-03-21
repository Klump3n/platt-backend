/*
 * norderney -- Display FEM raw data in a browser
 * Copyright (C) 2018 Matthias Plock <matthias.plock@bam.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

function DatasetView(gl, sceneHash, datasetHash) {

    var m = meshData[datasetHash];

    var datasetCenter = m.surfaceData['nodesCenter'];

    // fucking javascript
    var that = this;

    // define all those matrices we need and set them to identity
    var projectionMatrix = twgl.m4.identity();
    var viewMatrix = twgl.m4.identity();
    var viewProjectionMatrix = twgl.m4.identity();

    var centerDatasetMatrix = twgl.m4.identity(); // just a centered and upscaled dataset
    var datasetMatrix = twgl.m4.identity(); // the centered, upscaled, BUT ALSO moved dataset

    var datasetTranslation = twgl.v3.create(0, 0, 0);
    var datasetTranslationMatrix = twgl.m4.identity();
    var datasetRotationMatrix = twgl.m4.identity();

    // the placing of the camera in the world
    var viewerPosition = [0, 0, 100];      // place the viewer on the z axis
    var viewingTargetPosition = [0, 0, 0]; // look at the coordinate center
    var upVector =  [0, -1, 0]; // the up vector is defined in the -y direction

    var cameraToTargetVector;

    var datasetScreenCenter;
    var x_center;
    var y_center;

    var datasetScalingFactor = 100;
    /**
     * Variables for tracking the mouse movement and dragging events.
     */
    var x_prev = 0,
        x_now = 0;

    var y_prev = 0,
        y_now = 0;

    var start_mouse = false;
    var dragging = false;
    var translating_model = false;

    this.change_orientation = false;

    var translationFactor;

    var thetaAxis = twgl.v3.create(0, 0, 0);

    // setup/place camera and stuff
    setupWorld().then(function() {

        // check the server for updates on the orientation every second or send it there
        setInterval(orientationCheck, 1000);

        // a vector pointing from the camera to the datasets center
        cameraToTargetVector = twgl.v3.subtract(datasetTranslation, viewerPosition);

        datasetScreenCenter = worldToScreen(datasetTranslation);
        x_center = datasetScreenCenter[0];
        y_center = datasetScreenCenter[1];

        /** Initialise the eventListener for mouse-button-pressing */
        gl.canvas.addEventListener("mousedown", doMouseDown, false);
        gl.canvas.addEventListener("DOMMouseScroll", doMouseWheel, false);
    });



    /**
     * Update the orientation of the dataset before the camera.
     */
    this.updateView = function() {
        return twgl.m4.multiply(viewProjectionMatrix, datasetMatrix);
    };

    /**
     * Setup the world. Set the frustum and place the camera in the world.
     */
    function setupWorld() {
        return new Promise(function(resolve, reject) {

            // Set the frustum of the camera (angle of camera, depth of field and so on)
            var fovIn;
            var aspectIn;
            var zNearIn;
            var zFarIn;
            setFrustum(fovIn, aspectIn, zNearIn, zFarIn);

            // place the camera in the world
            placeCamera(viewerPosition, viewingTargetPosition, upVector);

            // combine the two camera matrices. this will remain unchanged
            viewProjectionMatrix = twgl.m4.multiply(projectionMatrix, viewMatrix);

            // scale the dataset a bit so the handling is easier
            centerDatasetMatrix = twgl.m4.scale(
                centerDatasetMatrix,
                twgl.v3.create(
                    datasetScalingFactor,
                    datasetScalingFactor,
                    datasetScalingFactor
                )
            );

            // translate the model so its centered
            centerDatasetMatrix = twgl.m4.translate(centerDatasetMatrix, twgl.v3.negate(datasetCenter));

            var updateTimestep = connectToAPIPromise(
                basePath = basePath,
                APIEndpoint = "scenes/" + sceneHash + "/" + datasetHash + "/orientation",
                HTTPMethod = "get",
                payload = {}
            );
            updateTimestep.then(function(value) {

                var init = value['datasetOrientationInit'];

                if (init) {

                    // get the orientation from the server
                    datasetTranslationMatrix = new Float32Array(value['datasetOrientation']['datasetTranslation']);
                    datasetRotationMatrix = new Float32Array(value['datasetOrientation']['datasetRotation']);
                    // extract the translation from it

                    datasetTranslation = twgl.m4.getTranslation(datasetTranslationMatrix);

                    // update the dataset matrix
                    datasetMatrix = twgl.m4.multiply(datasetRotationMatrix, centerDatasetMatrix);
                    datasetMatrix = twgl.m4.multiply(datasetTranslationMatrix, datasetMatrix);

                } else {

                    // update the dataset matrix on init
                    datasetMatrix = twgl.m4.multiply(datasetRotationMatrix, centerDatasetMatrix);
                    datasetMatrix = twgl.m4.multiply(datasetTranslationMatrix, datasetMatrix);

                    // upload the initial translation and rotation to the server (will be unity)
                    var payload = {
                        'datasetTranslation': Array.from(datasetTranslationMatrix),
                        'datasetRotation': Array.from(datasetRotationMatrix)
                    };

                    updateTimestep = connectToAPIPromise(
                        basePath = basePath,
                        APIEndpoint = "scenes/" + sceneHash + "/" + datasetHash + "/orientation",
                        HTTPMethod = "patch",
                        payload = {'datasetOrientation': payload} // upload basically nothing... its unity anyway
                    );
                }

                resolve();
            });
        });
    }


    function orientationCheck() {

        // var m = meshData[datasetHash];

        var updateTimestep;

        if (m.changeThisOrientation) {

            var payload = {
                'datasetTranslation': Array.from(datasetTranslationMatrix),
                'datasetRotation': Array.from(datasetRotationMatrix)
            };

            updateTimestep = connectToAPIPromise(
                basePath = basePath,
                APIEndpoint = "scenes/" + sceneHash + "/" + datasetHash + "/orientation",
                HTTPMethod = "patch",
                payload = {'datasetOrientation': payload}
            );

        } else {

            updateTimestep = connectToAPIPromise(
                basePath = basePath,
                APIEndpoint = "scenes/" + sceneHash + "/" + datasetHash + "/orientation",
                HTTPMethod = "get",
                payload = {}
            );
            updateTimestep.then(function(value) {

                datasetTranslationMatrix = new Float32Array(value['datasetOrientation']['datasetTranslation']);
                datasetRotationMatrix = new Float32Array(value['datasetOrientation']['datasetRotation']);

                // extract the translation from it
                datasetTranslation = twgl.m4.getTranslation(datasetTranslationMatrix);

                // update the dataset matrix
                datasetMatrix = twgl.m4.multiply(datasetRotationMatrix, centerDatasetMatrix);
                datasetMatrix = twgl.m4.multiply(datasetTranslationMatrix, datasetMatrix);
            });
        }
    }

    /**
     * Create the frustum of our view.
     * @param {float} fovIn - [OPTIONAL] Field Of View -- The angle with which
     * we perceive objects.
     * @param {float} aspectIn - [OPTIONAL] Aspect ratio of the canvas.
     * @param {float} zNearIn - [OPTIONAL] The closest distance at which we
     * can see objects in our frustum.
     * @param {float} zFarIn - [OPTIONAL] - The furthest distance at which we
     * can see objects in our frustum.
     */
    function setFrustum(fovIn, aspectIn, zNearIn, zFarIn) {

        // reset the projectionMatrix
        projectionMatrix = twgl.m4.identity();

        var fov = 30 * Math.PI / 180 || fovIn;
        var aspect = gl.canvas.clientWidth/gl.canvas.clientHeight || aspectIn;
        var zNear = 1 || zNearIn;
        var zFar = 2000 || zFarIn;

        /** Calculate the perspective matrix. */
        projectionMatrix = twgl.m4.perspective(
            fov, aspect, zNear, zFar);
    };

    /**
     * Creates a viewMatrix by inverting the camera matrix.
     * @param {vec3} viewerPosition - The position of the viewer.
     * @param {vec3} viewingTargetPosition - The position of the target.
     * @param {vec3} upVector - A vector that points upwards.
     */
    function placeCamera(viewerPosition, viewingTargetPosition, upVector) {

        // reset view- and camMatrix
        var camMatrix = twgl.m4.identity();
        camMatrix = twgl.m4.lookAt(viewerPosition, viewingTargetPosition, upVector);
        viewMatrix = twgl.m4.inverse(camMatrix);
    };

    /**
     * Translate the model by translation.
     * @param {twgl.v3 vector} translation - The amount of translation.
     */
    function translateDataset(translation) {

        if (that.change_orientation) {
            datasetTranslation = twgl.v3.add(datasetTranslation, translation);

            var translateBy = twgl.m4.translation(translation);
            datasetTranslationMatrix = twgl.m4.multiply(translateBy, datasetTranslationMatrix);

            datasetMatrix = twgl.m4.multiply(translateBy, datasetMatrix);

            // only translation of the dataset will change its position in space
            // and thus make the recomputation of the axis vector for rotation
            // necessary
            cameraToTargetVector = twgl.v3.subtract(datasetTranslation, viewerPosition);

            datasetScreenCenter = worldToScreen(datasetTranslation);
            x_center = datasetScreenCenter[0];
            y_center = datasetScreenCenter[1];
        }
    }

    function rotateDataset(differentialRotation) {

        if (that.change_orientation) {
            // move to center, apply rotation and move back
            datasetMatrix = twgl.m4.multiply(twgl.m4.inverse(datasetTranslationMatrix), datasetMatrix);
            datasetMatrix = twgl.m4.multiply(differentialRotation, datasetMatrix);
            datasetMatrix = twgl.m4.multiply(datasetTranslationMatrix, datasetMatrix);

            datasetRotationMatrix = twgl.m4.multiply(differentialRotation, datasetRotationMatrix);
        }
    }

    /**
     * Get the SCREEN coordinates (in pixels) for a point in world space.
     * @param {twgl.v3} worldSpacePoint - The point in world coordinates.
     * @returns {twgl.v3} A vector where the first 2 coordinates are the screen
     * coordinates
     */
    function worldToScreen(worldSpacePoint) {

        var M = twgl.m4.transpose(viewProjectionMatrix);

        var x = (
            M[0]*worldSpacePoint[0] +
                M[1]*worldSpacePoint[1] +
                M[2]*worldSpacePoint[2] +
                M[3]*1
        ),
            y = (
                M[4]*worldSpacePoint[0] +
                    M[5]*worldSpacePoint[1] +
                    M[6]*worldSpacePoint[2] +
                    M[7]*1
            ),
            z = (
                M[8]*worldSpacePoint[0] +
                    M[9]*worldSpacePoint[1] +
                    M[10]*worldSpacePoint[2] +
                    M[11]*1
            ),
            w = (
                M[12]*worldSpacePoint[0] +
                    M[13]*worldSpacePoint[1] +
                    M[14]*worldSpacePoint[2] +
                    M[15]*1
            );

        var xn = x/w,
            yn = y/w,
            zn = z/w;

        var sx = (xn + 1)/2 * gl.canvas.clientWidth,
            sy = (1 - yn)/2 * gl.canvas.clientHeight;

        // var sx = Math.round((x + 1)/2 * gl.canvas.clientWidth),
        //     sy = Math.round((1 - y)/2 * gl.canvas.clientHeight);

        return twgl.v3.create(sx, sy, 0);
    }

    /**
     * The the WORLD coordinates for a point in screen space. This will only
     * produce results for the z=0 plane.
     * @param {twgl.v3} screenSpacePoint - The point in screen space
     * @returns {twgl.v3} A vector where the first two coordinates are points
     * in world space
     */
    function screenToWorld(screenSpacePoint) {
        var sx = screenSpacePoint[0],
            sy = screenSpacePoint[1];

        var x = 2 * sx / gl.canvas.clientWidth - 1,
            y = -2 * sy / gl.canvas.clientHeight + 1;

        var M = twgl.m4.inverse(twgl.m4.transpose(viewProjectionMatrix));

        var distFromCamZ = twgl.v3.subtract(viewerPosition, datasetTranslation)[2];

        var wx = distFromCamZ * (M[0]*x + M[1]*y),
            wy = distFromCamZ * (M[4]*x + M[5]*y);

        return twgl.v3.create(wx, wy, 0);
    }

    /**
     * doMouseWheel: callback function for mouse wheel events. I.e.: zooming in
     * and out.
     * @param {event} event
     */
    function doMouseWheel(event){
        var factor = 10;
        var delta = factor*Math.max(-1, Math.min(1, (event.wheelDelta || -event.detail)));

        var translation = twgl.v3.create(0, 0, -delta);
        translateDataset(translation);

        delta = 0;
    }

    /**
     * Callback function for a mouse-button-down event. Sets dragging
     * to true and adds two eventListeners (one for mouse movement and
     * one for the release of the mouse button).
     * @param {} event
     */
    function doMouseDown(event){
        if (dragging || translating_model) {
            return;
        }

        x_prev = 0;
        x_now = 0;

        y_prev = 0;
        y_now = 0;

        start_mouse = true;

        if (!event.ctrlKey) {
            dragging = true;
        }

        if (event.ctrlKey) {
            translating_model = true;
        }

        document.addEventListener("mousemove", doMouseMove, true);
        document.addEventListener("mouseup", doMouseUp, false);

        // Create a vector thats orhthogonal to eye- and up vector
        thetaAxis = twgl.v3.cross(cameraToTargetVector, upVector);
    }

    /**
     * Callback function for a mouse-move event. If the mouse-button
     * has not been pressed nothing will happen. If dragging is true
     * it will calculate a velocity of the mouse movement.
     * @param {} event
     */
    function doMouseMove(event){
        if (!dragging && !translating_model) {
            return;
        }

        if (start_mouse){
            // This prevents a resetting effect when drag-and-dropping over
            // the screen.
            x_prev = event.clientX - x_center;
            y_prev = y_center - event.clientY;
            start_mouse = false;
            return;
        }

        if (dragging) {
            // Get current coordinates

            x_now = event.clientX - x_center;
            y_now = y_center - event.clientY;

            var normCameraToTargetVector = twgl.v3.normalize(cameraToTargetVector);

            var differentialRotation = getDifferentialQuaternionRotation(
                x_start=x_prev, y_start=y_prev,
                x_end=x_now, y_end=y_now,
                radius=200,
                x_axis=twgl.v3.normalize(twgl.v3.create(-1, 0, 0)),
                y_axis=twgl.v3.normalize(twgl.v3.create(0, -1, 0)),
                z_axis=twgl.v3.normalize(twgl.v3.create(0, 0, 1))
            );
            rotateDataset(differentialRotation);

            x_prev = event.clientX - x_center;
            y_prev = y_center - event.clientY;
        }

        if (translating_model) {
            // Get current coordinates
            x_now = event.clientX - x_center;
            y_now = y_center - event.clientY;

            var dx_screen = x_prev - x_now,
                dy_screen = y_prev - y_now;

            var dr_screen = Math.sqrt(dx_screen*dx_screen + dy_screen*dy_screen);

            var worldNow = screenToWorld(twgl.v3.create(x_now, y_now, 0));
            var worldPrev = screenToWorld(twgl.v3.create(x_prev, y_prev, 0));

            var dx_world = worldPrev[0] - worldNow[0],
                dy_world = worldPrev[1] - worldNow[1];

            var dr_world = Math.sqrt(dx_world*dx_world + dy_world*dy_world);

            if (dr_world != 0) {
                translationFactor = dr_world / dr_screen;
            }

            // move
            var translation = twgl.v3.create(dx_screen, dy_screen, 0);
            // scale by how much we translate
            translation = twgl.v3.mulScalar(translation, translationFactor);
            translateDataset(translation);

            x_prev = event.clientX - x_center;
            y_prev = y_center - event.clientY;
        }
    }

    /**
     * Callback function for a mouse-button-release event. If the
     * mouse-button is released it will delete the two eventListeners for
     * mouse-movement and mouse-button-release and disable dragging.
     * @param {} event
     */
    function doMouseUp(event){
        if (!dragging && !translating_model) {
            return;
        }
        document.removeEventListener("mousemove", doMouseMove, false);
        document.removeEventListener("mouseup", doMouseUp, false);
        prevx = 0;
        prevy = 0;

        dragging = false;
        translating_model = false;
    }

    /**
     * getDifferentialQuaternionRotation
     *
     * Given two points on the screen with x and y components, calculate a
     * differential rotation matrix based on quaternions.
     * @param {float} x_start - Starting point x coordinate
     * @param {float} y_start - Starting point y coordinate
     * @param {float} x_end - End point x coordinate
     * @param {float} y_end - End point y coordinate
     * @param {float} radius - The radius of the sphere. This affects how quick
     * the rotations are with respect to mouse movements
     * @param {vec3} reference_frame_x - A vector that defines x on the screen
     * @param {vec3} reference_frame_y - A vector that defines y on the screen
     * @param {vec3} reference_frame_z - A vector pointing towards the viewer
     * @returns {mat4} rotMatrixQuat - A differential quaternion matrix
     */
    function getDifferentialQuaternionRotation(
        x_start, y_start,
        x_end, y_end,
        radius,
        reference_frame_x, reference_frame_y, reference_frame_z
    ){

        // Define a surface on which we want to measure our mouse movements
        function z_on_surface(x, y) {
            var dd = x*x + y*y;
            if (dd < radius*radius/2){
                // A regular sphere
                return Math.sqrt(radius*radius - dd);
            } else {
                // A hyperbolic surface that diverges at the screen center
                return radius*radius/2/Math.sqrt(dd);
            }
        }

        // v1 und v2 muessen vom Ursprung des datasets kommen
        // die kugel muss auch an diese stelle gepackt werden


        // Define two normalised vectors from the center of the sphere
        var v1 = [x_start, y_start, z_on_surface(x_start, y_start)];
        v1 = twgl.v3.normalize(v1);
        var v2 = [x_end, y_end, z_on_surface(x_end, y_end)];
        v2 = twgl.v3.normalize(v2);

        // Angle by which to rotate
        var angle = Math.acos(twgl.v3.dot(v1, v2));
        // Axis around which to rotate
        var axis  = twgl.v3.cross(v1, v2);
        axis = twgl.v3.normalize(axis);

        // If we get an invalid angle we dont rotate at all.
        if (isNaN(angle)){
            angle = 0;
            axis = twgl.v3.create(1, 0, 0); // Direction does not matter, angle is 0 anyway.
        }

        // Calculate the quaternion
        var qw = Math.cos(angle/2),
            qx = twgl.v3.dot(axis, twgl.v3.normalize(reference_frame_x))*Math.sin(angle/2),
            qy = twgl.v3.dot(axis, twgl.v3.normalize(reference_frame_y))*Math.sin(angle/2),
            qz = twgl.v3.dot(axis, twgl.v3.normalize(reference_frame_z))*Math.sin(angle/2);

        // Generate a matrix from the quaternion
        var rotMatrixQuat = twgl.m4.identity();
        rotMatrixQuat[0] = 1 - 2*(qy*qy + qz*qz);
        rotMatrixQuat[1] = 2*(qx*qy + qw*qz);
        rotMatrixQuat[2] = 2*(qx*qz - qw*qy);
        rotMatrixQuat[3] = 0;
        rotMatrixQuat[4] = 2*(qx*qy - qw*qz);
        rotMatrixQuat[5] = 1 - 2*(qx*qx + qz*qz);
        rotMatrixQuat[6] = 2*(qw*qx + qy*qz);
        rotMatrixQuat[7] = 0;
        rotMatrixQuat[8] = 2*(qw*qy + qx*qz);
        rotMatrixQuat[9] = 2*(qy*qz - qw*qx);
        rotMatrixQuat[10] = 1 - 2*(qx*qx + qy*qy);

        return rotMatrixQuat;
    }

}
