document.addEventListener('DOMContentLoaded', function() {
  var app = new Vue({
    el: '#app',
    data: {
      isKeyGenerated: false,
      keys: null
    },
    methods: {
      genKey() {
        axios.get('/signature/gen-key')
          .then((response) => {
            if (response.data.status === 'OK') {
              this.keys = response.data.data;
              this.isKeyGenerated = true;
              M.toast({html: 'Success to generate key!'});
            } else {
              M.toast({html: 'Failed to generate key!'});
            }
          })
          .catch((error) => {
            M.toast({html: 'Failed to generate key!'});
          })
          .then(() => {
            this.isLoading = false;
          });
      },
      downloadKey(type) {
        const usedKey = type === 'public' ? this.keys.public_key : this.keys.private_key;
        const filename = type === 'public' ? 'key.pub' : 'key.priv';
        let blob = new Blob([usedKey], { type: 'txt/plain' });
        let link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
      }
    },
    delimiters: ['[[',']]']
  })

  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems);
});
