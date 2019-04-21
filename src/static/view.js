document.addEventListener('DOMContentLoaded', function() {
  var app = new Vue({
    el: '#app',
    filters: {
      prettyDate(dateString) {
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const date = new Date(dateString);
        return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} @ ${date.getHours()}:${date.getMinutes()}`
      }
    },
    data: {
      isLoading: true,
      fromPage: '',
      mail: null,
      decryptKey: '',
      signKeyText: '',
      signKeyFile: null

    },
    computed: {
      fromOrTo() {
        return this.fromPage === 'inbox' ? 'From:' : 'To:';
      },
      fromOrToValue() {
        if (!this.mail) return 'Loading...';
        return this.fromPage === 'inbox' ? this.mail.headers.From || this.mail.headers.from : this.mail.headers.To || this.mail.headers.to;
      },
      date() {
        return this.mail ? this.mail.headers.Date : 'Loading...';
      },
      subject() {
        return this.mail ? this.mail.headers.Subject || this.mail.headers.subject : 'Loading...';
      },
      text() {
        return this.mail ? this.mail.content.text : 'Loading...';
      },
      isSigned() {
        return this.mail ? this.mail.is_signed : false;
      },
      inboxClass() {
        return this.fromPage === 'inbox' ? 'active' : '';
      },
      outboxClass() {
        return this.fromPage === 'outbox' ? 'active' : '';
      }
    },
    mounted() {
      const urlParams = new URLSearchParams(window.location.search);
      this.fromPage = urlParams.get('from');
      const mail_id = urlParams.get('id');
      axios.get(`/mails/${mail_id}`)
      .then((response) => {
        if (response.data.status === 'OK') {
          this.mail = response.data.data;
        }
      })
      .catch((error) => {
        // handle error
        console.log(error);
      })
      .then(() => {
        this.isLoading = false;
      });
    },
    methods: {
      changeSignKey(event) {
        this.signKeyFile = event.target.files[0];
      },
      decrypt() {
        if (this.decryptKey === '') {
          M.toast({html: 'Decryption key cannot be empty!'});
          return;
        }
        const formData = new FormData()
        formData.set('key', this.decryptKey);
        formData.append('mail_id', this.mail.content.mail_id);
        axios({
          method: 'post',
          url: '/mails/decrypt',
          data: formData
        })
          .then((response) => {
            if (response.data.status === 'OK') {
              M.toast({html: 'Decryption success!'});
              this.mail.content.text = response.data.data;
            } else if (response.data.status === 'ERROR') {
              M.toast({html: response.data.msg});
            }
          })
          .catch(() => {
            M.toast({html: 'Decryption failed!'});
          })
        this.decryptKey = '';
      },
      verify() {
        if (this.signKeyText === '' && !this.signKeyFile) {
          M.toast({html: 'Public key cannot be empty!'});
          return;
        } else if (!this.signKeyFile && this.signKeyText !== '') {
          signKeyAsArray = this.signKeyText.split(',');
          if (signKeyAsArray.length !== 2
            || parseInt(signKeyAsArray[0]) <= 0
            || parseInt(signKeyAsArray[1]) >= 13) {
              M.toast({html: 'Public key\'s format is wrong!'});
              return;
          }
        }
        const formData = new FormData()
        if (this.signKeyFile) {
          formData.set('mode', 'file');
          formData.append('key', this.signKeyFile);
        } else {
          formData.set('mode', 'text');
          formData.append('key', this.signKeyText);
        }
        formData.append('content', this.mail.content.text);
        axios({
          method: 'post',
          url: '/mails/verify',
          data: formData,
          config: { headers: { 'Content-Type': 'multipart/form-data' } }
        })
          .then((response) => {
            if (response.data.status === 'OK') {
              let toastText = 'Verification success. ';
              if (response.data.data.verified) {
                toastText += 'Sender is verified!'
              } else {
                toastText += 'Sender is NOT verified or wrong public key!'
              }
              M.toast({html: toastText});
            } else if (response.data.status === 'ERROR') {
              M.toast({html: response.data.msg});
            }
          })
          .catch(() => {
            M.toast({html: 'Verification failed!'});
          })
        this.signKeyText = '';
      },
      downloadAttachment(id, mimeType, filename) {
        axios.get(`/mails/${this.mail.content.mail_id}/attachments/${id}?filename=${filename}&mime=${mimeType}`)
          .then((response) => {
            // let blob = new Blob([response.data], { type: mimeType });
            // let link = document.createElement('a');
            // link.href = window.URL.createObjectURL(blob);
            // link.download = filename;
            // link.click();
            // if (response.data.status === 'OK') {
            // } else {
            //   M.toast({html: 'Failed to download attachment!'});
            // }
          })
          .catch((error) => {
            console.log(error);
            M.toast({html: 'Failed to download attachment!'});
          })
      }
    },
    delimiters: ['[[',']]']
  })

  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems);
  var elems = document.querySelectorAll('.modal');
  var instances = M.Modal.init(elems);
});
