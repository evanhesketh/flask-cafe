"use strict";

const CAFE_ID = $("#c-id").attr("data-cafe-id");

async function getLikeStatus() {

  const resp = await axios.get('/api/likes', {params: {"cafe_id": CAFE_ID}});
  const likeStatus = resp.data.likes;
 
  return likeStatus;
}

async function updateLikeBtnText() {
  const likeStatus = await getLikeStatus();

  if (likeStatus) {
    $('#like-btn').text("Unlike");
  } else {
    $('#like-btn').text("Like");
  }
}

function handleLikeClick(evt)  {
  evt.preventDefault();

  const likeBtnText = $('#like-btn').text()

  if (likeBtnText === 'Unlike') {
    unlike();
  } else if (likeBtnText === 'Like') {
    like();
  }
}

async function unlike() {
  await axios.post('/api/unlike', {"cafe_id": CAFE_ID});
  $('#like-btn').text('Like');
}

async function like() {
  await axios.post('/api/like', {"cafe_id": CAFE_ID});
  $('#like-btn').text('Unlike');
}

$(window).on('load', updateLikeBtnText);
$('#like-btn').on('click', handleLikeClick);
