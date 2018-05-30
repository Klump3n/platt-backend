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

// Base path to the API
var protocol = document.location.protocol;
var host = document.location.host;
var basePath = protocol + "//" + host + "/api";

// If the websocket is not connected then the server is most likely down.
// Calls to the API will not work then so we can stop this by checking this
// variable. For the beginning set this to true...
webSocketIsConnected = true;   // global variable

// The hash for the scene we are looking at
var scene_hash = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");

// the store for all datasets rendered
var meshData = {};

// all the data required for rendering a dataset
var datasetPrototype = {

    // if this is true, the buffers will be reloaded with new data and the
    // bufferInfo is then recreated
    vertexDataHasChanged: false,
    fragmentDataHasChanged: false,

    // the hashes of the currently displayed geometry and field
    currentMeshHash: '',
    currentFieldHash: '',
    currentFieldType: '',

    // whether or not we want to change the orientation of THIS dataset
    changeThisOrientation: false,

    // the current orientation as set via mouse manipulation or via the API
    currentOrientation: twgl.m4.identity(),

    // the compressed model data as received from the api
    surfaceData: {
        "nodes": [],
        "nodesCenter": [],
        "tets": [],
        "wireframe": [],
        "freeEdges": [],
        "field": []
    },

    // bufferDataArray contains postions of tets and field values
    bufferDataArray: {
        a_position: {
            numComponents: 3,
            data: []
        },

        a_field: {
            numComponents: 1,
            // type: gl.FLOAT,
            // normalized: true,
            data: []
        }
    },

    // bufferFreeEdgesArray contains all the nodes for drawing the free edges
    // of the model
    bufferFreeEdgesArray: {
        a_line_data: {
            numComponents: 3,
            data: []
        }
    },

    // bufferWireframeArray contains all the nodes for drawing the wireframe
    // of the model
    bufferWireframeArray: {
        a_line_data: {
            numComponents: 3,
            data: []
        }
    }
};

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

    // // Check if we have loaded the colorbar. If loaded, add one.
    // if (typeof addColorbar === "function") {
    //     addColorbar(fragmentShaderTMin, fragmentShaderTMax);
    // }

    return gl;
}

/**
 * This is the main WebGL routine. It is called when we have established a
 * context (i.e. loaded a canvas) and have loaded our shaders.
 * @param {context} gl The WebGL2 context.
 */
function glRoutine(gl) {

    // Prepare the viewport.
    var centerModel,
        datasetView;

    var uniforms = {
        u_transform: twgl.m4.identity() // mat4
    };

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

    for (var dataset_index in meshData) {
        var m = meshData[dataset_index];

        centerModel = meshData[dataset_index].surfaceData['nodesCenter'];
        datasetView = new DatasetView(gl, scene_hash, dataset_index);
        meshData[dataset_index].datasetView = datasetView;

        m.bufferInfoColor = twgl.createBufferInfoFromArrays(gl, m.bufferDataArray);
        m.bufferInfoEdge = twgl.createBufferInfoFromArrays(gl, m.bufferFreeEdgesArray);
        m.bufferInfoWireframe = twgl.createBufferInfoFromArrays(gl, m.bufferWireframeArray);
    }

	  gl.enable(gl.CULL_FACE);
	  gl.enable(gl.DEPTH_TEST);

    var gl_width,
        gl_height,
        gl_view_changed = true;

    // The main drawing loop
    function drawScene(now) {

        // resize the viewport AND update the camera if the canvas has changed
        if ((gl_width != gl.canvas.clientWidth) || (gl_height != gl.canvas.clientHeight)) {
            gl_view_changed = true;
        }

        // resize the viewport
        if (gl_view_changed) {
            twgl.resizeCanvasToDisplaySize(gl.canvas);
            gl.viewport(0, 0, gl.canvas.clientWidth, gl.canvas.clientHeight);
        }

        // update every dataset
        for (var dataset_index in meshData) {
            var m = meshData[dataset_index];

            // Check if our data has been updated at some point.
            if (m.vertexDataHasChanged) {
                // Update the buffer.
                m.bufferInfoColor = twgl.createBufferInfoFromArrays(gl, m.bufferDataArray);
                m.bufferInfoEdge = twgl.createBufferInfoFromArrays(gl, m.bufferFreeEdgesArray);
                m.bufferInfoWireframe = twgl.createBufferInfoFromArrays(gl, m.bufferWireframeArray);

                m.vertexDataHasChanged = false;
            };

            if (m.fragmentDataHasChanged){
                m.bufferInfoColor = twgl.createBufferInfoFromArrays(gl, m.bufferDataArray);

                m.fragmentDataHasChanged = false;
            };

            // update the camera
            if (gl_view_changed) {
                m.datasetView.updateCamera(gl);
            }

            // change the orientation of the dataset
            m.currentOrientation = m.datasetView.updateView();
            uniforms.u_transform = m.currentOrientation;

            // colors

            gl.useProgram(programInfoColor.program);
            twgl.setBuffersAndAttributes(gl, programInfoColor, m.bufferInfoColor);
            twgl.setUniforms(programInfoColor, uniforms);

            twgl.drawBufferInfo(gl, m.bufferInfoColor);

            // edges

            gl.useProgram(programInfoEdge.program);
            twgl.setBuffersAndAttributes(gl, programInfoEdge, m.bufferInfoEdge);
            twgl.setUniforms(programInfoEdge, uniforms);

            twgl.drawBufferInfo(gl, m.bufferInfoEdge, type=gl.LINES);

            // wireframe

            gl.useProgram(programInfoWireframe.program);
            twgl.setBuffersAndAttributes(gl, programInfoWireframe, m.bufferInfoWireframe);
            twgl.setUniforms(programInfoWireframe, uniforms);

            twgl.drawBufferInfo(gl, m.bufferInfoWireframe, type=gl.LINES);
        }

        gl_width = gl.canvas.clientWidth;
        gl_height = gl.canvas.clientHeight;

        // draw scene
        window.requestAnimationFrame(drawScene);
    }

    drawScene();

}

