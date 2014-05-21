function addGeoHashedRecords(query) {

    L.GeohashRect = L.Rectangle.extend({
        initialize: function (geohash, options) {
            L.Rectangle.prototype.initialize.call(this, this._geohashToBounds(geohash), options);
        },

        _geohashToBounds: function(geohash) {
            var gh = this._decodeGeoHash(geohash);

            var southWest = L.latLng(gh['latitude'][0], gh['longitude'][0]),
                northEast = L.latLng(gh['latitude'][1], gh['longitude'][1]),
                bounds = L.latLngBounds(southWest, northEast);

            return this._boundsToLatLngs(bounds)
        },

        _decodeGeoHash: function(geohash) {
            var is_even = 1;
            var lat = []; var lon = [];
            lat[0] = -90.0;  lat[1] = 90.0;
            lon[0] = -180.0; lon[1] = 180.0;
            lat_err = 90.0;  lon_err = 180.0;

            for (i=0; i<geohash.length; i++) {
                c = geohash[i];
                cd = this.BASE32.indexOf(c);
                for (j=0; j<5; j++) {
                    mask = this.BITS[j];
                    if (is_even) {
                        lon_err /= 2;
                        this._refine_interval(lon, cd, mask);
                    } else {
                        lat_err /= 2;
                        this._refine_interval(lat, cd, mask);
                    }
                    is_even = !is_even;
                }
            }
            lat[2] = (lat[0] + lat[1])/2;
            lon[2] = (lon[0] + lon[1])/2;

            return { latitude: lat, longitude: lon};
        },
        BITS: [16, 8, 4, 2, 1],
        BASE32: "0123456789bcdefghjkmnpqrstuvwxyz",
        _refine_interval: function(interval, cd, mask) {
            if (cd&mask) {
                interval[0] = (interval[0] + interval[1])/2;
            } else {
                interval[1] = (interval[0] + interval[1])/2;
            }
        }

    });
    L.geohashRect = function (geohash, options) {
        return new L.GeohashRect(geohash, options);
    }

    function getColour(d) {
        // colours from http://colorbrewer2.org/
        return d > 10000 ? '#238b45':
               d > 1000  ? '#66c2a4':
               d > 100   ? '#b2e2e2':
                           '#edf8fb';
    }

    var geoHashesLayer = new L.featureGroup();

    function zoomToFeature(e) {
        map.fitBounds(e.target.getBounds());
    }

    var info = L.control();
    info.onAdd = function(map) {
       this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
       this.update();
       return this._div; 
    }

    // method that we will use to update the control based on feature properties passed
    info.update = function (numRecords) {
        this._div.innerHTML = '<h4>Number of records</h4>' +  (numRecords ?
            '<b>' + numRecords + '</b>'
            : 'Hover over a region');
    };

    info.addTo(map);

    function highlightFeature(e) {
        var layer = e.target;
        info.update(layer.options.numRecords);
    }

    function resetHighlight(e) {
        info.update();
    }

    jQuery.ajax({
        url: "{{ url_for('geogrid_json') }}" + (query ? query : ""),
        dataType: "json"
    }).done(function(locations) {
        var buckets = locations.aggregations.geogrid.buckets;
        for (var i = 0; i < buckets.length; i++) {
            var bucket = buckets[i];
            var ghMarker = L.geohashRect(bucket.key, {
                fillColor: getColour(bucket.doc_count),
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7,
                numRecords: bucket.doc_count
            });
            ghMarker.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            });
            geoHashesLayer.addLayer(ghMarker);

        }
        map.addLayer(geoHashesLayer);
        // map.fitBounds(geoHashesLayer.getBounds());

    });
}