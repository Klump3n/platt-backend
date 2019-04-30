function Colorbar(sceneHash, datasets) {

    var cbarMin = 0;
    var cbarMax = 800;

    var defaultBullet = "";   // hash, current or values
    var defaultBulletId = "";

    var currentMin = 0;
    var currentMax = 0;

    var valuesMin = 0;
    var valuesMax = 0;

    var fieldValues = {};

    initColorbar();

    // sometimes we dont want to patch information to the server, e.g. when we
    // just received an update
    var patchServer = false;

    // When we patch the server we will get a message via websocket which tells
    // us to update. We dont want to do that.
    var pollServer = true;

    // public functions
    //
    // get the min and max values from the colorbar
    this.getCbarMin = function() {
        return cbarMin;
    };

    this.getCbarMax = function() {
        return cbarMax;
    };

    this.setFieldValues = function(dataset_hash, fieldMin, fieldMax) {

        // update the field values in either case
        fieldValues[dataset_hash] = {'min': fieldMin, 'max': fieldMax};

        // if the updated field is being tracked
        if (defaultBullet.localeCompare(dataset_hash) == 0) {

            if ((fieldMin != cbarMin) || (fieldMax != cbarMax)) {

                cbarMin = fieldMin;
                cbarMax = fieldMax;

                // patch information to the server and ignore the websocket
                // update instruction
                patchServer = true;
                pollServer = false;

                updateShader();

            }
        }
    };

    this.updateColorbarMenu = function() {

        if (!(pollServer)) {

            // catch the next polling
            pollServer = true;

        } else {

            var serverColorbar = getServerColorbarPromise();
            serverColorbar.then(function(value) {

                var colorbar_selected = value.selected;

                defaultBullet = colorbar_selected;
                defaultBulletId = ('colorbar_select_' + defaultBullet);

                var newDefaultBulletElement = document.getElementById(defaultBulletId);
                newDefaultBulletElement.setAttribute('checked', 'checked');

                currentMin = value.current.min;
                currentMax = value.current.max;
                valuesMin = value.values.min;
                valuesMax = value.values.max;

                var cbar_sub_start = document.getElementById('colorbar_form_sub_start');
                cbar_sub_start.value = valuesMin;
                var cbar_sub_end = document.getElementById('colorbar_form_sub_end');
                cbar_sub_end.value = valuesMax;

                if ("values".localeCompare(colorbar_selected) == 0) {
                    cbarMin = valuesMin;
                    cbarMax = valuesMax;
                } else if ("current".localeCompare(colorbar_selected) == 0) {
                    cbarMin = currentMin;
                    cbarMax = currentMax;
                } else {
                    cbarMin = fieldValues[defaultBullet]['min'];
                    cbarMax = fieldValues[defaultBullet]['max'];
                }

                addColorbar(update=true);
                updateFragmentShaderColorbar();

            });
        }
    };

    // private functions
    //
    // init the class
    function initColorbar() {

        var serverColorbar = getServerColorbarPromise();
        serverColorbar.then(function(value) {

            var colorbar_selected = value.selected;

            if (colorbar_selected == null) {

                defaultBullet = datasets[0]['datasetHash'];

            } else {

                defaultBullet = colorbar_selected;

                // if we dont init the server we dont have to patch it
                patchServer = false;

            }

            defaultBulletId = ('colorbar_select_' + defaultBullet);

            currentMin = value.current.min;
            currentMax = value.current.max;
            valuesMin = value.values.min;
            valuesMax = value.values.max;

            if ("values".localeCompare(colorbar_selected) == 0) {
                cbarMin = valuesMin;
                cbarMax = valuesMax;
            }

            if ("current".localeCompare(colorbar_selected) == 0) {
                cbarMin = currentMin;
                cbarMax = currentMax;
            }

            addColorbar();
            createColorbarMenu();

        });
    }

    function updateServerColorbar() {

        var colorbar_settings = {
            'selected': defaultBullet,
            'current': {'min': currentMin, 'max': currentMax},
            'values': {'min': valuesMin, 'max': valuesMax}
        };

        // patching will initiate a websocket message to everyone (also US!).
        // we dont need to respond to this message, so dont poll data from the
        // server for once
        if (patchServer) {
            patchServerColorbarPromise(colorbar_settings);
            patchServer = false;
        }
    }

    // call a function in the main code...
    function updateShader() {

        if ("values".localeCompare(defaultBullet) == 0) {
            cbarMin = valuesMin;
            cbarMax = valuesMax;
        } else if ("current".localeCompare(defaultBullet) == 0) {
            cbarMin = currentMin;
            cbarMax = currentMax;
        } else {
            cbarMin = fieldValues[defaultBullet]['min'];
            cbarMax = fieldValues[defaultBullet]['max'];
        }

        updateServerColorbar();
        addColorbar(update=true);
        updateFragmentShaderColorbar();

    }

    function getServerColorbarPromise() {

        var serverColorbarPromise = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = "scenes/" + sceneHash + "/colorbar",
            HTTPMethod = "get",
            payload = {}
        );

        return serverColorbarPromise;

    }

    function patchServerColorbarPromise(colorbar_settings) {

        var serverColorbarPromise = connectToAPIPromise(
            basePath = basePath,
            APIEndpoint = "scenes/" + sceneHash + "/colorbar",
            HTTPMethod = "patch",
            payload = colorbar_settings
        );

        return serverColorbarPromise;

    }

    // transmit which bullet is selected
    function bulletSelector() {

        var newBullet = this.getAttribute('data-bullet');

        // do nothing if nothing has to change
        if (newBullet.localeCompare(defaultBullet) == 0 ) {
            return;

        } else {
            // remove the old one
            var oldDefaultBulletElement = document.getElementById(defaultBulletId);
            oldDefaultBulletElement.removeAttribute('checked');

            defaultBullet = newBullet;
            defaultBulletId = ('colorbar_select_' + defaultBullet);

            var newDefaultBulletElement = document.getElementById(defaultBulletId);
            newDefaultBulletElement.setAttribute('checked', 'checked');

            if ("current".localeCompare(defaultBullet) == 0) {
                currentMin = cbarMin;
                currentMax = cbarMax;
            }

            // patch information to the server and ignore the websocket
            // update instruction
            patchServer = true;
            pollServer = false;

            updateShader();
        }
    }

    // select the values to lock to
    function valueSelector() {
        var minOrMax = this.getAttribute('data-valuesMinMax');
        var value = this.value;

        // delete everything that is not a number
        if (isNaN(value)) {
            this.value = "";

        } else {
            if ("valuesMin".localeCompare(minOrMax) == 0) {
                valuesMin = Number(value);
                if ("values".localeCompare(defaultBullet) == 0) {
                    cbarMin = valuesMin;
                }
            }
            if ("valuesMax".localeCompare(minOrMax) == 0) {
                valuesMax = Number(value);
                if ("values".localeCompare(defaultBullet) == 0) {
                    cbarMax = valuesMax;
                }
            }

            // patch information to the server and ignore the websocket
            // update instruction
            patchServer = true;
            pollServer = false;

            updateShader();
        }
    }

    function addColorbar(update=false) {

        // Look for the element with Id 'colorbar'
        var cbar = document.getElementById('colorbar');

        // delete the old stuff first if we update it
        if (update) {
            while (cbar.firstChild) {
                cbar.removeChild(cbar.firstChild);
            }
        }

        // The intervals for displaying the colorbar
        var intervals = [
            1.0,
            0.9523809523809523,
            0.9047619047619047,
            0.8571428571428571,
            0.8095238095238095,
            0.7619047619047619,
            0.7142857142857142,
            0.6666666666666666,
            0.6190476190476191,
            0.5714285714285714,
            0.5238095238095237,
            0.47619047619047616,
            0.42857142857142855,
            0.38095238095238093,
            0.3333333333333333,
            0.2857142857142857,
            0.23809523809523808,
            0.19047619047619047,
            0.14285714285714285,
            0.09523809523809523,
            0.047619047619047616,
            0.0
        ];

        // Based upon our given Tmin and Tmax we assign temperatures to the
        // intervals

        // this is for the decimal points, so we dont end up having a certain
        // number in the colorbar more than once
        var log10Dist = Math.floor(Math.log10(Math.abs(cbarMax - cbarMin) / 21));
        var n = 0;
        if (log10Dist < 0) {
            n = -log10Dist;
        }

        function roundTo(value, decimals) {
            return Math.round(cbarValue * 10**decimals) / 10**decimals;
        };

        var colorbarText = [];
        for (var index in intervals) {
            var cbarValue = (intervals[index]*(cbarMax - cbarMin) + cbarMin);
            colorbarText.push(roundTo(cbarValue, n));
        }

        var colors = [
            '#bf0000',
            '#df4000',
            '#ff8000',
            '#ffbf00',
            '#ffff00',
            '#d4ea00',
            '#aad400',
            '#7fbf00',
            '#55aa00',
            '#2b9500',
            '#008000',
            '#009f1a',
            '#00bf33',
            '#00df4c',
            '#00ff66',
            '#00bf80',
            '#008099',
            '#0040b2',
            '#0000cc',
            '#3300ff',
            '#8000ff'
        ];

        // The first colorbar segment for every temperature above Tmax
        var div = document.createElement('div');
        div.setAttribute('class', 'colorbar_field');
        div.setAttribute('style', 'background-color: #FFFFFF');
        var divText = document.createElement('div');
        divText.setAttribute('class', 'colorbar_text');
        if (cbarMin < cbarMax) {
            divText.innerHTML = '> '+ cbarMax;
        } else {
            divText.innerHTML = '< '+ cbarMax;
        }
        div.appendChild(divText);
        cbar.appendChild(div);

        // All real colors from the intervals
        for (index in colors){
            div = document.createElement('div');
            div.setAttribute('class', 'colorbar_field');
            div.setAttribute('style', 'background-color: '+colors[index]);
            divText = document.createElement('div');
            divText.setAttribute('class', 'colorbar_text');
            // divText.innerHTML = Math.round(colorbarText[index], -1);
            divText.innerHTML = colorbarText[index];
            div.appendChild(divText);
            cbar.appendChild(div);
        }

        // The last colorbar segment
        div = document.createElement('div');
        div.setAttribute('class', 'colorbar_field');
        div.setAttribute('style', 'background-color: #FFFFFF');
        divText = document.createElement('div');
        divText.setAttribute('class', 'colorbar_text');
        divText.innerHTML = cbarMin;
        div.appendChild(divText);
        cbar.appendChild(div);

        // The last bit of text for every temperature below Tmin
        div = document.createElement('div');
        div.setAttribute('class', 'colorbar_field');
        div.setAttribute('style', 'height: 0px;');
        divText = document.createElement('div');
        divText.setAttribute('class', 'colorbar_text');
        if (cbarMin < cbarMax) {
            divText.innerHTML = '< '+ cbarMin;
        } else {
            divText.innerHTML = '> '+ cbarMin;
        }
        div.appendChild(divText);

        // create a new colorbar
        cbar.appendChild(div);

    };

    // create a colorbar menu
    function createColorbarMenu() {

        // place the colorbar settings in the dataset container
        var dataset_container = document.getElementById('dataset_container');

        var colorbar_padding = document.createElement('div');
        colorbar_padding.setAttribute('class', 'colorbar_padding');

        var colorbar_settings = document.createElement('details');
        colorbar_settings.setAttribute('class', 'dataset');

        var colorbar_heading = document.createElement('summary');
        colorbar_heading.setAttribute('class', 'colorbar_heading');
        colorbar_heading.innerHTML = 'Colorbar';

        var colorbar_sub_heading = document.createElement('div');
        colorbar_sub_heading.setAttribute('class', 'colorbar_sub_heading');
        colorbar_sub_heading.innerHTML = 'Set tracking';

        colorbar_heading.appendChild(colorbar_sub_heading);

        var colorbar_container = document.createElement('div');
        colorbar_container.setAttribute('class', 'colorbar_container');

        var colorbar_selection_form = document.createElement('form');
        colorbar_selection_form.setAttribute('class', 'colorbar_selection_form');
        colorbar_selection_form.setAttribute('action', '');


        // for every dataset spawn a menu entry
        for (var dataset_index in datasets) {

            var dataset_hash = datasets[dataset_index]['datasetHash'];
            var dataset_name = datasets[dataset_index]['datasetName'];
            var dataset_alias = datasets[dataset_index]['datasetAlias'];

            // lock to the values
            var colorbar_track_dataset_container = document.createElement('div');
            colorbar_track_dataset_container.setAttribute('class', 'colorbar_form_container');
            colorbar_track_dataset_container.setAttribute('id', 'colorbar_form_container_' + dataset_hash);

            var colorbar_track_dataset_entry_main = document.createElement('div');
            colorbar_track_dataset_entry_main.setAttribute('class', 'colorbar_form_main_entry');

            var colorbar_track_dataset_input_bullet_container = document.createElement('div');
            colorbar_track_dataset_input_bullet_container.setAttribute('class', 'colorbar_input_bullet_container');

            var colorbar_track_dataset_input_bullet = document.createElement('input');
            colorbar_track_dataset_input_bullet.setAttribute('class', 'colorbar_input_bullet');
            colorbar_track_dataset_input_bullet.setAttribute('type', 'radio');
            colorbar_track_dataset_input_bullet.setAttribute('name', 'colorbar_select');
            colorbar_track_dataset_input_bullet.setAttribute('id', 'colorbar_select_' + dataset_hash);
            colorbar_track_dataset_input_bullet.setAttribute('data-bullet', dataset_hash);
            colorbar_track_dataset_input_bullet.addEventListener("change", bulletSelector);
            colorbar_track_dataset_input_bullet_container.appendChild(colorbar_track_dataset_input_bullet);

            colorbar_track_dataset_entry_main.appendChild(colorbar_track_dataset_input_bullet_container);

            var colorbar_track_dataset_name = document.createElement('div');
            colorbar_track_dataset_name.setAttribute('class', 'colorbar_input_name');
            colorbar_track_dataset_name.innerHTML = 'Track dataset';
            colorbar_track_dataset_entry_main.appendChild(colorbar_track_dataset_name);

            colorbar_track_dataset_container.appendChild(colorbar_track_dataset_entry_main);

            var colorbar_track_dataset_entry_sub = document.createElement('div');
            colorbar_track_dataset_entry_sub.setAttribute('class', 'colorbar_form_sub_entry_track');

            var colorbar_track_dataset_sub_name = document.createElement('div');
            colorbar_track_dataset_sub_name.setAttribute('class', 'colorbar_form_sub_entry_track_name');
            colorbar_track_dataset_sub_name.setAttribute('title', dataset_name);
            colorbar_track_dataset_sub_name.innerHTML = dataset_name;
            colorbar_track_dataset_entry_sub.appendChild(colorbar_track_dataset_sub_name);

            var colorbar_track_dataset_sub_hash = document.createElement('div');
            colorbar_track_dataset_sub_hash.setAttribute('class', 'colorbar_form_sub_entry_track_hash');
            colorbar_track_dataset_sub_hash.innerHTML = '(' + dataset_hash.substr(0, 7) + ')';
            colorbar_track_dataset_entry_sub.appendChild(colorbar_track_dataset_sub_hash);

            colorbar_track_dataset_container.appendChild(colorbar_track_dataset_entry_sub);

            var colorbar_track_dataset_sep = document.createElement('div');
            colorbar_track_dataset_sep.setAttribute('class', 'colorbar_form_container_separator');
            colorbar_track_dataset_sep.setAttribute('id', 'colorbar_form_sep_' + dataset_hash);

            colorbar_selection_form.appendChild(colorbar_track_dataset_container);
            colorbar_selection_form.appendChild(colorbar_track_dataset_sep);

        }

        // lock to current
        var colorbar_lock_to_current_container = document.createElement('div');
        colorbar_lock_to_current_container.setAttribute('class', 'colorbar_form_container');

        var colorbar_lock_to_current_entry_main = document.createElement('div');
        colorbar_lock_to_current_entry_main.setAttribute('class', 'colorbar_form_main_entry');

        var colorbar_lock_to_current_input_bullet_container = document.createElement('div');
        colorbar_lock_to_current_input_bullet_container.setAttribute('class', 'colorbar_input_bullet_container');

        var colorbar_lock_to_current_input_bullet = document.createElement('input');
        colorbar_lock_to_current_input_bullet.setAttribute('class', 'colorbar_input_bullet');
        colorbar_lock_to_current_input_bullet.setAttribute('type', 'radio');
        colorbar_lock_to_current_input_bullet.setAttribute('name', 'colorbar_select');
        colorbar_lock_to_current_input_bullet.setAttribute('id', 'colorbar_select_current');
        colorbar_lock_to_current_input_bullet.setAttribute('data-bullet', 'current');
        colorbar_lock_to_current_input_bullet.addEventListener("change", bulletSelector);
        colorbar_lock_to_current_input_bullet_container.appendChild(colorbar_lock_to_current_input_bullet);

        colorbar_lock_to_current_entry_main.appendChild(colorbar_lock_to_current_input_bullet_container);

        var colorbar_lock_to_current_name = document.createElement('div');
        colorbar_lock_to_current_name.setAttribute('class', 'colorbar_input_name');
        colorbar_lock_to_current_name.innerHTML = 'Lock to current';
        colorbar_lock_to_current_entry_main.appendChild(colorbar_lock_to_current_name);

        colorbar_lock_to_current_container.appendChild(colorbar_lock_to_current_entry_main);

        // var colorbar_lock_to_current_entry_sub = document.createElement('div');
        // colorbar_lock_to_current_entry_sub.setAttribute('class', 'colorbar_form_sub_entry_form');

        // var colorbar_lock_to_current_sub_start_form = document.createElement('div');
        // colorbar_lock_to_current_sub_start_form.setAttribute('class', 'colorbar_form_sub_start');
        // colorbar_lock_to_current_entry_sub.appendChild(colorbar_lock_to_current_sub_start_form);

        // var colorbar_lock_to_current_sub_separator = document.createElement('div');
        // colorbar_lock_to_current_sub_separator.setAttribute('class', 'colorbar_form_sub_separator');
        // colorbar_lock_to_current_sub_separator.innerHTML = 'to';
        // colorbar_lock_to_current_entry_sub.appendChild(colorbar_lock_to_current_sub_separator);

        // var colorbar_lock_to_current_sub_end_form = document.createElement('div');
        // colorbar_lock_to_current_sub_end_form.setAttribute('class', 'colorbar_form_sub_end');
        // colorbar_lock_to_current_entry_sub.appendChild(colorbar_lock_to_current_sub_end_form);

        // colorbar_lock_to_current_container.appendChild(colorbar_lock_to_current_entry_sub);

        var colorbar_lock_to_current_sep = document.createElement('div');
        colorbar_lock_to_current_sep.setAttribute('class', 'colorbar_form_container_separator');


        // lock to the values
        var colorbar_lock_to_values_container = document.createElement('div');
        colorbar_lock_to_values_container.setAttribute('class', 'colorbar_form_container');

        var colorbar_lock_to_values_entry_main = document.createElement('div');
        colorbar_lock_to_values_entry_main.setAttribute('class', 'colorbar_form_main_entry');

        var colorbar_lock_to_values_input_bullet_container = document.createElement('div');
        colorbar_lock_to_values_input_bullet_container.setAttribute('class', 'colorbar_input_bullet_container');

        var colorbar_lock_to_values_input_bullet = document.createElement('input');
        colorbar_lock_to_values_input_bullet.setAttribute('class', 'colorbar_input_bullet');
        colorbar_lock_to_values_input_bullet.setAttribute('type', 'radio');
        colorbar_lock_to_values_input_bullet.setAttribute('name', 'colorbar_select');
        colorbar_lock_to_values_input_bullet.setAttribute('id', 'colorbar_select_values');
        colorbar_lock_to_values_input_bullet.setAttribute('data-bullet', 'values');
        colorbar_lock_to_values_input_bullet.addEventListener("change", bulletSelector);
        colorbar_lock_to_values_input_bullet_container.appendChild(colorbar_lock_to_values_input_bullet);

        colorbar_lock_to_values_entry_main.appendChild(colorbar_lock_to_values_input_bullet_container);

        var colorbar_lock_to_values_name = document.createElement('div');
        colorbar_lock_to_values_name.setAttribute('class', 'colorbar_input_name');
        colorbar_lock_to_values_name.innerHTML = 'Lock to values';
        colorbar_lock_to_values_entry_main.appendChild(colorbar_lock_to_values_name);

        colorbar_lock_to_values_container.appendChild(colorbar_lock_to_values_entry_main);

        var colorbar_lock_to_values_entry_sub = document.createElement('div');
        colorbar_lock_to_values_entry_sub.setAttribute('class', 'colorbar_form_sub_entry_form');

        var colorbar_lock_to_values_sub_start_form = document.createElement('input');
        colorbar_lock_to_values_sub_start_form.setAttribute('class', 'colorbar_form_sub_start');
        colorbar_lock_to_values_sub_start_form.setAttribute('id', 'colorbar_form_sub_start');
        colorbar_lock_to_values_sub_start_form.setAttribute('data-valuesMinmax', 'valuesMin');
        colorbar_lock_to_values_sub_start_form.addEventListener('focusout', valueSelector);
        colorbar_lock_to_values_sub_start_form.value = valuesMin;
        colorbar_lock_to_values_entry_sub.appendChild(colorbar_lock_to_values_sub_start_form);

        var colorbar_lock_to_values_sub_separator = document.createElement('div');
        colorbar_lock_to_values_sub_separator.setAttribute('class', 'colorbar_form_sub_separator');
        colorbar_lock_to_values_sub_separator.innerHTML = 'to';
        colorbar_lock_to_values_entry_sub.appendChild(colorbar_lock_to_values_sub_separator);

        var colorbar_lock_to_values_sub_end_form = document.createElement('input');
        colorbar_lock_to_values_sub_end_form.setAttribute('class', 'colorbar_form_sub_end');
        colorbar_lock_to_values_sub_end_form.setAttribute('id', 'colorbar_form_sub_end');
        colorbar_lock_to_values_sub_end_form.setAttribute('data-valuesMinMax', 'valuesMax');
        colorbar_lock_to_values_sub_end_form.addEventListener('focusout', valueSelector);
        colorbar_lock_to_values_sub_end_form.value = valuesMax;
        colorbar_lock_to_values_entry_sub.appendChild(colorbar_lock_to_values_sub_end_form);

        colorbar_lock_to_values_container.appendChild(colorbar_lock_to_values_entry_sub);

        var colorbar_lock_to_values_sep = document.createElement('div');
        colorbar_lock_to_values_sep.setAttribute('class', 'colorbar_form_container_separator');


        colorbar_selection_form.appendChild(colorbar_lock_to_current_container);
        colorbar_selection_form.appendChild(colorbar_lock_to_current_sep);
        colorbar_selection_form.appendChild(colorbar_lock_to_values_container);

        colorbar_container.appendChild(colorbar_selection_form);

        // attach heading and display to dataset
        colorbar_settings.appendChild(colorbar_heading);
        colorbar_settings.appendChild(colorbar_container);

        // put dataset into padding
        colorbar_padding.appendChild(colorbar_settings);

        // attach new menu to the menu list
        dataset_container.appendChild(colorbar_padding);

        // set the default bullet
        var bulletToSelect = document.getElementById(defaultBulletId);
        bulletToSelect.setAttribute('checked', 'checked');
    };
}
