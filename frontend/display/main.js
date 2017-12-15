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

var model_metadata;
var surfaceNodesCenter;

var fragmentShaderTMin = 0.0;
var fragmentShaderTMax = 800.0;

var bufferIndexArray;

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

    var scaleTheWorldBy = 150;
    var tarPos = twgl.v3.mulScalar(surfaceNodesCenter, scaleTheWorldBy);
    var camPos = twgl.v3.create(tarPos[0], tarPos[1], 550); // Center the z-axis over the model
    var up = [0, -1, 0];

    modelMatrix.placeCamera(camPos, tarPos, up);

    // Place the center of rotation into the center of the model
    modelMatrix.translateWorld(twgl.v3.negate(surfaceNodesCenter));

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
    console.log('done');
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

            // Center the new object.
            centerModel = model_metadata;
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

        // // draw scene

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

        var node_file = parsed_json['datasetSurfaceNodes'];
        var index_file = parsed_json['datasetSurfaceNodesIndices'];
        var timestep_data = parsed_json['datasetSurfaceColours'];
        var meta_file = parsed_json['datasetCenterCoord'];

        var rescaledTimestepData = rescaleFieldValues(
            timestep_data,
            fragmentShaderTMin,
            fragmentShaderTMax
        );

        timestep_data = expandDataWithIndices(
            index_file,
            rescaledTimestepData,
            chunksize=1
        );

        // averageFieldValsOverElement(timestep_data);

        bufferDataArray['a_temp']['data'] = new Float32Array(timestep_data);

        fragmentDataHasChanged = true;

    });
}

/**
 * Update the data that is handled by the fragment shader. This means colour
 * data that is usually loaded for each timestep. If we additionally want to
 * change geometrical data we have to call updateVertexShaderData().
 * @param {string} object_name The object for which we want to change some data.
 * @param {string} field The dataset that gets updated.
 * @param {string} timestep The corresponding timestep.
 * @returns {undefined} Nothing
 */
function updateFragmentShaderData(object_name, field, timestep) {

    var timestep_promise = postJSONPromise(
        'api/get_timestep_data',
        {'object_name': object_name, 'field': field, 'timestep': timestep}
    );
    var timestep_data;

    timestep_promise.then(function(value){
        var rescaledTimestepData = rescaleFieldValues(
            value['timestep_data'],
            fragmentShaderTMin,
            fragmentShaderTMax
        );
        timestep_data = expandDataWithIndices(
            bufferIndexArray,
            rescaledTimestepData,
            chunksize=1
        );

        averageFieldValsOverElement(timestep_data);

        bufferDataArray['a_temp']['data'] = new Float32Array(timestep_data);

        fragmentDataHasChanged = true;
    });
}

/**
 * Update the data that is handled by the vertex shader. This means geometrical
 * data. This is usually loaded only once. If we want to change colour data we
 * have to call updateFragmentShaderData().
 * @param {string} object_name The object for which we want to change some data.
 * @param {string} field The dataset that gets updated.
 * @param {string} nodepath The path to the node file.
 * @param {string} elementpath The path to the element file.
 * @param {string} timestep The corresponding timestep.
 * @returns {undefined} Nothing
 */
