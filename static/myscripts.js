//Base html javascript
//Set up login modal
// When the user clicks on the button, open the modal 
$('#login').on('click', function() {
  $('#login-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeLogin').on('click', function() {
    $('#login-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#login-form-popup')) {
        $('#login-form-popup').fadeOut(50);
    }
  });


//Set up register modal
// When the user clicks on the button, open the modal 
$('#createAccount').on('click', function() {
  $('#create-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeCreateAccount').on('click', function() {
    $('#create-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#create-form-popup')) {
        $('#create-form-popup').fadeOut(50);
    }
  });



//Homepage javascript
//Set up map on trips page
var map;
var visibleMarkers = [];
var tripAutocomplete;

function initMap() {
  geocoder = new google.maps.Geocoder();
  loc = new google.maps.LatLng("30","5");
  var mapOptions =
  {
    zoom: 2,
    center: loc
  };
  map = new google.maps.Map(document.getElementById('trip-map'), mapOptions);
  addTripMarkers('.myTrip');
}

function initAutocomplete() {
  // Create the autocomplete object, restricting the search to geographical
  // location types.
  tripAutocomplete = new google.maps.places.Autocomplete(
      /** @type {!HTMLInputElement} */(document.getElementById('trip-autocomplete')),
      {types: ['(regions)']});
}

function codeTripMarkerAddress(address, name, contentString) {
  geocoder.geocode( {address:address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      // place a marker at the location
      var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          animation: google.maps.Animation.DROP,
          title: name
      });
      visibleMarkers.push(marker);
      var infowindow = new google.maps.InfoWindow({
      content: contentString
      });
      marker.addListener('click', function() {
      infowindow.open(map, marker);
  });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
   }
  });
}

function addTripMarkers(className) {
  $( className ).each(function() {
  var location = $(this).children(".trip-location").html();
  var name = $(this).children(".trip-link").children(".trip-name").html();
  var link = $(this).children(".trip-link").children(".trip-name").attr("href");
  var contentString;
  if (typeof link != 'undefined') {
    contentString = '<div>'+
      '<h1><a href=\"'+link+'\">'+name+'</a></h1>'+
      '<div>'+
      '<p>'+location+'</p>'+
      '</div>'+
      '</div>';
  } else {
    contentString = '<div>'+
      '<h1>'+name+'</h1>'+
      '<div>'+
      '<p>'+location+'</p>'+
      '</div>'+
      '</div>';
  }
  codeTripMarkerAddress(location, name, contentString);
});
}

  //Add event handler to trip buttons
$("#viewShared").on('click', function() {
  $("#yourTrips").attr('hidden', true);
  $("#sharedTrips").attr('hidden', false);
  visibleMarkers.forEach(function(marker) {
    marker.setMap(null);
  });
  addTripMarkers('.theirTrip');
});

$("#viewTrips").on('click', function() {
  $("#yourTrips").attr('hidden', false);
  $("#sharedTrips").attr('hidden', true);
  visibleMarkers.forEach(function(marker) {
    marker.setMap(null);
  });
  addTripMarkers('.myTrip');
});

