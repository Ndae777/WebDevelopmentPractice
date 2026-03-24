document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  let not_reply = true // i will use this bool to determine if the submit is for a reply message

  document.querySelector("#compose-form").onsubmit = () => {
    if (not_reply) {
      send_mail();
    } else {
      // The expected else logic will be handled by the trigger of not_reply changing from true to false
    }
    return false;
  };

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

  //this function answers the second specification.
  mailbox_view(mailbox)
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


function mailbox_view(mailbox_name) {

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
          if (mail[mail_count]['read']) {
            div.style.backgroundColor = "lightgrey";
          }
          document.querySelector("#emails-view").append(div)

          let id = mail[mail_count]['id']

          //View email
          div.onclick = () => {
            view_email(id, mailbox_name);
            // Once clicked read turns to true.
            fetch(`/emails/${id}`, {
              method: 'PUT',
              body: JSON.stringify({
                read: true
              })
            })
          }

          mail_count++;
        }
      )

      return false;
    })
}

function view_email(mail_id, mailbox_name) {

  //show the email in this format
  fetch(`/emails/${mail_id}`)
    .then(response => response.json())
    .then(mail => {
      let div = document.createElement("div");
      div.innerHTML = `
    <b>From:</b> ${mail['sender']}</br>
    <b>To</b>: ${mail['recipients']}</br>
    <b>Subject</b>: ${mail['subject']}</br>
    <b>Timestamp</b>: ${mail['timestamp']}</br>
    <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
    <hr>
    ${mail['body']}`

      document.querySelector("#emails-view").innerHTML = "";
      document.querySelector("#emails-view").append(div);

      //show the archive option when viewing the appropriate mail
      archive(mailbox_name, mail_id);

      //reply logic
      document.querySelector("#reply").onclick = () => {
        compose_email();

        //sender pre-fill
        document.querySelector('#compose-recipients').value = mail['sender'];

        //subject pre-fill
        if (mail['subject'].slice(0, 4) == "Re: ") {
          document.querySelector("#compose-subject").value = mail['subject'];
        } else {
          document.querySelector("#compose-subject").value = `Re: ${mail['subject']}`;
        }

        //body pre-fill
        let previousMailbodies = [];
        let mail_starter = `On ${mail['timestamp']} ${mail['sender']} wrote:\n`;
        previousMailbodies.push(mail_starter);
        previousMailbodies.push(mail['body']);

        //what the user sees
        document.querySelector('#compose-body').value = `${mail_starter}${mail['body']}\n`;

        not_reply = false;

        // Re-define onsubmit for reply
        document.querySelector("#compose-form").onsubmit = () => {

          let full_text = document.querySelector("#compose-body").value;
          let body_to_save = full_text;

          // delete prev mail string 
          previousMailbodies.forEach((mailbod) => {
            body_to_save = body_to_save.replace(mailbod, '');
          });

          fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
              recipients: document.querySelector("#compose-recipients").value,
              subject: document.querySelector("#compose-subject").value,
              body: body_to_save, // saves only the new body without previous strings here
            })
          })
          .then(() => load_mailbox('sent'));

          return false;
        }
      }
    }
    )

}

function archive(mailbox_name, mail_id) {


  //the function should only run under if appropriate mailbox else it will return a console log 
  if (mailbox_name === "inbox" || mailbox_name === "archive") {

    const archive_button = document.createElement("button");

    //change the name of the archive button depending on context
    if (mailbox_name === "inbox") {
      archive_button.innerHTML = "Archive";
    } else { archive_button.innerHTML = "Unarchive"; }

    archive_button.className = "btn btn-sm btn-outline-primary"; //inherit class name for styling 
    document.querySelector("#emails-view").append(archive_button);

    archive_button.onclick = () => {

      if (mailbox_name === "inbox") {

        //archive the mail
        fetch(`/emails/${mail_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: true
          })
        })
          .then(() => {
            load_mailbox('inbox')
          })

      } else {

        //should Unarchive
        fetch(`/emails/${mail_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: false
          })
        })
          .then(() => {
            load_mailbox('inbox')
          })
      }


    }
  } else { console.log("This mailbox does not need archive option") }

}

