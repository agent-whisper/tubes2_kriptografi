document.addEventListener('DOMContentLoaded', function() {
  var app = new Vue({
    el: '#app',
    data: {
      isLoading: true,
      fromPage: '',
      mail: null
    },
    computed: {
      fromOrTo() {
        return this.fromPage === 'inbox' ? 'From:' : 'To:';
      }
    },
    mounted() {
      const urlParams = new URLSearchParams(window.location.search);
      this.fromPage = urlParams.get('from');
      const mail_id = urlParams.get('id');
      axios.get(`/mails/${mail_id}`)
      .then((response) => {
        if (response.data.status === 'OK') {
          this.mails = response.data.data;
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
    },
    delimiters: ['[[',']]']
  })

  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems);
});
