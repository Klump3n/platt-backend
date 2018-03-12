/*
 * fem-gl -- Display FEM raw data in a browser
 * Copyright (C) 2017 Matthias Plock <matthias.plock@bam.de>
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

var gl;

// Make the array for holding web gl data global.
var vertexDataHasChanged = false;
var fragmentDataHasChanged = false;

var bufferDataArray;
// var edgeDataArray;
var bufferFreeEdgesArray;
var bufferWireframeArray;

var shaders;
var surfaceData = {
    "nodes": [],
    "nodesCenter": [],
    "tets": [],
    "wireframe": [],
    "freeEdges": [],
    "field": []
};

var model_metadata;
var surfaceNodesCenter;

var fragmentShaderTMin = 0.0;
var fragmentShaderTMax = 800.0;

var bufferIndexArray;

var currentMeshHash = '';
var currentFieldHash = '';

/**
 * Try to find a HTML5 canvas element. If found, try to assign it a WebGL2
 * context. If this fails throw an error, else return the context.
 * @param {string} canvasElementName The HTML5 canvas element.
 * @returns {context} gl - The WebGL2 context.
 * @throws {error} Error: No WebGL2
 */
function grabCanvas(canvasElementName) {

    // Select the canvas element from the html
    var webGlCanvas = document.getElementById(canvasElementName);

    // Create a webGl2 context if possible
    var gl = twgl.getContext(webGlCanvas);

    // Check if WebGL 2.0, if not throw error
    function isWebGL2(gl) {
        return gl.getParameter(gl.VERSION).indexOf("WebGL 2.0") == 0;
    }
    if (isWebGL2(gl) != true) {
        console.log("No WebGL2");
        Error("No WebGL2");
    }

    // Check if we have loaded the colorbar. If loaded, add one.
    if (typeof addColorbar === "function") {
        addColorbar(fragmentShaderTMin, fragmentShaderTMax);
    }

    return gl;
}

/**
 * This is the main WebGL routine. It is called when we have established a
 * context (i.e. loaded a canvas) and have loaded our shaders.
 * @param {context} gl The WebGL2 context.
 * @param {string} vs The vertex shader.
 * @param {string} fs The fragment shader.
 * @returns {undefined} Nothing
 */