/**
 * Gets the current hashes for the field and geometry. If a mismatch is found
 * the relevant routines are called.
 * @param {string} dataset_hash - The hash of the dataset we want to update.
 * @param {string} newFieldHash - The hash of the field being served currently.
 * @param {string} newMeshHash - The hash of the geometry being served currently.
 */
function updateMesh(dataset_hash, newFieldHash, newMeshHash) {

    var vertPromise;
    var fragPromise;

    var m = meshData[dataset_hash];

    // If we find a mismatch between the data we have and the data the
    // server currently serves we call for new data
    if ((newFieldHash != m.currentFieldHash) && (newMeshHash == m.currentMeshHash)) {
        fragPromise = updateFragmentShaderDataPromise(dataset_hash);
        fragPromise.then(function(frag_value) {
            m.fragmentDataHasChanged = true;
        });
    }

    if ((newFieldHash == m.currentFieldHash) && (newMeshHash != m.currentMeshHash)) {
        vertPromise = updateVertexShaderDataPromise(dataset_hash);
        vertPromise.then(function(vert_value) {
            m.vertexDataHasChanged = true;
        });
    }

    if ((newFieldHash != m.currentFieldHash) && (newMeshHash != m.currentMeshHash)) {
        fragPromise = updateFragmentShaderDataPromise(dataset_hash);
        vertPromise = updateVertexShaderDataPromise(dataset_hash);
        Promise.all([fragPromise, vertPromise]).then(function(frag_vert_value){
            m.fragmentDataHasChanged = true;
            m.vertexDataHasChanged = true;
        });
    }
}

// rescale the data for every dataset (we should check which one is already reset...)
function updateFragmentShaderColorbar() {

    for (var dataset_hash in meshData) {

        var m = meshData[dataset_hash];

        var expandedSurfaceField;
        if ('elemental'.localeCompare(m.currentFieldType) == 0) {
            // expand the data
            expandedSurfaceField = m.surfaceData['field'];
        } else {
            expandedSurfaceField = expandDataWithIndices(
                m.surfaceData['tets'], m.surfaceData['field'], chunksize=1);
        }

        var fragmentShaderTMin = colorbar.getCbarMin();
        var fragmentShaderTMax = colorbar.getCbarMax();

        // rescale the field values to a value between 0 and 1 (for the
        // general purpose shader)
        var rescaledField = rescaleFieldValues(
            expandedSurfaceField,
            fragmentShaderTMin,
            fragmentShaderTMax
        );

        // update the data in the buffer
        m.bufferDataArray['a_field']['data'] = new Float32Array(rescaledField);

        m.fragmentDataHasChanged = true;
    }
}

