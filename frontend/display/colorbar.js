function addColorbar(Tmin, Tmax) {
    // Adds a colorbar to our document.
    Tmin = 0 || Tmin;
    Tmax = 0 || Tmax;

    var cbar = document.getElementById('colorbar');

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
    var colorbarText = [];
    for (var index in intervals) {
        colorbarText.push(intervals[index]*(Tmax - Tmin) + Tmin);
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
    div.setAttribute('style', 'background-color: #000000');
    var divText = document.createElement('div');
    divText.setAttribute('class', 'colorbar_text');
    divText.innerHTML = '> '+ Tmax;
    div.appendChild(divText);
    cbar.appendChild(div);

    // All real colors from the intervals
    for (var index in colors){
        div = document.createElement('div');
        div.setAttribute('class', 'colorbar_field');
        div.setAttribute('style', 'background-color: '+colors[index]);
        divText = document.createElement('div');
        divText.setAttribute('class', 'colorbar_text');
        divText.innerHTML = Math.round(colorbarText[index], -1);
        div.appendChild(divText);
        cbar.appendChild(div);
    }

    // The last colorbar segment
    div = document.createElement('div');
    div.setAttribute('class', 'colorbar_field');
    div.setAttribute('style', 'background-color: #000000');
    divText = document.createElement('div');
    divText.setAttribute('class', 'colorbar_text');
    divText.innerHTML = Tmin;
    div.appendChild(divText);
    cbar.appendChild(div);

    // The last bit of text for every temperature below Tmin
    div = document.createElement('div');
    div.setAttribute('class', 'colorbar_field');
    div.setAttribute('style', 'height: 0px;');
    divText = document.createElement('div');
    divText.setAttribute('class', 'colorbar_text');
    divText.innerHTML = '< ' + Tmin;
    div.appendChild(divText);
    cbar.appendChild(div);
}
