document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  //Send Mail Task
  document.querySelector('#compose-form').addEventListener("submit", send_mail);

  
});


function send_mail(event) {

  event.preventDefault();

  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    load_mailbox('sent');
  })
  .catch(error => {
     console.log('Error:', error);
   }); 
}


function compose_email(reply=false, recipients_str='', subject_str='', body_str='') {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#display-email').style.display = 'none';

  document.querySelector('#compose-recipients').value = recipients_str;
  document.querySelector('#compose-subject').value = subject_str;
  document.querySelector('#compose-body').value = body_str;
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#display-email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show the mailbox emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    const emails_view = document.querySelector('#emails-view');
    emails.forEach(email => {
      let new_email = display_email(email, mailbox);
      if(new_email !== -1){
        emails_view.appendChild(new_email);
      }
    })
  });
}

function display_email(email, mailbox) {
  if ( (mailbox === 'sent' || mailbox === 'inbox') && email['archived']){
    return -1
  }
  else if(mailbox === 'archive' && !email['archived']){
    return -1
  }

  const email_container = document.createElement('div');
  email_container.className = "email container";
  const user_display = document.createElement('span');
  if (mailbox === 'sent' || mailbox === 'archive'){
    user_display.innerHTML = email['recipients'];
  }else if (mailbox === 'inbox'){
    user_display.innerHTML = email['sender'];
  }else{
    error = document.createElement('span');
    return error.innerHTML = 'Problem with the mailboxes'
  }

  const subject_display = document.createElement('span');
  subject_display.innerHTML = email['subject'];

  const timestamp_display = document.createElement('span');
  timestamp_display.innerHTML = email['timestamp'];

  email_container.appendChild(user_display);
  email_container.appendChild(subject_display);
  email_container.appendChild(timestamp_display);

  style_email(email['read'], email_container);

  //View Email Task
  email_container.addEventListener("click", () => view_email(email['id'], mailbox));

  return email_container;
}

function style_email(read, email_container){
  email_container.style.border = "1px solid #007bff";
  email_container.style.borderRadius = "5px";
  email_container.style.marginBottom = "10px";
  email_container.style.padding = "3px";
  email_container.style.display = "flex";
  email_container.style.justifyContent = "space-between";
  email_container.addEventListener('mouseover', () => email_container.style.cursor = "pointer");

  if (!read){
    email_container.style.background = "white";
  }else{
    email_container.style.background = "gray";
  }
  

  return email_container
}

function view_email(id, mailbox){
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#display-email').style.display = 'block';

  // Gets the email from the API
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
     view_whole_email(email, mailbox);
  });

  // Marks email as read
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });
  
}

function view_whole_email(email, mailbox){
  const email_container = document.querySelector('#display-email');
  email_container.innerHTML = '';
  const date = document.createElement('div');
  date.innerHTML = email['timestamp'];

  const sender = document.createElement('div');
  sender.innerHTML =  `<strong>From:</strong> ${email['sender']}`;

  const recipient = document.createElement('div');
  recipient.innerHTML = `<strong>To:</strong> ${email['recipients'].join(', ')}`;

  const subject = document.createElement('div');
  subject.innerHTML = email['subject'];
  subject.style.border = "1px solid #007bff";
  subject.style.padding = "2px 5px";
  subject.style.marginTop = "15px";
  subject.style.borderRadius = "5px";

  const body = document.createElement('div');
  body.innerHTML = email['body'];
  body.style.border = "1px solid #007bff";
  body.style.borderRadius = "5px";
  body.style.padding = "2px 5px";
  body.style.marginTop = "5px";
  body.style.minHeight = "20vh";

  email_container.appendChild(date);
  email_container.appendChild(sender);
  email_container.appendChild(recipient);

  // Reply button
  const reply = document.createElement('button');
  reply.innerHTML = "Reply";
  reply.className = "btn btn-primary";
  reply.style.margin = "10px 10px 0 0";
  email_container.appendChild(reply);
  reply.addEventListener('click', () => {
    let subject_str = email['subject'];
    if (!subject_str.startsWith('Re: ')){
      subject_str = `Re: ${subject_str}`;
    }
    const body_str = `On ${email['timestamp']} ${email['sender']} wrote: \n ${email['body']}`;
    compose_email(true, email['sender'], subject_str, body_str);
  } );

  // Archive button when opening an inbox or archived email
  if (mailbox === "inbox" || mailbox === "archive"){
    const archive = document.createElement('button');
    if (email['archived']){
      archive.innerHTML = "Unarchive";
    }else{
      archive.innerHTML = "Archive";
    }
    archive.className = "btn btn-primary";
    archive.style.marginTop = "10px";
    archive.addEventListener('click', () => {
      update_archive(email);
    });
    email_container.appendChild(archive);
  } 

  email_container.appendChild(subject);
  email_container.appendChild(body); 
}

function update_archive(email){
  // Marks email as archived or unarchived
  fetch(`/emails/${email['id']}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !email['archived']
    })
  })
  .then(() => load_mailbox("inbox"));
}