//Set up add new trip modal
// When the user clicks on the button, open the modal 
$('#add-trip').on('click', function() {
  $('#trip-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeNewTrip').on('click', function() {
    $('#trip-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#trip-form-popup')) {
        $('#trip-form-popup').fadeOut(50);
    }
  });

//Set up request friend modal
// When the user clicks on the button, open the modal 
$('#requestFriend').on('click', function() {
  $('#friend-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeAddFriend').on('click', function() {
    $('#friend-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#friend-form-popup')) {
        $('#friend-form-popup').fadeOut(50);
    }
  });

function flashMessage(message) {
  $('.flash').addClass('alert');
  $('.flash').html(message);
  setTimeout(function() {
    $('.flash').empty();
    $('.flash').removeClass('alert');
  }, 3000);
}

//Ajax request to share trip
function friendRequested(result) {
  var status = result;
  if (status.request_status == "no user") {
    $('#request_form').attr('hidden', true);
    $('#invite_friend_form').attr('hidden', false);
    $('#requestEmail').val($('#inviteFriendEmail').val());
  } else if (status.request_status == "already friends") {
    friendModal.style.display = "none";
    flashMessage("You are already friends with that user!");
  } else {
    friendModal.style.display = "none";
    flashMessage("Friend request sent!");
  }
}

//Ajax call
function requestFriend(evt) {
  evt.preventDefault();
  var formInputs = {
    "email": $('#friendEmail').val()
  };
  $.post("/request-friend.json", formInputs, friendRequested);
}

//Add event handler to share form
$('#request_form').on('submit', requestFriend);

//Ajax request to accept friend
function shareRequest() {
  $(".requestDetials[name=status]").attr('disabled', true);
}

//Ajax call
function requestDetails() {
  var formInputs = {
    "trip_id": this.getAttribute("name")
  };
  $.post("/share-request.json", formInputs, shareRequest);
}

// Add event handler to all friend request accept buttons
$('.requestDetails').on('click', requestDetails);


var tripLocation = $( '#trip-location' ).html();
var tripMap;

function initTripMap() {
  geocoder = new google.maps.Geocoder();
  var mapOptions =
  {
    zoom: 12
  };
  tripMap = new google.maps.Map(document.getElementById('entry-map'), mapOptions);
  codeTripCenterAddress(tripLocation);
  addEntryMarkers();
}



// View trip page javascript
var placeSearch, entryAutocomplete;

function initEntryAutocomplete() {
  // Create the autocomplete object, restricting the search to geographical
  // location types.
  entryAutocomplete = new google.maps.places.Autocomplete(
      /** @type {!HTMLInputElement} */(document.getElementById('entry-autocomplete')),
      {types: ['establishment']});
  entryAutocomplete.addListener('place_changed', fillInAddress);

}

function fillInAddress() {
  // Get the place details from the autocomplete object.
  var place = entryAutocomplete.getPlace();
  var address = place.formatted_address;
  $('#address').val(address);
}

function codeTripCenterAddress(address) {
  // Set the center of the map
  geocoder.geocode( {address:address}, function(results, status)
  {
    if (status == google.maps.GeocoderStatus.OK)
    {
      if (results[0].address_components.length == 1) {
        tripMap.setZoom(8);
      }
      tripMap.setCenter(results[0].geometry.location);//center the map over the result
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
   }
  });
}

//Marker icons by category
var icons = {
  Attraction: {
    icon: '/static/Attraction_marker.png'
  },
  Accommodation: {
    icon: '/static/Accommodation_marker.png'
  },
  Bar: {
    icon: '/static/Bar_marker.png'
  },
  Restaurant: {
    icon: '/static/Restaurant_marker.png'
  },
  Other: {
    icon: '/static/Other_marker.png'
  }
};

//Place markers on map for each entry
function codeEntryMarkerAddress(address, name, markerIcon, contentString) {
  // Change the marker address in to latlong and place parker at the latlong
  geocoder.geocode( {address:address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      // map.setCenter(results[0].geometry.location);//center the map over the result
      // place a marker at the location
      var marker = new google.maps.Marker({
          map: tripMap,
          position: results[0].geometry.location,
          icon: markerIcon,
          title: name
      });
      var infowindow = new google.maps.InfoWindow({
      content: contentString
      });

      marker.addListener('click', function() {
      infowindow.open(tripMap, marker);
  });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
   }
  });
}

//Set info for markers for each entry
function addEntryMarkers() {
  // Add markers for each entry to the map
  $( ".entry" ).each(function() {
  var address = $(this).children(".entry-address").html();
  var name = $(this).children(".entry-link").children(".entry-name").html();
  var category = $(this).children(".entry-category").html();
  var markerIcon = icons[category].icon;
  category = '/static/' + category + '.png';
  var photo = $(this).children(".entry-photo").html();
  var notes = $(this).children(".entry-notes").html();
  var link = $(this).children(".entry-link").children(".entry-name").attr("href");
  var contentString = '<div id="content">'+
      '<span id="popupBanner"><h1 id="popupHeader"><a href=\"' + link + '\">' + name + '</a></h1></span>'+
      '<img src=\"/'+photo+'\" width="300"</img>'+
      '<div id="bodyContent">'+
      '<img src=\"'+category+'\"></img>'+
      '<p>'+address+'</p>'+
      '<p>'+notes+'</p>'+
      // '<img src=\"/'+photo+'\" height="100"</img>'+
      '</div>'+
      '</div>';
  codeEntryMarkerAddress(address, name, markerIcon, contentString);
});
}

//Set up add new entry modal
// When the user clicks on the button, open the modal 
$('#createEntry').on('click', function() {
  $('#entry-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeNewEntry').on('click', function() {
    $('#entry-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#entry-form-popup')) {
        $('#entry-form-popup').fadeOut(50);
    }
  });

//Set up share trip modal
// When the user clicks on the button, open the modal 
$('#shareTrip').on('click', function() {
  $('#share-form-popup').show();
});

// When the user clicks on <span> (x), close the modal
$('#closeShareTrip').on('click', function() {
    $('#share-form-popup').hide();
});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function (e) {
    if ($(e.target).is('#share-form-popup')) {
        $('#share-form-popup').fadeOut(50);
    }
  });

function flashMessage(message) {
  $('.flash').addClass('alert');
  $('.flash').html(message);
  setTimeout(function() {
    $('.flash').empty();
    $('.flash').removeClass('alert');
  }, 3000);
}

//Ajax request to share trip
function shareResults(result) {
  var status = result;
  // console.log(status.share_status);
  if (status.share_status == "no user") {
    $('#share_form').attr('hidden', true);
    $('#invite_form').attr('hidden', false);
    $('#inviteEmail').val($('#shareEmail').val());
  } else if (status.share_status == "already shared") {
    shareModal.style.display = "none";
    flashMessage("You have already shared this trip with that user.");
    // alert("You have already shared this trip with that user");
  } else {
    shareModal.style.display = "none";
    flashMessage("Trip successfully shared!");
    // alert("Trip successfully shared!");
  }
}

//Ajax call
function shareTrip(evt) {
  evt.preventDefault();
  var formInputs = {
    "email": $('#shareEmail').val()
  };
  $.post("/share-trip/{{ trip.trip_id }}.json", formInputs, shareResults);
}

//Add event handler to share form
$('#share_form').on('submit', shareTrip);



//View entry Page Javascript

function btnClicked() {
    var notesHtml = $('#notes').html();
    var editableText = $("<textarea id=\"editNotes\"/>");
    editableText.val(notesHtml);
    $('#notes').replaceWith(editableText);
    editableText.focus();
    $('#updateNotes').hide();
    $('#submitUpdate').removeAttr('hidden');
    // console.log('got here');
}

function editableTextBlurred() {
    var html = $('#editNotes').val();
    var viewableText = $("<p id=\"notes\">");
    viewableText.html(html);
    $('#editNotes').replaceWith(viewableText);
    $('#updateNotes').show();
    $('#submitUpdate').attr('hidden', true);

}

$('#updateNotes').on("click", btnClicked);

$('#submitUpdate').on("click", function() {
    var formInputs = {
        "notes": $("#editNotes").val(),
        "entry": $('#entryId').html()
    };

    $.post("/update-notes",
           formInputs,
           editableTextBlurred);
});



// Friend page Javascript
//Ajax request to accept friend
function friendAccepted(result) {
  var status = result['request_id'];
  $("button[name=" + status + "]").remove();
  $("div[name=" + status + "]").html('Accepted!');
}

//Ajax call
function requestAccept() {
  var formInputs = {
    "response": this.getAttribute("name")
  };
  $.post("/accept-friend.json", formInputs, friendAccepted);
}

// Add event handler to all friend request accept buttons
$('.accepted-friend').on('click', requestAccept);


//Ajax request to accept friend
function friendDenied(result) {
  var status = result['request_id'];
  $("button[name=" + status + "]").remove();
  $("div[name=" + status + "]").html('Denied!');
}

//Ajax call
function requestDeny() {
  var formInputs = {
    "response": this.getAttribute("name")
  };
  $.post("/deny-friend.json", formInputs, friendDenied);
}

// Add event handler to all friend request accept buttons
$('.denied-friend').on('click', requestDeny);