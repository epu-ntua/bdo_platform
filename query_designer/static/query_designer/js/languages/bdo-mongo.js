/**
 * Created by dimitris on 10/5/2017.
 */
BDOMongo = function(qdDocument) {
    this.qdDocument = qdDocument;

    this.getQuery = function() {
        var result = JSON.stringify(qdDocument, null, '\t');

        return result;
    };

    return this;
};