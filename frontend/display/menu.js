/**
 * @fileOverview Creates a menu to control the displayed timestep and field for
 * the displayed datasets in the scene.
 * @name menu.js
 * @author Matthias Plock (matthias.plock@bam.de)
 * @license GLPv3
 */
function main() {

    // Lay out some basic variables that won't change over the course of this script
    // Hash of the scene
    var scene_hash = document.getElementById("webGlCanvas").getAttribute("data-scene-hash");
    var protocol = document.location.protocol;
    var host = document.location.host;
    // API base path, http://IP:PORT/api
    var basePath = protocol + "//" + host + "/api";

    // Get all datasets that are loaded in this scene
    var loadedDatasets = contactServer(
        basePath = basePath,
        APIEndpoint = "scenes/" + scene_hash,
        HTTPMethod = "get",
        // payload = {}
    );
    loadedDatasets.then(function(value) {
        var datasets = value["loadedDatasets"];
        var dataset_hash = datasets[0]["datasetHash"];

        // Adds a dataset to the menu
        add_dataset(dataset_hash);
    });

    /**
     * Add a dataset to the menu.
     * @param {string} dataset_hash - The hash of the dataset we want to add to
     * the menu.
     */
    function add_dataset(dataset_hash) {
        build_menu(dataset_hash);
    }

    /**
     * Open the timestep selection menu.
     */
    function open_timestep_menu() {

        var object_name = this.getAttribute('data-name');
        var objects_timestep_menu = document.getElementById('object_timestep_menu_padding_container'+object_name);
        var object_timestep_menu_padding_container = document.getElementById('object_timestep_menu_padding_container'+object_name);

        var get_timesteps = contactServer(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + object_name + '/timesteps',
            HTTPMethod = 'get'
        );
        get_timesteps.then(function(value) {
            var timesteps = value['datasetTimestepList'];

            for (var it in timesteps) {
                var timestep_menu_item = document.createElement("div");
                timestep_menu_item.innerHTML = timesteps[it];
                timestep_menu_item.setAttribute("id", 'timestep_menu_item_'+object_name+'_'+timesteps[it]);
                timestep_menu_item.setAttribute("data-timestep", timesteps[it]);
                timestep_menu_item.setAttribute("data-name", object_name);
                // timestep_menu_item.setAttribute("class", "timestep_menu_item");
                timestep_menu_item.addEventListener('click', select_timestep);
                object_timestep_menu_padding_container.appendChild(timestep_menu_item);
            };
        });

        objects_timestep_menu.style.visibility = 'visible';
        this.removeEventListener('click', open_timestep_menu);
        this.addEventListener('click', close_timestep_menu);
    }

    function select_timestep() {
        var object_name = this.getAttribute('data-name');
        var timestep = this.getAttribute('data-timestep');
        var object_current_timestep = document.getElementById('object_timestep_current'+object_name);

        var set_timestep = contactServer(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + object_name + '/timesteps',
            'patch',
            {"datasetTimestepSelected": timestep}
        );
        set_timestep.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            object_current_timestep.innerHTML = new_ts;
            updateMesh(object_name);
        });
    }

    function decrease_timestep() {
        var object_name = this.getAttribute('data-name');
        var object_current_timestep = document.getElementById(
            'object_timestep_current'+object_name);

        var current_timestep = object_current_timestep.innerHTML;

        var patch_timesteps = contactServer(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + object_name + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_prev_timestep"}
        );
        patch_timesteps.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            object_current_timestep.innerHTML = new_ts;
            updateMesh(object_name);
        });
    }

    function increase_timestep() {
        var object_name = this.getAttribute('data-name');
        var object_current_timestep = document.getElementById(
            'object_timestep_current'+object_name);

        var current_timestep = object_current_timestep.innerHTML;

        var patch_timesteps = contactServer(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + object_name + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_next_timestep"}
        );
        patch_timesteps.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            object_current_timestep.innerHTML = new_ts;
            updateMesh(object_name);
        });
    }

    function close_timestep_menu() {
        var object_name = this.getAttribute('data-name');
        var objects_timestep_menu = document.getElementById('object_timestep_menu_padding_container'+object_name);
        objects_timestep_menu.style.visibility = 'hidden';
        this.removeEventListener('click', close_timestep_menu);
        this.addEventListener('click', open_timestep_menu);
    }

    function build_menu(dataset_hash) {

        var objects_container = document.getElementById('objects_container');

        var object_padding = document.createElement('div');
        object_padding.setAttribute('class', 'object_heading');
        object_padding.setAttribute('id', 'object_heading'+dataset_hash);

        var object = document.createElement('details');
        object.setAttribute('class', 'object');
        object.setAttribute('id', 'object'+dataset_hash);

        var object_heading = document.createElement('summary');
        object_heading.setAttribute('class', 'object_heading');
        object_heading.setAttribute('id', 'object_heading'+dataset_hash);
        object_heading.innerHTML = dataset_hash;

        var object_functions = document.createElement('div');
        object_functions.setAttribute('class', 'object_functions');
        object_functions.setAttribute('id', 'object_functions'+dataset_hash);

        var object_timestep_container = document.createElement('div');
        object_timestep_container.setAttribute('class', 'object_timestep_container');
        object_timestep_container.setAttribute('id', 'object_timestep_container'+dataset_hash);

        var object_timestep_heading = document.createElement('div');
        object_timestep_heading.setAttribute('class', 'object_timestep_heading');
        object_timestep_heading.setAttribute('id', 'object_timestep_heading'+dataset_hash);
        object_timestep_heading.innerHTML = 'Timestep';

        var object_timestep_controls = document.createElement('div');
        object_timestep_controls.setAttribute('class', 'object_timestep_controls');
        object_timestep_controls.setAttribute('id', 'object_timestep_controls'+dataset_hash);

        var object_timestep_previous = document.createElement('div');
        object_timestep_previous.setAttribute('class', 'object_timestep_previous');
        object_timestep_previous.setAttribute('id', 'object_timestep_previous'+dataset_hash);
        object_timestep_previous.setAttribute('data-name', dataset_hash);
        object_timestep_previous.innerHTML = '<';
        object_timestep_previous.addEventListener('click', decrease_timestep);

        var object_timestep_current = document.createElement('div');
        object_timestep_current.setAttribute('class', 'object_timestep_current');
        object_timestep_current.setAttribute('id', 'object_timestep_current'+dataset_hash);
        // object_timestep_current.innerHTML = '##.##';     // This is set later.
        object_timestep_current.addEventListener('click', open_timestep_menu);
        object_timestep_current.setAttribute('data-name', dataset_hash);

        var object_timestep_next = document.createElement('div');
        object_timestep_next.setAttribute('class', 'object_timestep_next');
        object_timestep_next.setAttribute('id', 'object_timestep_next'+dataset_hash);
        object_timestep_next.setAttribute('data-name', dataset_hash);
        object_timestep_next.innerHTML = '>';
        object_timestep_next.addEventListener('click', increase_timestep);

        var object_timestep_menu_padding_container = document.createElement('div');
        object_timestep_menu_padding_container.setAttribute('class', 'object_timestep_menu_padding_container');
        object_timestep_menu_padding_container.setAttribute('id', 'object_timestep_menu_padding_container'+dataset_hash);

        var object_timestep_menu = document.createElement('div');
        object_timestep_menu.setAttribute('class', 'object_timestep_menu');
        object_timestep_menu.setAttribute('id', 'object_timestep_menu'+dataset_hash);

        var object_property_container = document.createElement('div');
        object_property_container.setAttribute('class', 'object_property_container');
        object_property_container.setAttribute('id', 'object_property_container'+dataset_hash);

        var object_properties;
        var initial_timestep;

        var object_controls_container = document.createElement('div');
        object_controls_container.setAttribute('class', 'object_controls_container');
        object_controls_container.setAttribute('id', 'object_controls_container'+dataset_hash);

        var object_controls_delete_object = document.createElement('div');
        object_controls_delete_object.setAttribute('class', 'object_controls_delete_object');
        object_controls_delete_object.setAttribute('id', 'object_controls_delete_object'+dataset_hash);
        object_controls_delete_object.innerHTML = 'Delete Object';
        object_controls_delete_object.setAttribute('data-name', dataset_hash);
        object_controls_delete_object.addEventListener('click', delete_object);

        // Composing timestep control menu.
        object_timestep_controls.appendChild(object_timestep_previous);
        object_timestep_controls.appendChild(object_timestep_current);
        object_timestep_controls.appendChild(object_timestep_next);

        object_timestep_menu_padding_container.appendChild(object_timestep_menu);
        object_timestep_controls.appendChild(object_timestep_menu_padding_container);

        object_timestep_container.appendChild(object_timestep_heading);
        object_timestep_container.appendChild(object_timestep_controls);

        object_functions.appendChild(object_timestep_container);

        // Properties have been set in a loop.
        object_functions.appendChild(object_property_container);

        object_controls_container.appendChild(object_controls_delete_object);

        object_functions.appendChild(object_controls_container);

        object.appendChild(object_heading);
        object.appendChild(object_functions);

        object_padding.appendChild(object);

        objects_container.appendChild(object_padding);
    }
}
