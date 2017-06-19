function main() {

    var add_object_button = document.getElementById('add_objects_button');
    add_object_button.addEventListener("click", open_objects_menu);
    var add_objects_menu_container = document.getElementById('add_objects_menu_container');
    var add_objects_menu = document.getElementById('add_objects_menu');

    // Init
    var object_list;
    var displayed_objects = [];

    function open_objects_menu() {

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/get_object_list', true);
        xhr.send();
        xhr.onload = function() {
            var temp_json = JSON.parse(xhr.responseText);

            object_list = temp_json['data_folders'];

            for (var it in object_list) {
                var add_objects_menu_item = document.createElement("div");
                add_objects_menu_item.innerHTML = object_list[it];
                add_objects_menu_item.setAttribute("id", object_list[it]);
                add_objects_menu_item.setAttribute("data-name", object_list[it]);
                add_objects_menu_item.setAttribute("class", "add_objects_menu_item");
                add_objects_menu_item.addEventListener('click', add_object);
                add_objects_menu.appendChild(add_objects_menu_item);
            };

            add_objects_menu_container.style.visibility = "visible";

            add_object_button.removeEventListener("click", open_objects_menu);

            // Bit cumbersome to add two of those suckers, but otherwise it strangely does not work.
            add_object_button.addEventListener("click", remove_eventListener_button);
            document.addEventListener("click", close_objects_menu_outside);
        };
    }

    function remove_eventListener_button(event) {
        // Check if we clicked on the button
        //

        if (event.target.matches('.add_objects_button')) {
            hide_and_delete_objects();
        }
    }

    function close_objects_menu_outside(event) {
        // Check if we clicked on anything else
        //

        if (!event.target.matches('.add_objects_button')) {
            hide_and_delete_objects();
        }
    }

    function hide_and_delete_objects() {
        add_object_button.removeEventListener("click", remove_eventListener_button);
        document.removeEventListener("click", close_objects_menu_outside);
        add_object_button.addEventListener("click", open_objects_menu);

        add_objects_menu_container.style.visibility = "hidden";

        for (var it in object_list) {
            var add_objects_menu_item = document.getElementById(object_list[it]);
            add_objects_menu.removeChild(add_objects_menu_item);
        };
    }

    function add_object(){
        // Add an object to the list of objects
        //

        var object_name = this.getAttribute('data-name');

        // Check if the object is already in the list
        if (!displayed_objects.includes(object_name)){
            displayed_objects.push(object_name);
            build_menu(object_name);
        }
    }

    function delete_object() {
        // Delete an object from the list of objects
        //

        var object_name = this.getAttribute('data-name');
        var object = document.getElementById('object_heading'+object_name);
        object.parentNode.removeChild(object);

        // Find index of array in displayed objects
        var index_in_disp_objects = displayed_objects.indexOf(object_name);
        // Remove one element at index
        displayed_objects.splice(index_in_disp_objects, 1);
    }

    function open_timestep_menu(){
        var object_name = this.getAttribute('data-name');
        var objects_timestep_menu = document.getElementById('object_timestep_menu_padding_container'+object_name);

        var object_timestep_menu_padding_container = document.getElementById('object_timestep_menu_padding_container'+object_name);

        // Load the timesteps via XHR. Do this every time to be able to
        // update the menu.
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/get_object_timesteps', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify({'object_name': object_name}));
        xhr.onload = function() {
            var temp_json = JSON.parse(xhr.responseText);
            var timesteps = temp_json['object_timesteps'];

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
        };

        objects_timestep_menu.style.visibility = 'visible';
        this.removeEventListener('click', open_timestep_menu);
        this.addEventListener('click', close_timestep_menu);
    }

    function select_timestep() {
        var object_name = this.getAttribute('data-name');
        var timestep = this.getAttribute('data-timestep');
        var object_current_timestep = document.getElementById('object_timestep_current'+object_name);
        object_current_timestep.innerHTML = timestep;

        // FIXME
        var field = 'temperatures';

        updateFragmentShaderData(object_name, field, timestep);
    }

    function decrease_timestep() {
        var object_name = this.getAttribute('data-name');
        var object_current_timestep = document.getElementById(
            'object_timestep_current'+object_name);

        var current_timestep = object_current_timestep.innerHTML;

        var previousTimestepPromise = postJSONPromise(
            'get_timestep_before',
            {'current_timestep': current_timestep, 'object_name': object_name}
        );
        // var previousTimestepPromise = postDataPromise(
        //     '/get_timestep_before?current_timestep='+
        //         current_timestep+'&object_name='+object_name);

        previousTimestepPromise.then(function(value) {
            var previous_timestep = value['previous_timestep'];
            if (current_timestep != previous_timestep) {

                // FIXME
                var field = 'temperatures';

                updateFragmentShaderData(object_name, field, previous_timestep);
                object_current_timestep.innerHTML = previous_timestep;
            }
        });
    }

    function increase_timestep() {
        var object_name = this.getAttribute('data-name');
        var object_current_timestep = document.getElementById(
            'object_timestep_current'+object_name);

        var current_timestep = object_current_timestep.innerHTML;

        var nextTimestepPromise = postJSONPromise(
            'get_timestep_after',
            {'current_timestep': current_timestep, 'object_name': object_name}
        );
        // var nextTimestepPromise = postDataPromise(
        //     '/get_timestep_after?current_timestep='+
        //         current_timestep+'&object_name='+object_name);

        nextTimestepPromise.then(function(value) {
            var next_timestep = value['next_timestep'];
            if (current_timestep != next_timestep) {

                // FIXME
                var field = 'temperatures';

                updateFragmentShaderData(object_name, field, next_timestep);
                object_current_timestep.innerHTML = next_timestep;
            }
        });
    }

    function close_timestep_menu() {
        var object_name = this.getAttribute('data-name');
        var objects_timestep_menu = document.getElementById('object_timestep_menu_padding_container'+object_name);
        objects_timestep_menu.style.visibility = 'hidden';
        this.removeEventListener('click', close_timestep_menu);
        this.addEventListener('click', open_timestep_menu);
    }

    function build_menu(object_name) {

        var objects_container = document.getElementById('objects_container');

        var object_padding = document.createElement('div');
        object_padding.setAttribute('class', 'object_heading');
        object_padding.setAttribute('id', 'object_heading'+object_name);

        var object = document.createElement('details');
        object.setAttribute('class', 'object');
        object.setAttribute('id', 'object'+object_name);

        var object_heading = document.createElement('summary');
        object_heading.setAttribute('class', 'object_heading');
        object_heading.setAttribute('id', 'object_heading'+object_name);
        object_heading.innerHTML = object_name;

        var object_functions = document.createElement('div');
        object_functions.setAttribute('class', 'object_functions');
        object_functions.setAttribute('id', 'object_functions'+object_name);

        var object_timestep_container = document.createElement('div');
        object_timestep_container.setAttribute('class', 'object_timestep_container');
        object_timestep_container.setAttribute('id', 'object_timestep_container'+object_name);

        var object_timestep_heading = document.createElement('div');
        object_timestep_heading.setAttribute('class', 'object_timestep_heading');
        object_timestep_heading.setAttribute('id', 'object_timestep_heading'+object_name);
        object_timestep_heading.innerHTML = 'Timestep';

        var object_timestep_controls = document.createElement('div');
        object_timestep_controls.setAttribute('class', 'object_timestep_controls');
        object_timestep_controls.setAttribute('id', 'object_timestep_controls'+object_name);

        var object_timestep_previous = document.createElement('div');
        object_timestep_previous.setAttribute('class', 'object_timestep_previous');
        object_timestep_previous.setAttribute('id', 'object_timestep_previous'+object_name);
        object_timestep_previous.setAttribute('data-name', object_name);
        object_timestep_previous.innerHTML = '<';
        object_timestep_previous.addEventListener('click', decrease_timestep);

        var object_timestep_current = document.createElement('div');
        object_timestep_current.setAttribute('class', 'object_timestep_current');
        object_timestep_current.setAttribute('id', 'object_timestep_current'+object_name);
        // object_timestep_current.innerHTML = '##.##';     // This is set later.
        object_timestep_current.addEventListener('click', open_timestep_menu);
        object_timestep_current.setAttribute('data-name', object_name);

        var object_timestep_next = document.createElement('div');
        object_timestep_next.setAttribute('class', 'object_timestep_next');
        object_timestep_next.setAttribute('id', 'object_timestep_next'+object_name);
        object_timestep_next.setAttribute('data-name', object_name);
        object_timestep_next.innerHTML = '>';
        object_timestep_next.addEventListener('click', increase_timestep);

        var object_timestep_menu_padding_container = document.createElement('div');
        object_timestep_menu_padding_container.setAttribute('class', 'object_timestep_menu_padding_container');
        object_timestep_menu_padding_container.setAttribute('id', 'object_timestep_menu_padding_container'+object_name);

        var object_timestep_menu = document.createElement('div');
        object_timestep_menu.setAttribute('class', 'object_timestep_menu');
        object_timestep_menu.setAttribute('id', 'object_timestep_menu'+object_name);

        var object_property_container = document.createElement('div');
        object_property_container.setAttribute('class', 'object_property_container');
        object_property_container.setAttribute('id', 'object_property_container'+object_name);

        var xhr = new XMLHttpRequest();
        // xhr.open('POST', '/get_object_properties?object_name='+object_name, true);
        // xhr.send();
        xhr.open('POST', '/get_object_properties', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify({'object_name': object_name}));

        var object_properties;
        var initial_timestep;

        xhr.onload = function() {
            var temp_json = JSON.parse(xhr.responseText);
            object_properties = temp_json['object_properties'];
            initial_timestep = temp_json['initial_timestep'];

            object_timestep_current.innerHTML = initial_timestep;

            for (var propertyId in object_properties) {
                var property = object_properties[propertyId];
                var object_property = document.createElement('div');
                object_property.setAttribute('class', 'object_property');
                object_property.setAttribute('id', 'object_property'+object_name+property);
                object_property.innerHTML = property;
                object_property_container.appendChild(object_property);
            }

            var nodepath = object_name + '/fo/' + initial_timestep + '/mesh/case.nodes.bin';
            var elementpath = object_name + '/fo/' + initial_timestep + '/mesh/case.dc3d8.bin';

            // FIXME
            var field = 'temperatures';

            updateVertexShaderData(
                object_name=object_name,
                field=field,
                nodepath=nodepath,
                elementpath=elementpath,
                timestep=initial_timestep);
        };

        var object_controls_container = document.createElement('div');
        object_controls_container.setAttribute('class', 'object_controls_container');
        object_controls_container.setAttribute('id', 'object_controls_container'+object_name);

        var object_controls_delete_object = document.createElement('div');
        object_controls_delete_object.setAttribute('class', 'object_controls_delete_object');
        object_controls_delete_object.setAttribute('id', 'object_controls_delete_object'+object_name);
        object_controls_delete_object.innerHTML = 'Delete Object';
        object_controls_delete_object.setAttribute('data-name', object_name);
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
