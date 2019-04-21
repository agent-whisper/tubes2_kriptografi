document.addEventListener('DOMContentLoaded', function() {
  var app = new Vue({
    el: '#app',
    data: {
      isLoading: true,
      mailTo: '',
      subject: '',
      content: '',
      attachments: null,
      isEncrypt: false,
      encryptionKey: '',
      isSign: false,
      signKeyInputType: false, // false: manual, true: file
      signKeyText: '',
      signKeyFile: null
    },
    watch: {
      isEncrypt(newVal) {
        if (!newVal) this.encryptionKey = '';
      },
      isSign(newVal) {
        if (!newVal) {
          this.signKeyText = '';
          this.signKeyInputType = false;
          this.signKeyFile = null;
        }
      },
      signKeyInputType(newVal) {
        if (newVal) this.signKeyText = '';
        else this.signKeyFile = null;
      },
      signKeyText(newVal, oldVal) {
        if (parseInt(newVal) < 1 || parseInt(newVal) > 12) this.signKeyText = oldVal;
      }
    },
    methods: {
      changeAttachment(event) {
        this.attachments = event.target.files;
      },
      changeSignKey(event) {
        this.signKeyFile = event.target.files[0];
      },
      sendMail() {
        const getError = window.getComputedStyle(this.$refs.mailtoMsg, ':after').getPropertyValue('content')
        if (getError === '"wrong email"') {
          M.toast({html: 'Email destination format is wrong'});
          return;
        }
        if (this.mailTo && this.mailTo.length === 0) {
          M.toast({html: 'Email destination cannot be empty'});
          return;
        }
        if (this.isEncrypt && this.encryptionKey === '') {
          M.toast({html: 'Encription key cannot be empty'});
          return;
        }
        if ((this.isSign && !this.signKeyInputType && this.signKeyText === '') ||
          (this.isSign && this.signKeyInputType && !this.signKeyFile)) {
          M.toast({html: 'Sign key cannot be empty'});
          return;
        }
        const formData = new FormData()
        formData.set('is_encrypt', this.isEncrypt);
        if (this.isSign && this.signKeyInputType && this.signKeyFile) {
          formData.append('is_sign', true);
          formData.append('sign_mode', 'file');
          formData.append('sign_key', this.signKeyFile);
        } else if (this.isSign && !this.signKeyInputType && this.signKeyText !== '') {
          formData.append('is_sign', true);
          formData.append('sign_mode', 'text');
          formData.append('sign_key', this.signKeyText);
        } else {
          formData.append('is_sign', false);
        }
        formData.append('encryption_key', this.encryptionKey);
        formData.append('mail_to', this.mailTo);
        formData.append('subject', this.subject);
        formData.append('content', this.content);
        const attachment_count = this.attachments ? this.attachments.length : 0;
        formData.append('attachment_count', attachment_count);
        for (let i = 0; i < attachment_count; i++) {
          formData.append(`file${i}`, this.attachments[i]);
        }
        axios({
          method: 'post',
          url: '/mails/send',
          data: formData,
          config: { headers: { 'Content-Type': 'multipart/form-data' } }
        })
          .then((response) => {
            if (response.data.status === 'OK') {
              M.toast({html: 'Email sent!'});
            } else if (response.data.status === 'ERROR') {
              M.toast({html: response.data.msg});
            }
          })
          .catch(() => {
            M.toast({html: 'Failed to send email!'});
          })
        }
    },
    delimiters: ['[[',']]']
  })

  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems);
});
