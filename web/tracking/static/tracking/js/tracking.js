/**
 * Finds the nearest coordinate to a point
 * from an array of coordinates and returns
 * its index in the array.
 * 
 * @method getNearest
 * @param {Array} coordinates Two-dimensional array with coordinates
 * @param {Array} point One-dimensional array [x, y] holding the point
 * @return {Int} index
 */
function getNearest(coordinates, point) {
    var x = (coordinates[0][0] - point[0]);
    var y =  (coordinates[0][1] - point[1]);
    var d = {index: 0, distance: x*x + y*y};
    var nd = 0;
    for (i = 1; i < coordinates.length; i++) {
        x = (coordinates[i][0] - point[0]);
        y =  (coordinates[i][1] - point[1]);
        nd = x*x + y*y;
        if (nd < d.distance) {
            d = {index: i, distance: nd};
        }
    }
    return d.index;
}


/**
 * Formats the content of the popup displayed for a vehicle.
 * 
 * @param {Array} vehicle
 * @param {Array} track
 * @return {String} formatted popup content
 */
function formatPopupContent(vehicle, track) {
    var text = "<p><img src=" + vehicle[1] + " height='50px'></p><p>" + "<b>" + vehicle[0] +"</b>" + 
               "<br>Time: " + track[3] +
               "<br>Speed: " + Math.round(track[4] * 3.6) + " km/h" + 
               "<br>Altitude: " + track[2] + " m" +
               "<br>Climb: " + track[5] + " m/s" +
               "<br>Odometer: " + track[6] + " km";
    return text;
}
                

