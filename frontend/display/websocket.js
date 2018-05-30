/**
 * Tries to connect to the WebSocket for the scene. Returns a promise to do so.
 */
function connectToWebSocket() {

    // if scene_hash == 'None' -> results in 0
    if (('None'.localeCompare(scene_hash)) != 0){

        var wsProtocol = (protocol == 'http:') ? 'ws:' : 'wss:';
        var wsPath = wsProtocol + '//' + host + '/websocket/';
        var websock = new WebSocket(wsPath + scene_hash);
        var websockOpened = false;

        window.addEventListener("beforeunload", function() {
            websock.close();
        });

        websock.onopen = function() {
            console.log('WebSocket connection opened');
            websockOpened = true;
        };

        websock.onclose = function() {
            webSocketIsConnected = false;

            // to avoid this being printed in case of a failed attempt
            if (websockOpened) {
                console.log('WebSocket connection closed');
                alert(
                    'WebSocket connection closed.\n\n' +
                        'You will be able to move the existing mesh(es)\n' +
                        'around but not receive further changes/updates.'
                );
            }
        };

        websock.onmessage = function(value) {
            var msg = JSON.parse(value.data);

            var datasetHash = msg['datasetHash'];
            var update = msg['update'];

            if (update == 'orientation') {
                meshData[datasetHash].datasetView.getOrientation();
            }

            if (update == 'mesh') {
                var newHashGeometry = msg['hashes']['mesh'];
                var newHashField = msg['hashes']['field'];

                updateMesh(datasetHash, newHashField, newHashGeometry);
            }
        };

        websock.onerror = function(value) {
            console.log('WebSocket error');
        };

    } else {

        webSocketIsConnected = false;

    }
}
