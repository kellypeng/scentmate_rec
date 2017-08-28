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
db.perfume_features.remove({_id:{$in:duplicates}});


################################# perfume_new


var duplicates = [];

db.perfume_new.aggregate([
  { $match: {
    name: { "$ne": '' }  // discard selection criteria
  }},
  { $group: {
    _id: { name: "$item_name"}, // can be grouped on multiple properties
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
db.perfume_new.remove({_id:{$in:duplicates}});

################################# ratings_trial2

var duplicates = [];

db.ratings_trial2.aggregate([
  { $match: {
    name: { "$ne": '' }  // discard selection criteria
  }},
  { $group: {
    _id: { 'user_rating': "$user_rating", 'rated_user_id': "$rated_user_id",
    'perfume_id': "$perfume_id"}, // can be grouped on multiple properties
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
db.ratings_trial2.remove({_id:{$in:duplicates}});