/**
 * Update the field data of the mesh.
 * @param {string} dataset_hash - Hash of the dataset.
 * @returns {promose} When the data in the bufferDataArray has been replaced the
 * promise is resolved.
 */
function updateFragmentShaderDataPromise(dataset_hash) {

    // return a promise
    return new Promise(function(resolve, revoke) {

        // get the field data from the API
        var mesh_data_promise = connectToAPIPromise(       // returns a promise on some data
            basePath = basePath,
            APIEndpoint = "scenes/" + scene_hash + "/" + dataset_hash + "/mesh/field",
            HTTPMethod = "get",
            payload = {}
        );
        mesh_data_promise.then(function(value) {

            var m = meshData[dataset_hash];

            var fieldMin = value['datasetSurfaceFieldExtrema']['fieldMin'];
            var fieldMax = value['datasetSurfaceFieldExtrema']['fieldMax'];
            colorbar.setFieldValues(dataset_hash, fieldMin, fieldMax);

            m.surfaceData['field'] = value['datasetSurfaceField'];

            var datasetFieldSelected = value['datasetFieldSelected'];
            m.currentFieldType = datasetFieldSelected['type'];

            // interpret __no_type__ as nodal
            if ('__no_type__'.localeCompare(m.currentFieldType) == 0) {
                m.currentFieldType = 'nodal';
            }

            var expandedSurfaceField;
            if ('elemental'.localeCompare(m.currentFieldType) == 0) {
                // expand the data
                expandedSurfaceField = m.surfaceData['field'];
            } else {
                expandedSurfaceField = expandDataWithIndices(
                    m.surfaceData['tets'], m.surfaceData['field'], chunksize=1);
            }

            var fragmentShaderTMin = colorbar.getCbarMin();
            var fragmentShaderTMax = colorbar.getCbarMax();

            // rescale the field values to a value between 0 and 1 (for the
            // general purpose shader)
            var rescaledField = rescaleFieldValues(
                expandedSurfaceField,
                fragmentShaderTMin,
                fragmentShaderTMax
            );

            // update the data in the buffer
            m.bufferDataArray['a_field']['data'] = new Float32Array(rescaledField);

            // update the field hash we have
            m.currentFieldHash = value['datasetFieldHash'];

            // resolve the promise
            resolve();
        });
    });
}

/**
 * Update the geometry data of the mesh. That includes the tets, nodes, free
 * edges and the wireframe.
 * @param {string} dataset_hash - The hash of the dataset.
 * @returns {promise} When the data in the different buffer arrays has been
 * replaced the promise is resolved.
 */
