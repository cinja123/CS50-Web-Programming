let bool_follower = false;
const profile_id = parseInt(window.location.pathname.split('/')[2], 10);

document.addEventListener('DOMContentLoaded', () => {
    const button = document.querySelector('#followButton');
    update_button(button);
    button.onclick = (event) => follow(event.target);
});


// Updates the text inside the button to Follow or Unfollow
function update_button(button){
    fetch(`/follows/${profile_id}`)
    .then(response => response.json())
    .then(data => {
        bool_follower = data.followsProfile;
        if(bool_follower){
            button.innerHTML = "Unfollow";
        }
        else{
            button.innerHTML = "Follow";
        }
    });
}

// Updates if user follows the profile or not
function follow(button){
    fetch(`/follows/${profile_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            follow: !bool_follower
        })
    })
    .then(response => response.json())
    .then(data => {
        update_button(button);
        document.querySelector('#followers').firstElementChild.innerHTML = data.follower_count;
    });
}