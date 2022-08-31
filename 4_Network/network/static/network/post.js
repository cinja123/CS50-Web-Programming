document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fas.fa-heart').forEach(heart => {
        heart.onclick = () => like(heart);
    });

    document.querySelectorAll('.editButton').forEach(edit => {
        edit.onclick = () => editPostForm(edit);
    });
});

function editPostForm(edit){
    const post_id = edit.dataset.postId;
    const post_body = edit.parentElement.previousElementSibling;
    const text_height = post_body.clientHeight;
    post_body.innerHTML = "";

    const textarea = document.createElement('textarea');
    textarea.setAttribute('class', 'edit area');
    textarea.style.height = `${text_height}px`;
    
    const save = document.createElement('button');
    save.setAttribute('class', 'saveButton');
    save.innerHTML = "Save";

    post_body.appendChild(textarea);
    edit.parentElement.appendChild(save);
    edit.style.display = "none";

    console.log(post_body);
    fetch(`/edit/${post_id}`)
    .then(response => response.json())
    .then(data => {
        textarea.value = data.content;
        save.onclick = () => editPost(textarea, post_id, edit, save);
    });
}


function editPost(textarea, post_id, edit, save){
    const new_content = textarea.value;
    fetch(`/edit/${post_id}`, {
        method: "PUT",
        body: JSON.stringify({
            new_content: new_content
        })
    })
    .then(() => {
        if(new_content.length === 0){
            textarea.parentElement.parentElement.remove();
        }
        else{
            textarea.parentElement.innerHTML = new_content;
            edit.style.display = "block";
            save.remove();
        }
       
    })
    // mit fetch(/edit/post_id) textarea neuen content in database speichern
}


function like(heart){
    const is_liked = heart.parentElement.className.includes("yes");
    const post_id = heart.dataset.postId;
    const like_count = parseInt(heart.nextSibling.innerHTML, 10);
    if (is_liked){
        like_update = "no";
    }else{
        like_update = "yes";
    }

    // Marks post as like or unlike
    fetch(`/likes/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            liked: like_update
        })
    })
    .then(response => response.json())
    .then(likes => {
        heart.nextSibling.innerHTML = likes.newLikes;
        if(is_liked){
            heart.parentElement.className = "post likes no";
        }else{
            heart.parentElement.className = "post likes yes";
        }
    });
}