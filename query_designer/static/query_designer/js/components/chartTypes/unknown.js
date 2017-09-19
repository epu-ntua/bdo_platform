/**
 * Created by dimitris on 19/9/2017.
 */
UnknownChart = function(refChart, nonVisualizedDimensions) {
    this.onHeadersLoaded = function() {};
    this.onChartCreated = function() {};
    this.onFiltersUpdateStarted = function() {};
    this.onFiltersUpdated = function() {};
    this.getVisualizationFilters = function() {return []};

    return this
};
