var duplicates = [];

db.perfume_features.aggregate([
  { $match: {
    name: { "$ne": '' }  // discard selection criteria
  }},
  { $group: {
    _id: { name: "$perfume_id"}, // can be grouped on multiple properties
    dups: { "$addToSet": "$_id" },
    count: { "$sum": 1 }
  }},
  { $match: {
    count: { "$gt": 1 }    // Duplicates considered as count greater than one
  }}
],
{allowDiskUse: true}       // For faster processing if set is larger
)               // You can display result until this and check duplicates
.forEach(function(doc) {
    doc.dups.shift();      // First element skipped for deleting
    doc.dups.forEach( function(dupId){
        duplicates.push(dupId);   // Getting all duplicate ids
        }
    )
})

// If you want to Check all "_id" which you are deleting else print statement not needed
printjson(duplicates);

// Remove all duplicates in one go
db.perfume_features.remove({_id:{$in:duplicates}})


//For short_ratings table
var duplicates = [];

db.short_ratings.aggregate([
  { $match: {
  name: { "$ne": '' }, // discard selection criteria
  rated_user_id: { "$ne": '' }
  }},
  { $group: {
    _id: { name: "$perfume_id", rated_user_id: "$rated_user_id"}, // can be grouped on multiple properties
    dups: { "$addToSet": "$_id" },
    count: { "$sum": 1 }
  }},
  { $match: {
    count: { "$gt": 1 }    // Duplicates considered as count greater than one
  }}
],
{allowDiskUse: true}       // For faster processing if set is larger
).forEach(function(doc) {
    doc.dups.shift();      // First element skipped for deleting
    doc.dups.forEach( function(dupId){
        duplicates.push(dupId);   // Getting all duplicate ids
        }
    )
})

// If you want to Check all "_id" which you are deleting else print statement not needed
printjson(duplicates);

// Remove all duplicates in one go
db.short_ratings.remove({_id:{$in:duplicates}})
