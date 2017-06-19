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
var model_metadata;

var fragmentShaderTMin = 100.0;
var fragmentShaderTMax = 1000.0;

var bufferIndexArray;

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

    addColorbar(fragmentShaderTMin, fragmentShaderTMax);

    return gl;
}

// This is called with established context and shaders loaded
function glRoutine(gl, vs, fs) {

    // Prepare the viewport.
    var modelMatrix = new ModelMatrix(gl);

    // var centerModel = new Float32Array(model_metadata.split(','));
    var centerModel = model_metadata;

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

    // var fbo = twgl.createFramebufferInfo(gl);
    // twgl.bindFramebufferInfo(gl);
    // twgl.resizeFramebufferInfo(gl, fbo);


    // Create opengl programs.
    var programInfo = twgl.createProgramInfo(gl, [vs, fs]);

    var bufferInfo = twgl.createBufferInfoFromArrays(gl, bufferDataArray);

    var uniforms = {
        u_transform: twgl.m4.identity() // mat4
    };

	  gl.enable(gl.CULL_FACE);
	  gl.enable(gl.DEPTH_TEST);

    var transformationMatrix = twgl.m4.identity();

    function drawScene(now) {

        // Check if our data has been updated at some point.
        if (vertexDataHasChanged) {
            // Update the buffer.
            bufferInfo = twgl.createBufferInfoFromArrays(gl, bufferDataArray);

            // Center the new object.
            centerModel = model_metadata;
            modelMatrix.translateWorld(twgl.v3.negate(centerModel));

            vertexDataHasChanged = false;
        } else if (fragmentDataHasChanged){
            bufferInfo = twgl.createBufferInfoFromArrays(gl, bufferDataArray);
            fragmentDataHasChanged = false;
        };

        // Update the model view
        uniforms.u_transform = modelMatrix.updateView();

        gl.useProgram(programInfo.program);
        twgl.setBuffersAndAttributes(gl, programInfo, bufferInfo);
        twgl.setUniforms(programInfo, uniforms);
        twgl.drawBufferInfo(gl, bufferInfo);

        window.requestAnimationFrame(drawScene);

    }
    drawScene();
}

function updateFragmentShaderData(object_name, field, timestep) {
    var timestep_promise = postJSONPromise(
        'get_timestep_data',
        {'object_name': object_name, 'field': field, 'timestep': timestep}
    );
    // var timestep_promise = postDataPromise(
    //     '/get_timestep_data?object_name=' + object_name +
    //         '&field=' + field + '&timestep='+timestep);
    var timestep_data;

    timestep_promise.then(function(value){
        var normalisedTimestepData = normaliseFieldValues(
            value['timestep_data'],
            fragmentShaderTMin,
            fragmentShaderTMax
        );
        timestep_data = expandDataWithIndices(
            bufferIndexArray,
            normalisedTimestepData,
            chunksize=1
        );

        averageFieldValsOverElement(timestep_data);

        bufferDataArray['a_temp']['data'] = new Float32Array(timestep_data);

        fragmentDataHasChanged = true;
    });
}

function updateVertexShaderData(object_name, field, nodepath, elementpath, timestep) {

    var node_file;
    var meta_file;

    var timestep_data;

    var meshPromise = postJSONPromise(
        'mesher_init',
        {'nodepath': nodepath, 'elementpath': elementpath}
    );
    // var meshPromise = postDataPromise('/mesher_init?nodepath='+nodepath+'&elementpath='+elementpath);

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
            'get_timestep_data',
            {'object_name': object_name, 'field': field, 'timestep': timestep}
        );
        // var initialTimestepDataPromise = postDataPromise(
        //     '/get_timestep_data?object_name=' + object_name +
        //         '&field=' + field + '&timestep='+timestep);

        initialTimestepDataPromise.then(function(value){
            var normalisedTimestepData = normaliseFieldValues(
                value['timestep_data'],
                fragmentShaderTMin,
                fragmentShaderTMax
            );
            timestep_data = expandDataWithIndices(
                bufferIndexArray,
                normalisedTimestepData,
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

function expandDataWithIndices(indices, data, chunksize) {
    // Given some index data for a non-redundant vertex array, expand this
    // vertex array data so we don't need the index data.

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
        var avgValue = fieldValues[3*it] + fieldValues[3*it+1] + fieldValues[3*it+2];
        avgValue = avgValue/3;
        for (var jt = 0; jt < 3; jt++) {
            averageArray.push(avgValue);
        }
    }
    return averageArray;
}

function generateBarycentricCoordinatesFromIndices(indices) {
    // Generate barycentric coordinates from a given set of indices.
    // This is for generation of a wireframe mesh overlay.

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

function normaliseFieldValues(originalField, minVal, maxVal) {
    // Normalise the fieldvalues between 0 and 1.
    var normalisedField = [];
    var deltaVal = maxVal - minVal;
    for (index in originalField) {
        normalisedField.push((originalField[index] - minVal)/deltaVal);
    }
    return normalisedField;
}

function main() {
    // Init WebGL.
    gl = grabCanvas("webGlCanvas");

    var node_file;
    var index_file;
    var meta_file;

    var timestep_data;

    var dodec_promise = getDataSourcePromise("data/dodecahedron.json");
    dodec_promise.then(function(value) {
        var parsed_json = JSON.parse(value);
        node_file = parsed_json['vertices'];
        index_file = parsed_json['indices'];
        timestep_data = parsed_json['colours'];
        meta_file = [0.0, 0.0, 0.0];

        loadShaders();
    });

    var vertexShaderSource;
    var fragmentShaderSource;

    function loadShaders() {
        var vertexShaderPromise = getDataSourcePromise("shaders/vertexShader.glsl.c");
        var fragmentShaderPromise = getDataSourcePromise("shaders/fragmentShader.glsl.c");

        Promise.all([vertexShaderPromise, fragmentShaderPromise]).then(function(value) {
            vertexShaderSource = value[0];
            fragmentShaderSource = value[1];

            beginRendering();
        });
    }

    function beginRendering() {


        var indexSource = index_file;

        var bary_coords = generateBarycentricCoordinatesFromIndices(indexSource);

        var triangleSource = expandDataWithIndices(indexSource, node_file, chunksize=3);
        var normalisedTimestepData = normaliseFieldValues(
            timestep_data,
            fragmentShaderTMin,
            fragmentShaderTMax
        );
        var temperatureSource = expandDataWithIndices(indexSource, normalisedTimestepData, chunksize=1);
        // temperatureSource = averageFieldValsOverElement(temperatureSource);
        var metaSource = meta_file;

        bufferDataArray = {
            // indices: {              // NOTE: This must be named indices or it will not work.
            //     drawType: gl.DYNAMIC_DRAW,
            //     numComponents: 1,
            //     data: indexSource
            // },
            a_position: {
                numComponents: 3,
                data: triangleSource
            },
            a_bc: {
                numComponents: 3,
                data: bary_coords
            },
            a_temp: {
                numComponents: 1,
                type: gl.FLOAT,
                normalized: false,
                data: new Float32Array(
                    temperatureSource
                )
            }
        };

        // Set model metadata.
        model_metadata = meta_file;

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl,
                  vertexShaderSource, fragmentShaderSource,
                  metaSource
                 );
    }
};
