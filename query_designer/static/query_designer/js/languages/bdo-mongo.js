/**
 * Created by dimitris on 10/5/2017.
 */
BDOMongo = function(qdDocument) {
    this.qdDocument = qdDocument;

    this.getQuery = function() {
        var result = 'db.data.find({ variable_id: ObjectId("' + qdDocument.from[0].type.id + '")})';

        return result;
    };

    return this;
};