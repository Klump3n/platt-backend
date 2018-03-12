/*
 * fem-gl -- getting to terms with WebGL and JavaScript
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

// Return a promise for some xhr request.
function getXHRPromise(dataFile) {
    return new Promise(function(resolve, reject) {
	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('GET', dataFile, true);
	      xhr.onload = function() {
	          if (xhr.status === 200) {
		            // Tries to get the shader source
		            resolve(xhr.responseText);
	          } else {
		            // If unsuccessful return an error
		            reject(Error('getXHRPromise() - Could not load ' + dataFile));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('getXHRPromise() - network issues'));
	      };
	      // Send the request
	      xhr.send();
    });
}

// Load the data from a file via xhr. Return a promise for this data.
function getDataSourcePromise(dataPath){
    return new Promise(function(resolve, revoke) {
        // Var that will hold the loaded string
        var dataSource;

        // Promise to load data from XHR
        var dataPromise = getXHRPromise(dataPath);

        // Promise to assign the loaded data to the source variable
        var assignDataToVar = dataPromise.then(function(value) {
            // console.log("Loading " + dataPath);
            dataSource = value;
        });

        // Once everything is loaded resolve the promise
        assignDataToVar.then(function() {
            resolve(dataSource);
        });
    });
}

// Post a string to the server and return a promise for some data.
function postDataPromise(postString) {
    // Return a promise for XHR data
    return new Promise(function(resolve, reject) {
	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('POST', postString, true);
	      xhr.onload = function() {
	          if (xhr.status === 200) {
		            // Tries to get the shader source
                var result = xhr.responseText;
		            resolve(JSON.parse(result));
	          } else {
		            // If unsuccessful return an error
		            reject(Error('postGetData() - ERROR with '+postString));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('postGetData() - network issues'));
	      };
	      // Send the request
	      xhr.send();
    });
}

// Post a json string to an url on the server and return a promise for some
// data.
function postJSONPromise(post_url, json_string) {
    // Return a promise for XHR data
    return new Promise(function(resolve, reject) {
	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('POST', '/' + post_url, true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	      // Send the request
	      xhr.send(JSON.stringify(json_string));
	      xhr.onload = function() {
	          if (xhr.status === 200) {
		            // Tries to get the shader source
                var result = xhr.responseText;
		            resolve(JSON.parse(result));
	          } else {
		            // If unsuccessful return an error
		            reject(Error('postJSONData() - ERROR with '+post_url+' and '+json_string));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('postJSONData() - network issues'));
	      };
    });
}

/**
 * Contact the server at rootPath with apiEndpoint and apply HTTPMethod with
 * optional payload.
 * @param {string} rootPath - The root path of the servers api.
 * @param {string} apiEndpoint - The API endpoint.
 * @param {string} HTTPMethod - 'GET', 'POST', 'DELETE', 'PATCH'.
 * @param {js object} payload - When POST or PATCH is used we want to transmit
 * some payload to the server. This should be a js object, such as a dictionary
 * or array.
 * @returns {object promise} A promise on a JSON object that the server was
 * contacted.
 */
function contactServer(basePath, apiEndpoint, HTTPMethod, payload) {
    return new Promise(function(resolve, revoke) {
        var xhr = new XMLHttpRequest;
        xhr.responseType = 'text';

        // Concat the complete path
        var path = basePath + '/' + apiEndpoint;

        // GET (or smth) from http://.... with async=true
        xhr.open(HTTPMethod.toUpperCase(), path, true);

        if (payload !== undefined) {
            // Set the charset
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            // Convert the payload into a JSON string
            xhr.send(JSON.stringify(payload));
        } else {
            // empty string
            xhr.send();
        }

        xhr.onload = function() {
            if (xhr.status === 200) {
		            // Tries to get the shader source
                var result = xhr.responseText;
		            resolve(JSON.parse(result));
	          } else {
		            // If unsuccessful return an error
		            reject(Error('contactServer() - ERROR with'+HTTPMethod.toUpperCase()+' '+apiEndpoint));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('contactServer() - network issues'));
        };
    });
}
