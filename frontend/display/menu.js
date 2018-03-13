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
    // API base path, http(s)://IP:PORT/api
    var basePath = protocol + "//" + host + "/api";

    // Get all datasets that are loaded in this scene
    var loadedDatasets = connectToAPIPromise(       // returns a promise on some data
        basePath = basePath,                  // http(s)://host:ip/api
        APIEndpoint = "scenes/" + scene_hash, // scenes/123ab..[40]
        HTTPMethod = "get",                   // get, post, patch, delete
        // payload = {}                       // {'key': 'value'}, not a string
    );
    loadedDatasets.then(function(value) {

        var datasets = value["loadedDatasets"];

        // for every dataset spawn a menu entry
        for (var dataset_index in datasets) {

            var dataset_hash = datasets[dataset_index]["datasetHash"];

            // Add the dataset to the menu
            add_dataset(dataset_hash);

            // initialise the displayed values for each dataset
            initialise_display(dataset_hash);
        }
    });


    /**
     * Set the displayed initial timestep and field for the given dataset.
     * @param {string} dataset_hash - The hash of the dataset.
     */
    function initialise_display(dataset_hash) {

        var dataset_current_timestep = document.getElementById('dataset_timestep_current'+dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
            'get'
        );
        set_timestep.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = new_ts;
        });
    }

    /**
     * Open the timestep selection menu.
     */
    function open_timestep_menu() {

        // get the dataset hash and the timestep menu and -padding container
        var dataset_hash = this.getAttribute('data-name');
        var dataset_timestep_menu = document.getElementById('dataset_timestep_menu_padding_container'+dataset_hash);
        var dataset_timestep_menu_padding_container = document.getElementById('dataset_timestep_menu_padding_container'+dataset_hash);

        var get_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
            HTTPMethod = 'get',
            // payload = {}
        );
        get_timesteps.then(function(value) {
            var timesteps = value['datasetTimestepList'];

            for (var it in timesteps) {
                var timestep_menu_item = document.createElement("div");
                timestep_menu_item.innerHTML = timesteps[it];
                timestep_menu_item.setAttribute("id", 'timestep_menu_item_'+dataset_hash+'_'+timesteps[it]);
                timestep_menu_item.setAttribute("data-timestep", timesteps[it]);
                timestep_menu_item.setAttribute("data-name", dataset_hash);
                // timestep_menu_item.setAttribute("class", "timestep_menu_item");
                timestep_menu_item.addEventListener('click', select_timestep);
                dataset_timestep_menu_padding_container.appendChild(timestep_menu_item);
            };
        });

        dataset_timestep_menu.style.visibility = 'visible';
        this.removeEventListener('click', open_timestep_menu);
        this.addEventListener('click', close_timestep_menu);
    }

    /**
     * Close the timestep selection menu.
     */
    function close_timestep_menu() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_timestep_menu = document.getElementById('dataset_timestep_menu_padding_container'+dataset_hash);
        dataset_timestep_menu.style.visibility = 'hidden';
        this.removeEventListener('click', close_timestep_menu);
        this.addEventListener('click', open_timestep_menu);
    }

    /**
     * Select a timestep by directly selecting it from the timestep menu.
     */
    function select_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var timestep = this.getAttribute('data-timestep');
        var dataset_current_timestep = document.getElementById('dataset_timestep_current'+dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
            'patch',
            {"datasetTimestepSelected": timestep}
        );
        set_timestep.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = new_ts;
            updateMesh(dataset_hash);
        });
    }

    /**
     * Decrease the timestep by clicking on the 'decrease timestep' button.
     */
    function decrease_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current'+dataset_hash);

        var current_timestep = dataset_current_timestep.innerHTML;

        var patch_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_prev_timestep"}
        );
        patch_timesteps.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = new_ts;
            updateMesh(dataset_hash);
        });
    }

    /**
     * Increase the timestep by clicking on the 'increase timestep' button.
     */
    function increase_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current'+dataset_hash);

        var current_timestep = dataset_current_timestep.innerHTML;

        var patch_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_next_timestep"}
        );
        patch_timesteps.then(function(value) {
            var new_ts = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = new_ts;
            updateMesh(dataset_hash);
        });
    }

    /**
     * Adds the control menu for a dataset to the main menu dock.
     * @param {string} dataset_hash - The hash of the dataset for which the menu should be.
     */
    function add_dataset(dataset_hash) {

        var dataset_container = document.getElementById('dataset_container');

        var dataset_padding = document.createElement('div');
        dataset_padding.setAttribute('class', 'dataset_heading');
        dataset_padding.setAttribute('id', 'dataset_heading'+dataset_hash);

        var dataset = document.createElement('details');
        dataset.setAttribute('class', 'dataset');
        dataset.setAttribute('id', 'dataset'+dataset_hash);

        var dataset_heading = document.createElement('summary');
        dataset_heading.setAttribute('class', 'dataset_heading');
        dataset_heading.setAttribute('id', 'dataset_heading'+dataset_hash);
        dataset_heading.innerHTML = dataset_hash;

        var dataset_functions = document.createElement('div');
        dataset_functions.setAttribute('class', 'dataset_functions');
        dataset_functions.setAttribute('id', 'dataset_functions'+dataset_hash);

        var dataset_timestep_container = document.createElement('div');
        dataset_timestep_container.setAttribute('class', 'dataset_timestep_container');
        dataset_timestep_container.setAttribute('id', 'dataset_timestep_container'+dataset_hash);

        var dataset_timestep_heading = document.createElement('div');
        dataset_timestep_heading.setAttribute('class', 'dataset_timestep_heading');
        dataset_timestep_heading.setAttribute('id', 'dataset_timestep_heading'+dataset_hash);
        dataset_timestep_heading.innerHTML = 'Timestep';

        var dataset_timestep_controls = document.createElement('div');
        dataset_timestep_controls.setAttribute('class', 'dataset_timestep_controls');
        dataset_timestep_controls.setAttribute('id', 'dataset_timestep_controls'+dataset_hash);

        var dataset_timestep_previous = document.createElement('div');
        dataset_timestep_previous.setAttribute('class', 'dataset_timestep_previous');
        dataset_timestep_previous.setAttribute('id', 'dataset_timestep_previous'+dataset_hash);
        dataset_timestep_previous.setAttribute('data-name', dataset_hash);
        dataset_timestep_previous.innerHTML = '<';
        dataset_timestep_previous.addEventListener('click', decrease_timestep);

        var dataset_timestep_current = document.createElement('div');
        dataset_timestep_current.setAttribute('class', 'dataset_timestep_current');
        dataset_timestep_current.setAttribute('id', 'dataset_timestep_current'+dataset_hash);
        // dataset_timestep_current.innerHTML = '##.##';     // This is set later.
        dataset_timestep_current.addEventListener('click', open_timestep_menu);
        dataset_timestep_current.setAttribute('data-name', dataset_hash);

        var dataset_timestep_next = document.createElement('div');
        dataset_timestep_next.setAttribute('class', 'dataset_timestep_next');
        dataset_timestep_next.setAttribute('id', 'dataset_timestep_next'+dataset_hash);
        dataset_timestep_next.setAttribute('data-name', dataset_hash);
        dataset_timestep_next.innerHTML = '>';
        dataset_timestep_next.addEventListener('click', increase_timestep);

        var dataset_timestep_menu_padding_container = document.createElement('div');
        dataset_timestep_menu_padding_container.setAttribute('class', 'dataset_timestep_menu_padding_container');
        dataset_timestep_menu_padding_container.setAttribute('id', 'dataset_timestep_menu_padding_container'+dataset_hash);

        var dataset_timestep_menu = document.createElement('div');
        dataset_timestep_menu.setAttribute('class', 'dataset_timestep_menu');
        dataset_timestep_menu.setAttribute('id', 'dataset_timestep_menu'+dataset_hash);

        // var dataset_property_container = document.createElement('div');
        // dataset_property_container.setAttribute('class', 'dataset_property_container');
        // dataset_property_container.setAttribute('id', 'dataset_property_container'+dataset_hash);

        // var dataset_controls_container = document.createElement('div');
        // dataset_controls_container.setAttribute('class', 'dataset_controls_container');
        // dataset_controls_container.setAttribute('id', 'dataset_controls_container'+dataset_hash);

        // Composing timestep control menu.
        dataset_timestep_controls.appendChild(dataset_timestep_previous);
        dataset_timestep_controls.appendChild(dataset_timestep_current);
        dataset_timestep_controls.appendChild(dataset_timestep_next);

        dataset_timestep_menu_padding_container.appendChild(dataset_timestep_menu);
        dataset_timestep_controls.appendChild(dataset_timestep_menu_padding_container);

        dataset_timestep_container.appendChild(dataset_timestep_heading);
        dataset_timestep_container.appendChild(dataset_timestep_controls);

        dataset_functions.appendChild(dataset_timestep_container);

        // Properties have been set in a loop.
        // dataset_functions.appendChild(dataset_property_container);

        // dataset_functions.appendChild(dataset_controls_container);

        dataset.appendChild(dataset_heading);
        dataset.appendChild(dataset_functions);

        dataset_padding.appendChild(dataset);

        dataset_container.appendChild(dataset_padding);
    }
}
