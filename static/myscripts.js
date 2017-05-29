// Get the modal to login
var modal = document.getElementById('login-form-popup');

// Get the button that opens the modal
var btn = document.getElementById("login");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal 
$(btn).on('click', function() {
  Modal.style.display = "block";
});

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

// Get the modal to register
var createModal = document.getElementById('create-form-popup');

// Get the button that opens the modal
var createBtn = document.getElementById("createAccount");

// When the user clicks on the button, open the modal 
$(createBtn).on('click', function() {
  createModal.style.display = "block";
});

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[1];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    createModal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == createModal) {
        createModal.style.display = "none";
    }
};

// debugger;
//Set up map on trips page
  var map;
  var visibleMarkers = [];

  function initMap() {
    geocoder = new google.maps.Geocoder();
    loc = new google.maps.LatLng("30","5");
    var mapOptions =
    {
      zoom: 2,
      center: loc
    };
    map = new google.maps.Map(document.getElementById('trip-map'), mapOptions);
    addMarkers('.myTrip');
  }

  function initAutocomplete() {
    // Create the autocomplete object, restricting the search to geographical
    // location types.
    autocomplete = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(document.getElementById('autocomplete')),
        {types: ['(regions)']});
  }

  function codeMarkerAddress(address, name, contentString) {
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


  function addMarkers(className) {
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
    codeMarkerAddress(location, name, contentString);
  });
  }

  //Add event handler to trip buttons
$("#viewShared").on('click', function() {
  $("#yourTrips").attr('hidden', true);
  $("#sharedTrips").attr('hidden', false);
  visibleMarkers.forEach(function(marker) {
    marker.setMap(null);
  });
  addMarkers('.theirTrip');
});

$("#viewTrips").on('click', function() {
  $("#yourTrips").attr('hidden', false);
  $("#sharedTrips").attr('hidden', true);
  visibleMarkers.forEach(function(marker) {
    marker.setMap(null);
  });
  addMarkers('.myTrip');
});

  // Get the modal to add new trip
var tripModal = document.getElementById('trip-form-popup');

// Get the button that opens the modal
var tripBtn = document.getElementById("addTrip");

// Get the <span> element that closes the modal
var tripSpan = document.getElementsByClassName("close")[2];

// When the user clicks on the button, open the modal 
tripBtn.onclick = function() {
    tripModal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
tripSpan.onclick = function() {
    tripModal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == tripModal) {
        tripModal.style.display = "none";
  }
};

// Get the modal to request friend
var friendModal = document.getElementById('friend-form-popup');

// Get the button that opens the modal
var friendBtn = document.getElementById("requestFriend");

// Get the <span> element that closes the modal
var friendSpan = document.getElementsByClassName("close")[3];

// When the user clicks on the button, open the modal 
friendBtn.onclick = function() {
    friendModal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
friendSpan.onclick = function() {
    friendModal.style.display = "none";
    $('#request_form').attr('hidden', false);
    $('#invite_friend_form').attr('hidden', true);
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == friendModal) {
        friendModal.style.display = "none";
        $('#request_form').attr('hidden', false);
        $('#invite_friend_form').attr('hidden', true);
  }
};

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

function initialize() {
  initMap();
  initAutocomplete();
}