function glRoutine(gl) {

    // Prepare the viewport.
    var modelMatrix = new ModelMatrix(gl);

    // var centerModel = new Float32Array(model_metadata.split(','));
    // var centerModel = model_metadata;
    var centerModel = surfaceData['nodesCenter'];
    var scaleTheWorldBy = 150;
    var tarPos = twgl.v3.mulScalar(centerModel, scaleTheWorldBy);
    var camPos = twgl.v3.create(tarPos[0], tarPos[1], 550); // Center the z-axis over the model
    var up = [0, -1, 0];

    modelMatrix.placeCamera(camPos, tarPos, up);

    // Place the center of rotation into the center of the model
    modelMatrix.translateWorld(twgl.v3.negate(centerModel));

    // Automate this...
    modelMatrix.scaleWorld(scaleTheWorldBy);

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    // Unpack shaders
    var vs_color = shaders['vert_colors'];
    var fs_color = shaders['frag_colors'];

    var vs_edge = shaders['vert_edges'];
    var fs_edge = shaders['frag_edges'];

    var vs_wireframe = shaders['vert_wireframe'];
    var fs_wireframe = shaders['frag_wireframe'];

    // Create opengl programs.
    var programInfoColor = twgl.createProgramInfo(gl, [vs_color, fs_color]);
    var programInfoEdge = twgl.createProgramInfo(gl, [vs_edge, fs_edge]);
    var programInfoWireframe = twgl.createProgramInfo(gl, [vs_wireframe, fs_wireframe]);

    var bufferInfoColor = twgl.createBufferInfoFromArrays(gl, bufferDataArray);
    var bufferInfoEdge = twgl.createBufferInfoFromArrays(gl, bufferFreeEdgesArray);
    var bufferInfoWireframe = twgl.createBufferInfoFromArrays(gl, bufferWireframeArray);

    var uniforms = {
        u_transform: twgl.m4.identity() // mat4
    };

	  gl.enable(gl.CULL_FACE);
	  gl.enable(gl.DEPTH_TEST);

    var transformationMatrix = twgl.m4.identity();

    // The main drawing loop
    function drawScene(now) {

        // Check if our data has been updated at some point.
        if (vertexDataHasChanged) {
            // Update the buffer.
            bufferInfoColor = twgl.createBufferInfoFromArrays(gl, bufferDataArray);
            bufferInfoEdge = twgl.createBufferInfoFromArrays(gl, bufferFreeEdgesArray);
            bufferInfoWireframe = twgl.createBufferInfoFromArrays(gl, bufferWireframeArray);

            // Center the new object.
            centerModel = surfaceData['nodesCenter'];
            modelMatrix.translateWorld(twgl.v3.negate(centerModel));

            vertexDataHasChanged = false;
        };

        if (fragmentDataHasChanged){
            bufferInfoColor = twgl.createBufferInfoFromArrays(gl, bufferDataArray);

            fragmentDataHasChanged = false;
        };

        // Update the model view
        uniforms.u_transform = modelMatrix.updateView();

        // colors

        gl.useProgram(programInfoColor.program);
        twgl.setBuffersAndAttributes(gl, programInfoColor, bufferInfoColor);
        twgl.setUniforms(programInfoColor, uniforms);

        twgl.drawBufferInfo(gl, bufferInfoColor);

        // edges

        gl.useProgram(programInfoEdge.program);
        twgl.setBuffersAndAttributes(gl, programInfoEdge, bufferInfoEdge);
        twgl.setUniforms(programInfoEdge, uniforms);

        twgl.drawBufferInfo(gl, bufferInfoEdge, type=gl.LINES);

        // wireframe

        gl.useProgram(programInfoWireframe.program);
        twgl.setBuffersAndAttributes(gl, programInfoWireframe, bufferInfoWireframe);
        twgl.setUniforms(programInfoWireframe, uniforms);

        twgl.drawBufferInfo(gl, bufferInfoWireframe, type=gl.LINES);

        // draw scene

        window.requestAnimationFrame(drawScene);

    }
    drawScene();
}