function updateVertexShaderData(
    object_name, field, nodepath, elementpath, timestep) {

    var node_file;
    var meta_file;

    var timestep_data;

    var meshPromise = postJSONPromise(
        'api/mesher_init',
        {'nodepath': nodepath, 'elementpath': elementpath}
    );

    meshPromise.then(function(value){

        bufferIndexArray = value['surface_indexfile'];
        node_file = expandDataWithIndices(
            bufferIndexArray,
            value['surface_nodes'],
            chunksize=3
        );
        meta_file = value['surface_metadata'];

        var bary_coords = generateBarycentricCoordinatesFromIndices(bufferIndexArray);

        var initialTimestepDataPromise = postJSONPromise(
            'api/get_timestep_data',
            {'object_name': object_name, 'field': field, 'timestep': timestep}
        );

        initialTimestepDataPromise.then(function(value){
            var rescaledTimestepData = rescaleFieldValues(
                value['timestep_data'],
                fragmentShaderTMin,
                fragmentShaderTMax
            );
            timestep_data = expandDataWithIndices(
                bufferIndexArray,
                rescaledTimestepData,
                chunksize=1
            );

            averageFieldValsOverElement(timestep_data);

            bufferDataArray['a_position']['data'] = node_file;
            bufferDataArray['a_temp']['data'] = new Float32Array(timestep_data);
            bufferDataArray['a_bc']['data'] = bary_coords;

            model_metadata = meta_file;

            vertexDataHasChanged = true;
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

    var surfaceNodes;
    var surfaceTets;
    var surfaceWireframe;
    var surfaceFreeEdges;
    var surfaceField;

    // var node_file;
    // var index_file;
    // var meta_file;

    // var timestep_data;
    // var edges_data;

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

            surfaceNodes = parsed_json['datasetSurfaceNodes'];
            surfaceTets = parsed_json['datasetSurfaceTets'];
            surfaceNodesCenter = parsed_json['datasetSurfaceNodesCenter'];
            surfaceWireframe = parsed_json['datasetSurfaceWireframe'];
            surfaceFreeEdges = parsed_json['datasetSurfaceFreeEdges'];
            surfaceField = parsed_json['datasetSurfaceField'];

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

        // var indexSource = index_file;

        // var bary_coords = generateBarycentricCoordinatesFromIndices(
        //     indexSource);

        // var triangleSource = expandDataWithIndices(
        //     indexSource, node_file, chunksize=3);

        // var rescaledTimestepData = rescaleFieldValues(
        //     timestep_data,
        //     fragmentShaderTMin,
        //     fragmentShaderTMax
        // );

        // var temperatureSource = expandDataWithIndices(
        //     indexSource, rescaledTimestepData, chunksize=1);

        // temperatureSource = averageFieldValsOverElement(temperatureSource);

        // var metaSource = meta_file;

        // var edgeSource = expandDataWithIndices(
        //     edges_data, node_file, chunksize=3);
        var expandedSurfaceNodes = expandDataWithIndices(
            surfaceTets, surfaceNodes, chunksize=3);

        var expandedSurfaceWireframe = expandDataWithIndices(
            surfaceWireframe, surfaceNodes, chunksize=3);

        var expandedSurfaceFreeEdges = expandDataWithIndices(
            surfaceFreeEdges, surfaceNodes, chunksize=3);
        // console.log(expandedSurfaceFreeEdges);
        // gl.lineWidth(2);

        bufferDataArray = {
            a_position: {
                numComponents: 3,
                data: expandedSurfaceNodes
            },

            a_field: {
                numComponents: 1,
                type: gl.FLOAT,
                normalized: false,
                data: new Float32Array(
                    surfaceField
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

        // bufferDataArray = {
        //     // NOTE: This must be named indices or it will not work.
        //     // indices: {
        //     //     drawType: gl.DYNAMIC_DRAW,
        //     //     numComponents: 1,
        //     //     data: indexSource
        //     // },

        //     a_position: {
        //         numComponents: 3,
        //         data: triangleSource
        //     },


        //     a_bc: {
        //         numComponents: 3,
        //         data: bary_coords
        //     },
        //     a_temp: {
        //         numComponents: 1,
        //         type: gl.FLOAT,
        //         normalized: false,
        //         data: new Float32Array(
        //             temperatureSource
        //         )
        //     }
        // };

        // edgeDataArray = {
        //     a_model_edges : {
        //         numComponents: 3,
        //         // type: gl.FLOAT,
        //         // normalized: false,
        //         data: edges_data
        //     }
        // };

        // Set model metadata.
        // model_metadata = meta_file;

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl);
    }
};
