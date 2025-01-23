function toggleErweiterteInformationen(event) {
  var kachel = event.target.parentNode;
  var erweiterteInformationen = kachel.querySelector('.erweiterte-informationen');

  if (erweiterteInformationen.classList.contains('angezeigt')) {
    erweiterteInformationen.classList.remove('angezeigt');
  } else {
    erweiterteInformationen.classList.add('angezeigt');
  }
}

function deleteNote(noteId) {
  fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId })
  }).then((_res) => {
      window.location.href ="/notes";
  });
}

function addToFavorites(city) {
  fetch('/add-to-favorites', {
    method: 'POST',
    body: JSON.stringify({'city': city}),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    if (response.ok) {
      alert('Stadt wurde zu Favoriten hinzugefügt!');
    } else {
      throw new Error('Stadt ist bereits in den Favoriten!');
    }
  })
  .catch(error => {
    alert(error.message);
  });
}

function deleteFavorite(fav_city) {
  fetch("/delete-favorite", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ "fav_city": fav_city })
  }).then((_res) => {
      window.location.href ="/favorite";
  });
}