function HACKupdateFragmentShaderData(dataset_hash) {
    var current_scene = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
    var scene_hash = current_scene;
    var protocol = document.location.protocol;
    var host = document.location.host;
    var path = protocol + "//" + host + "/api/scenes/" + current_scene + "/" + dataset_hash + "/mesh";

    var mesh_data = getDataSourcePromise(path);

    mesh_data.then(function(value) {
        var parsed_json = JSON.parse(value);

        currentMeshHash = parsed_json['datasetMeshHash'];
        currentFieldHash = parsed_json['datasetFieldHash'];
        surfaceData['nodes'] = parsed_json['datasetSurfaceNodes'];
        surfaceData['nodesCenter'] = parsed_json['datasetSurfaceNodesCenter'];
        surfaceData['tets'] = parsed_json['datasetSurfaceTets'];
        surfaceData['wireframe'] = parsed_json['datasetSurfaceWireframe'];
        surfaceData['freeEdges'] = parsed_json['datasetSurfaceFreeEdges'];
        surfaceData['field'] = parsed_json['datasetSurfaceField'];

        var expandedSurfaceWireframe = expandDataWithIndices(
            surfaceData['wireframe'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceFreeEdges = expandDataWithIndices(
            surfaceData['freeEdges'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceTets = expandDataWithIndices(
            surfaceData['tets'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceField = expandDataWithIndices(
            surfaceData['tets'], surfaceData['field'], chunksize=1);

        var rescaledField = rescaleFieldValues(
            expandedSurfaceField,
            fragmentShaderTMin,
            fragmentShaderTMax
        );

        bufferDataArray['a_field']['data'] = new Float32Array(rescaledField);
        bufferDataArray['a_position']['data'] = expandedSurfaceTets;
        bufferWireframeArray['a_line_data']['data'] = expandedSurfaceWireframe;
        bufferFreeEdgesArray['a_line_data']['data'] = expandedSurfaceFreeEdges;

        fragmentDataHasChanged = true;

    });
}

function updateMesh(dataset_hash) {
    // Gets the current hashes for the field and geometry. If a mismatch is found the relevant routines are called
    var current_scene = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
    var scene_hash = current_scene;
    var protocol = document.location.protocol;
    var host = document.location.host;
    var path = protocol + "//" + host + "/api/scenes/" + current_scene + "/" + dataset_hash + "/mesh/hash";

    var hashes = getDataSourcePromise(path);

    hashes.then(function(value) {
        var parsed_json = JSON.parse(value);

        var newFieldHash = parsed_json['datasetFieldHash'];
        var newMeshHash = parsed_json['datasetMeshHash'];

        var vertPromise;
        var fragPromise;

        if ((newFieldHash != currentFieldHash) && (newMeshHash == currentMeshHash)) {
            fragPromise = updateFragmentShaderDataPromise(dataset_hash);
            fragPromise.then(function(value) {
                fragmentDataHasChanged = true;
            });
        }

        if ((newFieldHash == currentFieldHash) && (newMeshHash != currentMeshHash)) {
            vertPromise = updateVertexShaderDataPromise(dataset_hash);
            vertPromise.then(function(value) {
                vertexDataHasChanged = true;
            });
        }

        if ((newFieldHash != currentFieldHash) && (newMeshHash != currentMeshHash)) {
            fragPromise = updateFragmentShaderDataPromise(dataset_hash);
            vertPromise = updateVertexShaderDataPromise(dataset_hash);
            Promise.all([fragPromise, vertPromise]).then(function(value){
                fragmentDataHasChanged = true;
                vertexDataHasChanged = true;
            });
        }
    });
}

function updateFragmentShaderDataPromise(dataset_hash) {
    return new Promise(function(resolve, revoke) {
        var current_scene = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
        var scene_hash = current_scene;
        var protocol = document.location.protocol;
        var host = document.location.host;
        var path = protocol + "//" + host + "/api/scenes/" + current_scene + "/" + dataset_hash + "/mesh/field";

        var mesh_data = getDataSourcePromise(path);

        mesh_data.then(function(value) {
            var parsed_json = JSON.parse(value);

            currentFieldHash = parsed_json['datasetFieldHash'];
            surfaceData['field'] = parsed_json['datasetSurfaceField'];

            var expandedSurfaceField = expandDataWithIndices(
                surfaceData['tets'], surfaceData['field'], chunksize=1);

            var rescaledField = rescaleFieldValues(
                expandedSurfaceField,
                fragmentShaderTMin,
                fragmentShaderTMax
            );

            bufferDataArray['a_field']['data'] = new Float32Array(rescaledField);

            resolve();
        });
    });
}

function updateVertexShaderDataPromise(dataset_hash) {
    return new Promise(function(resolve, revoke) {
        var current_scene = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
        var scene_hash = current_scene;
        var protocol = document.location.protocol;
        var host = document.location.host;
        var path = protocol + "//" + host + "/api/scenes/" + current_scene + "/" + dataset_hash + "/mesh/geometry";

        var mesh_data = getDataSourcePromise(path);

        mesh_data.then(function(value) {
            var parsed_json = JSON.parse(value);

            currentMeshHash = parsed_json['datasetMeshHash'];
            surfaceData['nodes'] = parsed_json['datasetSurfaceNodes'];
            surfaceData['nodesCenter'] = parsed_json['datasetSurfaceNodesCenter'];
            surfaceData['tets'] = parsed_json['datasetSurfaceTets'];
            surfaceData['wireframe'] = parsed_json['datasetSurfaceWireframe'];
            surfaceData['freeEdges'] = parsed_json['datasetSurfaceFreeEdges'];

            var expandedSurfaceWireframe = expandDataWithIndices(
                surfaceData['wireframe'], surfaceData['nodes'], chunksize=3);

            var expandedSurfaceFreeEdges = expandDataWithIndices(
                surfaceData['freeEdges'], surfaceData['nodes'], chunksize=3);

            var expandedSurfaceTets = expandDataWithIndices(
                surfaceData['tets'], surfaceData['nodes'], chunksize=3);

            bufferDataArray['a_position']['data'] = expandedSurfaceTets;
            bufferWireframeArray['a_line_data']['data'] = expandedSurfaceWireframe;
            bufferFreeEdgesArray['a_line_data']['data'] = expandedSurfaceFreeEdges;

            resolve();
        });
    });
}

/**
 * Expand the unique vertex data to a complete set of tetraeders.
 *
 * The vertex data that is transferred between server and client is compressed
 * -- in the sense that we send each vertex only once, even if it is present in
 * more that one tetraeder.
 * Given such a compressed dataset and a dataset which maps the unique vertices
 * to a complete list of tetraeders (some index data), we expand the unique
 * vertex list to a complete list of tetraeders.
 * @param {} indices The index data.
 * @param {} data The compressed vertex data.
 * @param {} chunksize The amount of data points per vertex. For (say) a
 * temperature field this would be 1 (temperature per vertex), for actual
 * tetraeders this would be 3 (locations in 3D space, therefore 1 for each
 * coordinate).
 * @returns {array} expanded_data - A complete list of tetraeders.
 */
function expandDataWithIndices(indices, data, chunksize) {

    var expanded_data = [];
    for (index in indices) {
        for (var i = 0; i < chunksize; i++) {
            expanded_data.push(data[chunksize * indices[index] + i]);
        }
    }

    return expanded_data;
}

function averageFieldValsOverElement(fieldValues) {
    // Set the values on an element to the average of the node values.

    var averageArray = [];

    // Assume the fieldvalues are divisible by 3. This should always be the
    // case. If not then something is borked..
    for (var it = 0; it < fieldValues.length/3; it++) {
        var avgValue = fieldValues[3*it] + fieldValues[3*it+1] +
                fieldValues[3*it+2];
        avgValue = avgValue/3;
        for (var jt = 0; jt < 3; jt++) {
            averageArray.push(avgValue);
        }
    }
    return averageArray;
}

/**
 * Generate barycentric coordinates for a wireframe overlay.
 * @param {array} indices Index data used for the wireframe
 * @returns {array} barycentric_coordinates The barycentric coordinates
 */
function generateBarycentricCoordinatesFromIndices(indices) {

    var barycentric_coordinates = [];
    for (index in indices) {
        if (index % 3 == 0) {
            barycentric_coordinates.push(1., 0., 0.);
        } else if ((index - 1) % 3 == 0 ) {
            barycentric_coordinates.push(0., 1., 0.);
        } else if ((index - 2) % 3 == 0 ) {
            barycentric_coordinates.push(0., 0., 1.);
        };
    }
    return barycentric_coordinates;
}

/**
 * We scale a field so that the interval that we want to look at lies between 0
 * and 1. Note: this function does NOT return a field with values that are
 * strictly between 0 and 1. In the shader stage we simply set the colors of
 * field values outside our scope to (e.g.) black.
 * @param {} originalField The field we want to rescale.
 * @param {} minVal The lowest field value we are interested in.
 * @param {} maxVal The largest field value we are interested in.
 * @returns {array} rescaledField - The rescaled field.
 */
function rescaleFieldValues(originalField, minVal, maxVal) {

    var rescaledField = [];
    var deltaVal = maxVal - minVal;
    for (index in originalField) {
        rescaledField.push((originalField[index] - minVal)/deltaVal);
    }
    return rescaledField;
}

/**
 * Entry point for the program.
 * @returns {undefined} Nothing
 */
function main() {
    // Init WebGL.
    gl = grabCanvas("webGlCanvas");

    // testing js json parse...
	  var current_scene = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
    var protocol = document.location.protocol;
    var host = document.location.host;
    var path = protocol + "//" + host + "/api/scenes/" + current_scene;
    var active_scenes = getDataSourcePromise(path);
    active_scenes.then(function(value) {
        var parsed_json = JSON.parse(value);

        var datasets = parsed_json["loadedDatasets"];
        var dataset_hash = datasets[0]["datasetHash"];
        var dataset_mesh_path = path + "/" + dataset_hash + "/mesh";

        var mesh_data = getDataSourcePromise(dataset_mesh_path);
        mesh_data.then(function(value) {
            var parsed_json = JSON.parse(value);

            currentMeshHash = parsed_json['datasetMeshHash'];
            currentFieldHash = parsed_json['datasetFieldHash'];
            surfaceData['nodes'] = parsed_json['datasetSurfaceNodes'];
            surfaceData['nodesCenter'] = parsed_json['datasetSurfaceNodesCenter'];
            surfaceData['tets'] = parsed_json['datasetSurfaceTets'];
            surfaceData['wireframe'] = parsed_json['datasetSurfaceWireframe'];
            surfaceData['freeEdges'] = parsed_json['datasetSurfaceFreeEdges'];
            surfaceData['field'] = parsed_json['datasetSurfaceField'];

            loadShaders();
        });
    });

    // // Load the dummy data.
    // var dodec_promise = getDataSourcePromise("data/dodecahedron.json");
    // dodec_promise.then(function(value) {
    //     var parsed_json = JSON.parse(value);
    //     node_file = parsed_json['vertices'];
    //     index_file = parsed_json['indices'];
    //     timestep_data = parsed_json['colours'];
    //     console.log(node_file);
    //     console.log(index_file);
    //     console.log(timestep_data);
    //     meta_file = [0.0, 0.0, 0.0];

    //     loadShaders();
    // });

    /**
     * Load vertexshader and fragmentshader.
     */
    function loadShaders() {
        var vert_ColorShaderPromise = getDataSourcePromise(
            "shaders/vert_color_shader.glsl.c");
        var frag_ColorShaderPromise = getDataSourcePromise(
            "shaders/frag_color_shader.glsl.c");
        var vert_EdgeShaderPromise = getDataSourcePromise(
            "shaders/vertex_dataset_edge.glsl.c");
        var frag_EdgeShaderPromise = getDataSourcePromise(
            "shaders/fragment_dataset_edge.glsl.c");
        var vert_WireframeShaderPromise = getDataSourcePromise(
            "shaders/vertex_dataset_wireframe.glsl.c");
        var frag_WireframeShaderPromise = getDataSourcePromise(
            "shaders/fragment_dataset_wireframe.glsl.c");

        Promise.all([
            vert_ColorShaderPromise,
            frag_ColorShaderPromise,
            vert_EdgeShaderPromise,
            frag_EdgeShaderPromise,
            vert_WireframeShaderPromise,
            frag_WireframeShaderPromise
        ]).then(
            function(value) {
                var vert_ColorShaderSource = value[0];
                var frag_ColorShaderSource = value[1];
                var vert_EdgeShaderSource = value[2];
                var frag_EdgeShaderSource = value[3];
                var vert_WireframeShaderSource = value[4];
                var frag_WireframeShaderSource = value[5];

                shaders = {
                    vert_colors: vert_ColorShaderSource,
                    frag_colors: frag_ColorShaderSource,
                    vert_edges: vert_EdgeShaderSource,
                    frag_edges: frag_EdgeShaderSource,
                    vert_wireframe: vert_WireframeShaderSource,
                    frag_wireframe: frag_WireframeShaderSource
                };

                beginRendering();
            });
    }

    /**
     * Once we have the dodecahedron and the shaders loaded we begin the
     * rendering.
     */
    function beginRendering() {

        var expandedSurfaceWireframe = expandDataWithIndices(
            surfaceData['wireframe'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceFreeEdges = expandDataWithIndices(
            surfaceData['freeEdges'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceTets = expandDataWithIndices(
            surfaceData['tets'], surfaceData['nodes'], chunksize=3);

        var expandedSurfaceField = expandDataWithIndices(
            surfaceData['tets'], surfaceData['field'], chunksize=1);

        var rescaledField = rescaleFieldValues(
            expandedSurfaceField,
            fragmentShaderTMin,
            fragmentShaderTMax
        );

        bufferDataArray = {
            a_position: {
                numComponents: 3,
                data: expandedSurfaceTets
            },

            a_field: {
                numComponents: 1,
                type: gl.FLOAT,
                normalized: true,
                data: new Float32Array(
                    rescaledField
                )
            }
        };

        bufferWireframeArray = {
            a_line_data: {
                numComponents: 3,
                data: expandedSurfaceWireframe
            }
        };

        bufferFreeEdgesArray = {
            a_line_data: {
                numComponents: 3,
                data: expandedSurfaceFreeEdges
            }
        };

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl);
    }
};
