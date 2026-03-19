document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => { load_mailbox('Inbox'); mailbox('inbox') });
  document.querySelector('#sent').addEventListener('click', () => { load_mailbox('sent'); mailbox('sent') });
  document.querySelector('#archived').addEventListener('click', () => { load_mailbox('archive'); mailbox('archive') });
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector("#compose-form").onsubmit = send_mail;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

}

function send_mail() {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector("#compose-recipients").value,
      subject: document.querySelector("#compose-subject").value,
      body: document.querySelector("#compose-body").value,
    })
  }).then(response => response.json())
    .then(email_composed => {
      console.log(email_composed);
      load_mailbox('sent');
    })
  return false;
}


function mailbox(mailbox_name) {


  fetch(`/emails/${mailbox_name}`)
    .then(response => response.json())
    .then(mail => {

      //console.log("Latest email in this mailbox: \n", mail[0]) //checking the data

      let mail_count = 0;

      mail.forEach(
        () => {
          
          //creating and styling div
          let div = document.createElement('div');
          div.innerHTML = `<div><b>${mail[mail_count]['sender']}</b> ${mail[mail_count]['subject']}</div> <div style='color:grey;'>${mail[mail_count]['timestamp']}</div>`
          div.style.border = "1px solid black";
          div.style.padding = "10px";
          div.style.display = "flex";
          div.style.justifyContent = "space-between";
          document.querySelector("#emails-view").append(div)

          mail_count++;
        }
      )


    })
}