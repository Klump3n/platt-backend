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

            var new_dataset = datasets[dataset_index];
            new DatasetMenu(basePath, scene_hash, new_dataset);
        }
    });
}

/**
 * Append a new menu item for a dataset to the datasets menu
 * @param {string} basePath - The base path to the API.
 * @param {string} scene_hash - The hash of the scene.
 * @param {dict} new_dataset - A dictionary containing meta information about
 * the dataset.
 */
function DatasetMenu(basePath, scene_hash, new_dataset) {
    this.currentTimestep = '';
    this.currentFieldType = '';
    this.currentFieldName = '';

    this.dataset_name = new_dataset['datasetName'];
    this.dataset_hash = new_dataset['datasetHash'];
    this.dataset_alias = new_dataset['datasetAlias'];
    this.dataset_href = new_dataset['datasetHref'];

    // Fucking javascript
    var that = this;

    // build and attach the menu and setup the initial display
    build_menu();
    initialise_display();

    /**
     * Set the displayed initial timestep and field for the dataset.
     */
    function initialise_display() {

        var dataset_current_timestep = document.getElementById('dataset_timestep_current'+that.dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            'get'
        );
        set_timestep.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
        });
    }

    /**
     * Open the timestep selection menu.
     */
    function open_timestep_menu() {

        // get the dataset hash and the timestep menu and -padding container
        var dataset_hash = this.getAttribute('data-name');
        var dataset_timestep_menu = document.getElementById('dataset_timestep_menu_padding_container'+that.dataset_hash);
        var dataset_timestep_menu_padding_container = document.getElementById('dataset_timestep_menu_padding_container'+that.dataset_hash);

        var get_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            HTTPMethod = 'get',
            // payload = {}
        );
        get_timesteps.then(function(value) {
            var timesteps = value['datasetTimestepList'];

            for (var it in timesteps) {
                var timestep_menu_item = document.createElement("div");
                timestep_menu_item.innerHTML = timesteps[it];
                timestep_menu_item.setAttribute("id", 'timestep_menu_item_'+that.dataset_hash+'_'+timesteps[it]);
                timestep_menu_item.setAttribute("data-timestep", timesteps[it]);
                timestep_menu_item.setAttribute("data-name", that.dataset_hash);
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
        var dataset_timestep_menu = document.getElementById('dataset_timestep_menu_padding_container'+that.dataset_hash);
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
        var dataset_current_timestep = document.getElementById('dataset_timestep_current'+that.dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            'patch',
            {"datasetTimestepSelected": timestep}
        );
        set_timestep.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
            updateMesh(that.dataset_hash);
        });
    }

    /**
     * Decrease the timestep by clicking on the 'decrease timestep' button.
     */
    function decrease_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current'+that.dataset_hash);

        var current_timestep = dataset_current_timestep.innerHTML;

        var patch_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_prev_timestep"}
        );
        patch_timesteps.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
            updateMesh(that.dataset_hash);
        });
    }

    /**
     * Increase the timestep by clicking on the 'increase timestep' button.
     */
    function increase_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current'+that.dataset_hash);

        var current_timestep = dataset_current_timestep.innerHTML;

        var patch_timesteps = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            HTTPMethod = 'patch',
            payload = {"datasetTimestepSelected": "_next_timestep"}
        );
        patch_timesteps.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
            updateMesh(that.dataset_hash);
        });
    }

    /**
     * Based on a checkbox turn on/off the control of the orientation of a dataset.
     */
    function control_orientation() {
        var dataset_hash = this.getAttribute('data-name');
        if (document.getElementById(this.id).checked) {
            meshData[dataset_hash].changeThisOrientation = true;
            meshData[dataset_hash].datasetView.change_orientation = true;
        } else {
            meshData[dataset_hash].changeThisOrientation = false;
            meshData[dataset_hash].datasetView.change_orientation = false;
        }
    }

    /**
     * Adds the control menu for a dataset to the main menu dock.
     */
    function build_menu() {

        // select the dataset container in which all datasets land
        var dataset_container = document.getElementById('dataset_container');

        // a padding zone around the dataset
        var dataset_padding = document.createElement('div');
        dataset_padding.setAttribute('class', 'dataset_heading');
        dataset_padding.setAttribute('id', 'dataset_heading'+that.dataset_hash);

        var dataset = document.createElement('details');
        dataset.setAttribute('class', 'dataset');
        dataset.setAttribute('id', 'dataset'+that.dataset_hash);

        var dataset_heading = document.createElement('summary');
        dataset_heading.setAttribute('class', 'dataset_heading');
        dataset_heading.setAttribute('id', 'dataset_heading'+that.dataset_hash);
        dataset_heading.innerHTML = that.dataset_name;

        var dataset_functions = document.createElement('div');
        dataset_functions.setAttribute('class', 'dataset_functions');
        dataset_functions.setAttribute('id', 'dataset_functions'+that.dataset_hash);

        // contains heading and controls
        var dataset_timestep_container = document.createElement('div');
        dataset_timestep_container.setAttribute('class', 'dataset_timestep_container');
        dataset_timestep_container.setAttribute('id', 'dataset_timestep_container'+that.dataset_hash);

        // heading for timestep, just says 'Timestep'
        var dataset_timestep_heading = document.createElement('div');
        dataset_timestep_heading.setAttribute('class', 'dataset_timestep_heading');
        dataset_timestep_heading.setAttribute('id', 'dataset_timestep_heading'+that.dataset_hash);
        dataset_timestep_heading.innerHTML = 'Timestep';

        // container for the controls, contains prev, current/menu and next timestep
        var dataset_timestep_controls = document.createElement('div');
        dataset_timestep_controls.setAttribute('class', 'dataset_timestep_controls');
        dataset_timestep_controls.setAttribute('id', 'dataset_timestep_controls'+that.dataset_hash);

        // previous timestep box
        var dataset_timestep_previous = document.createElement('div');
        dataset_timestep_previous.setAttribute('class', 'dataset_timestep_previous');
        dataset_timestep_previous.setAttribute('id', 'dataset_timestep_previous'+that.dataset_hash);
        dataset_timestep_previous.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_previous.innerHTML = '<';
        dataset_timestep_previous.addEventListener('click', decrease_timestep);

        // current timestep/menu button
        var dataset_timestep_current = document.createElement('div');
        dataset_timestep_current.setAttribute('class', 'dataset_timestep_current');
        dataset_timestep_current.setAttribute('id', 'dataset_timestep_current'+that.dataset_hash);
        dataset_timestep_current.addEventListener('click', open_timestep_menu);
        dataset_timestep_current.setAttribute('data-name', that.dataset_hash);

        // next timestep box
        var dataset_timestep_next = document.createElement('div');
        dataset_timestep_next.setAttribute('class', 'dataset_timestep_next');
        dataset_timestep_next.setAttribute('id', 'dataset_timestep_next'+that.dataset_hash);
        dataset_timestep_next.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_next.innerHTML = '>';
        dataset_timestep_next.addEventListener('click', increase_timestep);

        var dataset_timestep_menu_padding_container = document.createElement('div');
        dataset_timestep_menu_padding_container.setAttribute('class', 'dataset_timestep_menu_padding_container');
        dataset_timestep_menu_padding_container.setAttribute('id', 'dataset_timestep_menu_padding_container'+that.dataset_hash);

        var dataset_timestep_menu = document.createElement('div');
        dataset_timestep_menu.setAttribute('class', 'dataset_timestep_menu');
        dataset_timestep_menu.setAttribute('id', 'dataset_timestep_menu'+that.dataset_hash);

        // Composing timestep control menu.
        dataset_timestep_controls.appendChild(dataset_timestep_previous);
        dataset_timestep_controls.appendChild(dataset_timestep_current);
        dataset_timestep_controls.appendChild(dataset_timestep_next);

        dataset_timestep_menu_padding_container.appendChild(dataset_timestep_menu);
        dataset_timestep_controls.appendChild(dataset_timestep_menu_padding_container);

        dataset_timestep_container.appendChild(dataset_timestep_heading);
        dataset_timestep_container.appendChild(dataset_timestep_controls);


        var dataset_change_orientation_container = document.createElement('div');
        dataset_change_orientation_container.setAttribute('class', 'dataset_change_orientation_container');

        var dataset_change_orientation_checkbox = document.createElement('input');
        dataset_change_orientation_checkbox.setAttribute('type', 'checkbox');
        dataset_change_orientation_checkbox.setAttribute('data-name', that.dataset_hash);
        dataset_change_orientation_checkbox.setAttribute('class', 'dataset_change_orientation_checkbox');
        dataset_change_orientation_checkbox.setAttribute('id', 'dataset_change_orientation_checkbox'+that.dataset_hash);
        dataset_change_orientation_checkbox.addEventListener('click', control_orientation);

        var dataset_change_orientation_label = document.createElement('label');
        dataset_change_orientation_label.setAttribute('for', 'dataset_change_orientation_checkbox'+that.dataset_hash);
        dataset_change_orientation_label.innerHTML = 'Change orientation';

        dataset_change_orientation_container.appendChild(dataset_change_orientation_checkbox);
        dataset_change_orientation_container.appendChild(dataset_change_orientation_label);

        dataset_functions.appendChild(dataset_timestep_container);
        dataset_functions.appendChild(dataset_change_orientation_container);

        // attach heading and display to dataset
        dataset.appendChild(dataset_heading);
        dataset.appendChild(dataset_functions);

        // put dataset into padding
        dataset_padding.appendChild(dataset);

        // attach new menu to the menu list
        dataset_container.appendChild(dataset_padding);
    }
}