function updateVertexShaderDataPromise(dataset_hash) {

    // return a promise
    return new Promise(function(resolve, revoke) {

        // get the geometry data from the API
        var mesh_data_promise = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = "scenes/" + scene_hash + "/" + dataset_hash + "/mesh/geometry",
            HTTPMethod = "get",
            payload = {}
        );
        mesh_data_promise.then(function(value) {

            var m = meshData[dataset_hash];

            m.surfaceData['nodes'] = value['datasetSurfaceNodes'];
            m.surfaceData['nodesCenter'] = value['datasetSurfaceNodesCenter'];
            m.surfaceData['tets'] = value['datasetSurfaceTets'];
            m.surfaceData['wireframe'] = value['datasetSurfaceWireframe'];
            m.surfaceData['freeEdges'] = value['datasetSurfaceFreeEdges'];

            // expand the received data
            var expandedSurfaceWireframe = expandDataWithIndices(
                m.surfaceData['wireframe'], m.surfaceData['nodes'], chunksize=3);

            var expandedSurfaceFreeEdges = expandDataWithIndices(
                m.surfaceData['freeEdges'], m.surfaceData['nodes'], chunksize=3);

            var expandedSurfaceTets = expandDataWithIndices(
                m.surfaceData['tets'], m.surfaceData['nodes'], chunksize=3);

            // replace the data in the buffer arrays with the expanded data
            m.bufferDataArray['a_position']['data'] = expandedSurfaceTets;
            m.bufferWireframeArray['a_line_data']['data'] = expandedSurfaceWireframe;
            m.bufferFreeEdgesArray['a_line_data']['data'] = expandedSurfaceFreeEdges;

            // update the mesh promise we have
            m.currentMeshHash = value['datasetMeshHash'];

            // resolve the promise
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

    connectToWebSocket();

    /**
     * Load vertexshader and fragmentshader.
     */
    var vert_ColorShaderPromise = getLocalDataPromise(
        "shaders/vert_color_shader.glsl.c");
    var frag_ColorShaderPromise = getLocalDataPromise(
        "shaders/frag_color_shader.glsl.c");
    var vert_EdgeShaderPromise = getLocalDataPromise(
        "shaders/vertex_dataset_edge.glsl.c");
    var frag_EdgeShaderPromise = getLocalDataPromise(
        "shaders/fragment_dataset_edge.glsl.c");
    var vert_WireframeShaderPromise = getLocalDataPromise(
        "shaders/vertex_dataset_wireframe.glsl.c");
    var frag_WireframeShaderPromise = getLocalDataPromise(
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

            loadMeshData();
        });

    function loadMeshData() {
        var active_scenes = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = "scenes/" + scene_hash,
            HTTPMethod = "get",
            payload = {}
        );
        active_scenes.then(function(scenes_value) {
            var datasets = scenes_value["loadedDatasets"];

            // Check if we have loaded the colorbar. If loaded, add one.
            if (typeof Colorbar === "function") {
                // this is intended as a global function
                colorbar = new Colorbar(scene_hash, datasets);
            }

            var dataset_index;

            // array for all the promises waiting to be resolved
            var mesh_hash_promise_array = [];
            var mesh_data_promise_array = [];

            // append a dataset to the meshes of the scene
            for (dataset_index in datasets) {
                var dataset_hash = datasets[dataset_index]["datasetHash"];

                // What piece-of-shit language does not have an easy way to
                // deep-clone objects????
                meshData[dataset_hash] = JSON.parse(JSON.stringify(datasetPrototype));

                var mesh_hash_promise = connectToAPIPromise(
                    basePath = basePath,
                    APIEndpoint = "scenes/" + scene_hash + "/" + dataset_hash + "/mesh/hash",
                    HTTPMethod = "get",
                    payload = {}
                );
                mesh_hash_promise_array.push(mesh_hash_promise);
            }

            Promise.all(mesh_hash_promise_array).then(function(mesh_hash_values) {
                for (dataset_index in mesh_hash_values) {

                    var dataset_hash = mesh_hash_values[dataset_index].datasetMeta.datasetHash;

                    var datasetFieldPromise = updateFragmentShaderDataPromise(dataset_hash);
                    var datasetGeometryPromise = updateVertexShaderDataPromise(dataset_hash);
                    mesh_data_promise_array.push(datasetFieldPromise);
                    mesh_data_promise_array.push(datasetGeometryPromise);

                }
                Promise.all(mesh_data_promise_array).then(function() {
                    beginRendering();
                });
            });
        });
    }

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
     * Once we have the dodecahedron and the shaders loaded we begin the
     * rendering.
     */
    function beginRendering() {

        for (var dataset_index in meshData) {
            var m = meshData[dataset_index];

            var expandedSurfaceWireframe = expandDataWithIndices(
                m.surfaceData['wireframe'], m.surfaceData['nodes'], chunksize=3);

            var expandedSurfaceFreeEdges = expandDataWithIndices(
                m.surfaceData['freeEdges'], m.surfaceData['nodes'], chunksize=3);

            var expandedSurfaceTets = expandDataWithIndices(
                m.surfaceData['tets'], m.surfaceData['nodes'], chunksize=3);

            var expandedSurfaceField;
            if ('elemental'.localeCompare(m.currentFieldType) == 0) {
                // expand the data
                expandedSurfaceField = m.surfaceData['field'];
            } else {
                expandedSurfaceField = expandDataWithIndices(
                    m.surfaceData['tets'], m.surfaceData['field'], chunksize=1);
            }

            var fragmentShaderTMin = colorbar.getCbarMin();
            var fragmentShaderTMax = colorbar.getCbarMax();

            var rescaledField = rescaleFieldValues(
                expandedSurfaceField,
                fragmentShaderTMin,
                fragmentShaderTMax
            );

            m.bufferDataArray.a_position.data = expandedSurfaceTets;
            m.bufferDataArray.a_field.data = new Float32Array(rescaledField);
            m.bufferWireframeArray.a_line_data.data = expandedSurfaceWireframe;
            m.bufferFreeEdgesArray.a_line_data.data = expandedSurfaceFreeEdges;
        }

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl);
    }
};
