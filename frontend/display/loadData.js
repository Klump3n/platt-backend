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


/**
 * Load some data that is already on the web server, such as shaders or dummy
 * mesh data. The difference to the connectToAPIPromise method is that we
 * expect to read something which does not have to be converted into JSON.
 * @param {string} dataPath - The path to the file we want to load.
 * @returns {string, object} The contents of the file we want to load. This can
 * be JSON or just a long string.
 */
function getLocalDataPromise(dataPath){

    // return a promise
    return new Promise(function(resolve, reject) {

	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('GET', dataPath, true);
        xhr.send();

	      xhr.onload = function() {
	          if (xhr.status === 200) {

                // on success load the data and return it via the promise
                var data = xhr.responseText;
		            resolve(data);

	          } else {

		            // If unsuccessful return an error
		            reject(Error('getXHRPromise() - Could not load ' + dataPath));
	          }
	      };

	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('getXHRPromise() - network issues'));
	      };
    });
}

/**
 * Contact the server at rootPath with apiEndpoint and apply HTTPMethod with
 * optional payload. It is expected that the API returns a string of sorts,
 * which then has to be converted into a JSON valid object.
 * @param {string} basePath - The root path of the servers api.
 * @param {string} apiEndpoint - The API endpoint.
 * @param {string} HTTPMethod - 'GET', 'POST', 'DELETE', 'PATCH'.
 * @param {js object} payload - When POST or PATCH is used we want to transmit
 * some payload to the server. This should be a js object, such as a dictionary
 * or array.
 * @returns {object promise} A promise on a JSON object that the server was
 * contacted.
 */
function connectToAPIPromise(basePath, apiEndpoint, HTTPMethod, payload) {

    // return a promise on data
    return new Promise(function(resolve, reject) {

        // global variable set in main.js
        if (window.webSocketIsConnected == false) {

            reject(Error('WebSocket connection is closed'));

        } else {

            var xhr = new XMLHttpRequest;
            xhr.responseType = 'text';

            // Concat the complete path
            var path = basePath + '/' + apiEndpoint;

            // GET (or smth else) from http://.... with async=true
            xhr.open(HTTPMethod.toUpperCase(), path, true);

            // In case no payload is supplied
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
		                reject(Error('connectToAPIPromise() - ERROR with '+HTTPMethod.toUpperCase()+' '+apiEndpoint));
	              }
	          };
	          xhr.onerror = function() {
	              // Maybe we have more severe problems. Also return an error then
	              reject(Error('connectToAPIPromise() - network issues'));
            };
        }
    });
}
