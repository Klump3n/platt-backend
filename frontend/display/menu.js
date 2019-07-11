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

        var amountDatasets = 0;
        var datasets = value["loadedDatasets"];
        // var hashes = '[ ';

        // for every dataset spawn a menu entry
        for (var dataset_index in datasets) {

            if (amountDatasets > 1) {
                hashes = hashes.concat(' / ');
            }

            amountDatasets = amountDatasets + 1;
            var new_dataset = datasets[dataset_index];
            // hashes = hashes.concat(new_dataset['datasetHash'].substr(0, 7));
            new DatasetMenu(basePath, scene_hash, new_dataset);
        }

        // hashes = hashes.concat(' ]');
        document.title = '(' + amountDatasets + ') platt postprocessor';

        // colorbarSettings(datasets);
    });
}

/**
 * Set the displayed initial timestep and field for the dataset.
 */
function updateDatasetMenu(dataset_hash) {

    var dataset_current_timestep = document.getElementById('dataset_timestep_current_'+dataset_hash);
    var dataset_current_field = document.getElementById('dataset_field_current_'+dataset_hash);

    var set_timestep = connectToAPIPromise(
        basePath,
        APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/timesteps',
        'get'
    );
    set_timestep.then(function(value) {
        var currentTimestep = value["datasetTimestepSelected"];
        dataset_current_timestep.innerHTML = currentTimestep;
        dataset_current_timestep.setAttribute('title', currentTimestep);
    });

    var set_field = connectToAPIPromise(
        basePath,
        APIEndpoint = 'scenes/' + scene_hash + '/' + dataset_hash + '/fields',
        'get'
    );
    set_field.then(function(value) {
        var currentFieldType = value["datasetFieldSelected"]['type'];
        var currentFieldName = value["datasetFieldSelected"]['name'];

        var htmlString = '';

        if (currentFieldType.localeCompare('nodal') == 0) {
            htmlString = htmlString.concat('nod: ');
        }
        if (currentFieldType.localeCompare('elemental') == 0) {
            htmlString = htmlString.concat('elem: ');
        }
        if (currentFieldType.localeCompare('__no_type__') == 0) {
            htmlString = htmlString.concat('none: ');
        }

        htmlString = htmlString.concat(currentFieldName);
        dataset_current_field.innerHTML = htmlString;
        dataset_current_field.setAttribute('title', htmlString);
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
    this.currentElementset = '';

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

        var dataset_current_timestep = document.getElementById('dataset_timestep_current_'+that.dataset_hash);
        var dataset_current_field = document.getElementById('dataset_field_current_'+that.dataset_hash);
        var dataset_current_elset = document.getElementById('dataset_elset_current_'+that.dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            'get'
        );
        set_timestep.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
            dataset_current_timestep.setAttribute('title', that.currentTimestep);
        });

        var set_field = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/fields',
            'get'
        );
        set_field.then(function(value) {
            that.currentFieldType = value["datasetFieldSelected"]['type'];
            that.currentFieldName = value["datasetFieldSelected"]['name'];

            var htmlString = '';

            if (that.currentFieldType.localeCompare('nodal') == 0) {
                htmlString = htmlString.concat('nod: ');
            }
            if (that.currentFieldType.localeCompare('elemental') == 0) {
                htmlString = htmlString.concat('elem: ');
            }
            if (that.currentFieldType.localeCompare('__no_type__') == 0) {
                htmlString = htmlString.concat('none: ');
            }

            htmlString = htmlString.concat(that.currentFieldName);
            dataset_current_field.innerHTML = htmlString;
            dataset_current_field.setAttribute('title', htmlString);
        });

        var set_elset = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/elementsets',
            'get'
        );
        set_elset.then(function(value) {
            that.currentElementset = value['datasetElementsetSelected'];
            dataset_current_elset.innerHTML = that.currentElementset;
            dataset_current_elset.setAttribute('title', that.currentElementset);
        });

    }

    /**
     * Open the timestep selection menu.
     */
    function open_timestep_menu() {

        // get the dataset hash and the timestep menu and -padding container
        var dataset_hash = this.getAttribute('data-name');
        var dataset_timestep_menu = document.getElementById(
            'dataset_timestep_menu_padding_container_'+that.dataset_hash);
        var dataset_timestep_menu_padding_container = document.getElementById(
            'dataset_timestep_menu_padding_container_'+that.dataset_hash);

        // remove all the timesteps currently in the menu
        while ( dataset_timestep_menu.firstChild ) dataset_timestep_menu.removeChild( dataset_timestep_menu.firstChild );

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
                timestep_menu_item.setAttribute("title", timesteps[it]);
                timestep_menu_item.setAttribute("data-name", that.dataset_hash);
                timestep_menu_item.setAttribute("class", "dataset_timestep_menu_item");
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
        var dataset_timestep_menu_padding_container = document.getElementById('dataset_timestep_menu_padding_container_'+that.dataset_hash);
        dataset_timestep_menu_padding_container.style.visibility = 'hidden';
        this.removeEventListener('click', close_timestep_menu);
        this.addEventListener('click', open_timestep_menu);
    }

    /**
     * Select a timestep by directly selecting it from the timestep menu.
     */
    function select_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var timestep = this.getAttribute('data-timestep');
        var dataset_current_timestep = document.getElementById('dataset_timestep_current_'+that.dataset_hash);

        var set_timestep = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/timesteps',
            'patch',
            {"datasetTimestepSelected": timestep}
        );
        set_timestep.then(function(value) {
            that.currentTimestep = value["datasetTimestepSelected"];
            dataset_current_timestep.innerHTML = that.currentTimestep;
            dataset_current_timestep.setAttribute('title', that.currentTimestep);
        });
    }

    /**
     * Decrease the timestep by clicking on the 'decrease timestep' button.
     */
    function decrease_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current_'+that.dataset_hash);

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
            dataset_current_timestep.setAttribute('title', that.currentTimestep);
        });
    }

    /**
     * Increase the timestep by clicking on the 'increase timestep' button.
     */
    function increase_timestep() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_current_timestep = document.getElementById(
            'dataset_timestep_current_'+that.dataset_hash);

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
            dataset_current_timestep.setAttribute('title', that.currentTimestep);
            // updateMesh(that.dataset_hash);
        });
    }

    function open_field_menu() {
        // get the dataset hash and the timestep menu and -padding container
        var dataset_hash = this.getAttribute('data-name');
        var dataset_field_menu = document.getElementById(
            'dataset_field_menu_padding_container_'+that.dataset_hash);
        var dataset_field_menu_padding_container = document.getElementById(
            'dataset_field_menu_padding_container_'+that.dataset_hash);

        // remove all the timesteps currently in the menu
        while ( dataset_field_menu.firstChild ) dataset_field_menu.removeChild( dataset_field_menu.firstChild );

        var get_fields = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/fields',
            HTTPMethod = 'get',
            // payload = {}
        );
        get_fields.then(function(value) {
            var elementalFields = value['datasetFieldList']['elemental'];
            var nodalFields = value['datasetFieldList']['nodal'];

            var field_menu_item = document.createElement("div");
            field_menu_item.innerHTML = 'none: no field';
            field_menu_item.setAttribute("id", 'field_menu_item_'+that.dataset_hash+'_no_field');
            field_menu_item.setAttribute("data-field-type", '__no_type__');
            field_menu_item.setAttribute("data-field-name", '__no_field__');
            field_menu_item.setAttribute("title", 'none: __no_field__');
            field_menu_item.setAttribute("data-name", that.dataset_hash);
            field_menu_item.setAttribute("class", "dataset_field_menu_item");
            field_menu_item.addEventListener('click', select_field);
            dataset_field_menu_padding_container.appendChild(field_menu_item);

            for (var it in elementalFields) {
                var field_menu_item = document.createElement("div");
                field_menu_item.innerHTML = 'elem: ' + elementalFields[it];
                field_menu_item.setAttribute("id", 'field_menu_item_'+that.dataset_hash+'_'+elementalFields[it]);
                field_menu_item.setAttribute("data-field-type", 'elemental');
                field_menu_item.setAttribute("data-field-name", elementalFields[it]);
                field_menu_item.setAttribute("title", 'elemental: ' + elementalFields[it]);
                field_menu_item.setAttribute("data-name", that.dataset_hash);
                field_menu_item.setAttribute("class", "dataset_field_menu_item");
                field_menu_item.addEventListener('click', select_field);
                dataset_field_menu_padding_container.appendChild(field_menu_item);
            }

            for (var it in nodalFields) {
                var field_menu_item = document.createElement("div");
                field_menu_item.innerHTML = 'nod: ' + nodalFields[it];
                field_menu_item.setAttribute("id", 'field_menu_item_'+that.dataset_hash+'_'+nodalFields[it]);
                field_menu_item.setAttribute("data-field-type", 'nodal');
                field_menu_item.setAttribute("data-field-name", nodalFields[it]);
                field_menu_item.setAttribute("title", 'nodal: ' + nodalFields[it]);
                field_menu_item.setAttribute("data-name", that.dataset_hash);
                field_menu_item.setAttribute("class", "dataset_field_menu_item");
                field_menu_item.addEventListener('click', select_field);
                dataset_field_menu_padding_container.appendChild(field_menu_item);
            }
        });

        dataset_field_menu.style.visibility = 'visible';
        this.removeEventListener('click', open_field_menu);
        this.addEventListener('click', close_field_menu);
    }

    /**
     * Close the field selection menu.
     */
    function close_field_menu() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_field_menu_padding_container = document.getElementById('dataset_field_menu_padding_container_'+that.dataset_hash);

        dataset_field_menu_padding_container.style.visibility = 'hidden';
        this.removeEventListener('click', close_field_menu);
        this.addEventListener('click', open_field_menu);
    }

    /**
     * Select a field by directly selecting it from the field menu.
     */
    function select_field() {
        var dataset_hash = this.getAttribute('data-name');
        var fieldType = this.getAttribute('data-field-type');
        var fieldName = this.getAttribute('data-field-name');
        var dataset_current_field = document.getElementById('dataset_field_current_'+that.dataset_hash);

        var set_field = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/fields',
            'patch',
            {"datasetFieldSelected": {
                'type': fieldType,
                'name': fieldName
            }
            }
        );
        set_field.then(function(value) {
            that.currentFieldType = value["datasetFieldSelected"]['type'];
            that.currentFieldName = value["datasetFieldSelected"]['name'];

            var htmlString = '';

            if (that.currentFieldType.localeCompare('nodal') == 0) {
                htmlString = htmlString.concat('nod: ');
            }
            if (that.currentFieldType.localeCompare('elemental') == 0) {
                htmlString = htmlString.concat('elem: ');
            }
            if (that.currentFieldType.localeCompare('__no_type__') == 0) {
                htmlString = htmlString.concat('none: ');
            }

            htmlString = htmlString.concat(that.currentFieldName);
            dataset_current_field.innerHTML = htmlString;
            dataset_current_field.setAttribute('title', htmlString);
        });
    }







    function open_elset_menu() {
        // get the dataset hash and the timestep menu and -padding container
        var dataset_hash = this.getAttribute('data-name');
        var dataset_elset_menu = document.getElementById(
            'dataset_elset_menu_padding_container_'+that.dataset_hash);
        var dataset_elset_menu_padding_container = document.getElementById(
            'dataset_elset_menu_padding_container_'+that.dataset_hash);

        // remove all the timesteps currently in the menu
        while ( dataset_elset_menu.firstChild ) dataset_elset_menu.removeChild( dataset_elset_menu.firstChild );

        var get_elsets = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/elementsets',
            HTTPMethod = 'get',
            // payload = {}
        );
        get_elsets.then(function(value) {

            var elementsetList = value['datasetElementsetList'];

            for (var it in elementsetList) {
                var elset_menu_item = document.createElement("div");
                elset_menu_item.innerHTML = elementsetList[it];
                elset_menu_item.setAttribute("id", 'elset_menu_item_'+that.dataset_hash+'_'+elementsetList[it]);
                elset_menu_item.setAttribute("data-elset-name", elementsetList[it]);
                elset_menu_item.setAttribute("title", elementsetList[it]);
                elset_menu_item.setAttribute("data-name", that.dataset_hash);
                elset_menu_item.setAttribute("class", "dataset_elset_menu_item");
                elset_menu_item.addEventListener('click', select_elset);
                dataset_elset_menu_padding_container.appendChild(elset_menu_item);
            }
        });

        dataset_elset_menu.style.visibility = 'visible';
        this.removeEventListener('click', open_elset_menu);
        this.addEventListener('click', close_elset_menu);
    }

    /**
     * Close the elset selection menu.
     */
    function close_elset_menu() {
        var dataset_hash = this.getAttribute('data-name');
        var dataset_elset_menu_padding_container = document.getElementById('dataset_elset_menu_padding_container_'+that.dataset_hash);

        dataset_elset_menu_padding_container.style.visibility = 'hidden';
        this.removeEventListener('click', close_elset_menu);
        this.addEventListener('click', open_elset_menu);
    }

    /**
     * Select a elset by directly selecting it from the elset menu.
     */
    function select_elset() {
        var dataset_hash = this.getAttribute('data-name');
        var elsetName = this.getAttribute('data-elset-name');
        var dataset_current_elset = document.getElementById('dataset_elset_current_'+that.dataset_hash);

        var set_elset = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/elementsets',
            'patch',
            {"datasetElementsetSelected":
             elsetName
            }
        );
        set_elset.then(function(value) {
            that.currentElementset = value['datasetElementsetSelected'];
            dataset_current_elset.innerHTML = that.currentElementset;
            dataset_current_elset.setAttribute('title', that.currentElementset);
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

    function reset_orientation() {
        var dataset_hash = this.getAttribute('data-name');
        meshData[dataset_hash].datasetView.resetOrientation(dataset_hash);
    }

    function track_timestep_updates() {

        console.log("HE");
        var toggle_tracking = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/tracking',
            'patch',
            {}
        );
        toggle_tracking.then(function(value) {
            var trackingState = value["trackingState"];
            var tracking_dataset_id = document.getElementById('dataset_timestep_tracking_checkbox_'+that.dataset_hash);

            if (trackingState == true){
                tracking_dataset_id.checked = true;
            }
            else {
                tracking_dataset_id.checked = false;
            }
        });
    }

    function track_timestep_updates_state() {

        var toggle_tracking = connectToAPIPromise(
            basePath,
            APIEndpoint = 'scenes/' + scene_hash + '/' + that.dataset_hash + '/tracking',
            'get',
            {}
        );
        toggle_tracking.then(function(value) {
            var trackingState = value["trackingState"];
            var tracking_dataset_id = document.getElementById('dataset_timestep_tracking_checkbox_'+that.dataset_hash);

            if (trackingState == true){
                tracking_dataset_id.checked = true;
            }
            else {
                tracking_dataset_id.checked = false;
            }
        });
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

        var dataset = document.createElement('details');
        dataset.setAttribute('class', 'dataset');
        dataset.setAttribute('id', 'dataset_'+that.dataset_hash);

        var dataset_heading_hash = document.createElement('div');
        dataset_heading_hash.setAttribute('class', 'dataset_heading_hash');
        dataset_heading_hash.setAttribute('title', that.dataset_hash);
        dataset_heading_hash.innerHTML = '(' + that.dataset_hash.substr(0, 7) + ')';

        var dataset_heading = document.createElement('summary');
        dataset_heading.innerHTML = that.dataset_name;
        dataset_heading.appendChild(dataset_heading_hash);
        dataset_heading.setAttribute('class', 'dataset_heading');

        var dataset_functions = document.createElement('div');
        dataset_functions.setAttribute('class', 'dataset_functions');

        // contains heading and controls
        var dataset_timestep_container = document.createElement('div');
        dataset_timestep_container.setAttribute('class', 'dataset_function_container dataset_function_separator');

        // heading for timestep, just says 'Timestep'
        var dataset_timestep_heading = document.createElement('div');
        dataset_timestep_heading.setAttribute('class', 'dataset_function_heading');
        dataset_timestep_heading.innerHTML = 'Timestep';

        // container for the controls, contains prev, current/menu and next timestep
        var dataset_timestep_controls_container = document.createElement('div');
        dataset_timestep_controls_container.setAttribute('class', 'dataset_timestep_controls_container');

        // previous timestep box
        var dataset_timestep_previous = document.createElement('div');
        dataset_timestep_previous.setAttribute('class', 'dataset_timestep_control dataset_timestep_control_previous_next');
        dataset_timestep_previous.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_previous.setAttribute('title', 'Previous timestep');
        dataset_timestep_previous.innerHTML = '<';
        dataset_timestep_previous.addEventListener('click', decrease_timestep);

        // current timestep/menu button
        var dataset_timestep_current = document.createElement('div');
        dataset_timestep_current.setAttribute('class', 'dataset_timestep_control dataset_timestep_control_current');
        dataset_timestep_current.setAttribute('id', 'dataset_timestep_current_'+that.dataset_hash);
        dataset_timestep_current.addEventListener('click', open_timestep_menu);
        dataset_timestep_current.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_current.innerHTML = '##.##';

        // next timestep box
        var dataset_timestep_next = document.createElement('div');
        dataset_timestep_next.setAttribute('class', 'dataset_timestep_control dataset_timestep_control_previous_next');
        dataset_timestep_next.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_next.setAttribute('title', 'Next timestep');
        dataset_timestep_next.innerHTML = '>';
        dataset_timestep_next.addEventListener('click', increase_timestep);


        // timestep tracking (always update to the newest field values)
        var dataset_timestep_tracking_container = document.createElement('div');
        dataset_timestep_tracking_container.setAttribute('class', 'dataset_timestep_tracking_container');

        var dataset_timestep_tracking_checkbox = document.createElement('input');
        dataset_timestep_tracking_checkbox.setAttribute('type', 'checkbox');
        dataset_timestep_tracking_checkbox.setAttribute('data-name', that.dataset_hash);
        dataset_timestep_tracking_checkbox.setAttribute('class', 'dataset_timestep_tracking_checkbox');
        dataset_timestep_tracking_checkbox.setAttribute('id', 'dataset_timestep_tracking_checkbox_'+that.dataset_hash);
        dataset_timestep_tracking_checkbox.addEventListener('click', track_timestep_updates);

        track_timestep_updates_state();

        var dataset_timestep_tracking_label = document.createElement('label');
        dataset_timestep_tracking_label.setAttribute('for', 'dataset_timestep_tracking_checkbox_'+that.dataset_hash);
        dataset_timestep_tracking_label.setAttribute('class', 'dataset_timestep_tracking_label');
        dataset_timestep_tracking_label.setAttribute('title', 'Tick the box to follow the newest data on the cluster (if possible)');
        dataset_timestep_tracking_label.innerHTML = 'Track updates';


        var dataset_timestep_menu_padding_container = document.createElement('div');
        dataset_timestep_menu_padding_container.setAttribute('class', 'dataset_timestep_menu_padding_container');
        dataset_timestep_menu_padding_container.setAttribute('id', 'dataset_timestep_menu_padding_container_'+that.dataset_hash);

        var dataset_timestep_menu = document.createElement('div');
        dataset_timestep_menu.setAttribute('class', 'dataset_timestep_menu');

        // Composing timestep control menu.
        dataset_timestep_controls_container.appendChild(dataset_timestep_previous);
        dataset_timestep_controls_container.appendChild(dataset_timestep_current);
        dataset_timestep_controls_container.appendChild(dataset_timestep_next);

        dataset_timestep_menu_padding_container.appendChild(dataset_timestep_menu);
        dataset_timestep_controls_container.appendChild(dataset_timestep_menu_padding_container);

        dataset_timestep_tracking_container.appendChild(dataset_timestep_tracking_checkbox);
        dataset_timestep_tracking_container.appendChild(dataset_timestep_tracking_label);

        dataset_timestep_container.appendChild(dataset_timestep_heading);
        dataset_timestep_container.appendChild(dataset_timestep_controls_container);
        dataset_timestep_container.appendChild(dataset_timestep_tracking_container);

        var dataset_field_container = document.createElement('div');
        dataset_field_container.setAttribute('class', 'dataset_function_container dataset_function_separator');

        // heading for field, just says 'Field'
        var dataset_field_heading = document.createElement('div');
        dataset_field_heading.setAttribute('class', 'dataset_function_heading');
        dataset_field_heading.innerHTML = 'Field';

        var dataset_field_controls_container = document.createElement('div');

        var dataset_field_current = document.createElement('div');
        dataset_field_current.setAttribute('class', 'dataset_field_current');
        dataset_field_current.setAttribute('id', 'dataset_field_current_'+that.dataset_hash);
        dataset_field_current.addEventListener('click', open_field_menu);
        dataset_field_current.setAttribute('data-name', that.dataset_hash);
        dataset_field_current.innerHTML = 'PLACEHOLDER';

        var dataset_field_menu_padding_container = document.createElement('div');
        dataset_field_menu_padding_container.setAttribute('class', 'dataset_field_menu_padding_container');
        dataset_field_menu_padding_container.setAttribute('id', 'dataset_field_menu_padding_container_'+that.dataset_hash);

        var dataset_field_menu = document.createElement('div');
        dataset_field_menu.setAttribute('class', 'dataset_field_menu');
        dataset_field_menu.setAttribute('id', 'dataset_field_menu_'+that.dataset_hash);

        dataset_field_controls_container.appendChild(dataset_field_current);

        dataset_field_menu_padding_container.appendChild(dataset_field_menu);
        dataset_field_controls_container.appendChild(dataset_field_menu_padding_container);

        dataset_field_container.appendChild(dataset_field_heading);
        dataset_field_container.appendChild(dataset_field_controls_container);

        var dataset_elset_container = document.createElement('div');
        dataset_elset_container.setAttribute('class', 'dataset_function_container dataset_function_separator');

        // heading for elset, just says 'Elset'
        var dataset_elset_heading = document.createElement('div');
        dataset_elset_heading.setAttribute('class', 'dataset_function_heading');
        dataset_elset_heading.innerHTML = 'Elset';

        var dataset_elset_controls_container = document.createElement('div');

        var dataset_elset_current = document.createElement('div');
        dataset_elset_current.setAttribute('class', 'dataset_elset_current');
        dataset_elset_current.setAttribute('id', 'dataset_elset_current_'+that.dataset_hash);
        dataset_elset_current.addEventListener('click', open_elset_menu);
        dataset_elset_current.setAttribute('data-name', that.dataset_hash);
        dataset_elset_current.innerHTML = 'PLACEHOLDER';

        var dataset_elset_menu_padding_container = document.createElement('div');
        dataset_elset_menu_padding_container.setAttribute('class', 'dataset_field_menu_padding_container');
        dataset_elset_menu_padding_container.setAttribute('id', 'dataset_elset_menu_padding_container_'+that.dataset_hash);

        var dataset_elset_menu = document.createElement('div');
        dataset_elset_menu.setAttribute('class', 'dataset_elset_menu');
        dataset_elset_menu.setAttribute('id', 'dataset_elset_menu_'+that.dataset_hash);

        dataset_elset_controls_container.appendChild(dataset_elset_current);

        dataset_elset_menu_padding_container.appendChild(dataset_elset_menu);
        dataset_elset_controls_container.appendChild(dataset_elset_menu_padding_container);

        dataset_elset_container.appendChild(dataset_elset_heading);
        dataset_elset_container.appendChild(dataset_elset_controls_container);

        var dataset_orientation_container = document.createElement('div');
        dataset_orientation_container.setAttribute('class', 'dataset_function_container');

        // heading for orientation, just says 'Orientation'
        var dataset_orientation_heading = document.createElement('div');
        dataset_orientation_heading.setAttribute('class', 'dataset_function_heading');
        dataset_orientation_heading.innerHTML = 'Orientation';

        var dataset_change_orientation_container = document.createElement('div');
        dataset_change_orientation_container.setAttribute('class', 'dataset_change_orientation_container');

        var dataset_change_orientation_checkbox = document.createElement('input');
        dataset_change_orientation_checkbox.setAttribute('type', 'checkbox');
        dataset_change_orientation_checkbox.setAttribute('data-name', that.dataset_hash);
        dataset_change_orientation_checkbox.setAttribute('class', 'dataset_change_orientation_checkbox');
        dataset_change_orientation_checkbox.setAttribute('id', 'dataset_change_orientation_checkbox_'+that.dataset_hash);
        dataset_change_orientation_checkbox.addEventListener('click', control_orientation);

        var dataset_change_orientation_label = document.createElement('label');
        dataset_change_orientation_label.setAttribute('for', 'dataset_change_orientation_checkbox_'+that.dataset_hash);
        dataset_change_orientation_label.setAttribute('class', 'dataset_change_orientation_label');
        dataset_change_orientation_label.setAttribute('title', 'By ticking the box you can change the orientation of the dataset');
        dataset_change_orientation_label.innerHTML = 'Change';

        var dataset_reset_orientation_container = document.createElement('div');
        dataset_reset_orientation_container.setAttribute('class', 'dataset_reset_orientation_container');

        var dataset_reset_orientation_button = document.createElement('div');
        dataset_reset_orientation_button.setAttribute('data-name', that.dataset_hash);
        dataset_reset_orientation_button.setAttribute('class', 'dataset_reset_orientation_button');
        dataset_reset_orientation_button.setAttribute('title', 'Reset the orientation');
        dataset_reset_orientation_button.innerHTML = 'Reset';
        dataset_reset_orientation_button.addEventListener('click', reset_orientation);

        dataset_change_orientation_container.appendChild(dataset_change_orientation_checkbox);
        dataset_change_orientation_container.appendChild(dataset_change_orientation_label);

        dataset_reset_orientation_container.appendChild(dataset_reset_orientation_button);

        dataset_orientation_container.appendChild(dataset_orientation_heading);
        dataset_orientation_container.appendChild(dataset_change_orientation_container);
        dataset_orientation_container.appendChild(dataset_reset_orientation_container);

        dataset_functions.appendChild(dataset_timestep_container);
        dataset_functions.appendChild(dataset_field_container);
        dataset_functions.appendChild(dataset_elset_container);
        dataset_functions.appendChild(dataset_orientation_container);

        // attach heading and display to dataset
        dataset.appendChild(dataset_heading);
        dataset.appendChild(dataset_functions);

        // put dataset into padding
        dataset_padding.appendChild(dataset);

        // attach new menu to the menu list
        dataset_container.appendChild(dataset_padding);
    }
}
