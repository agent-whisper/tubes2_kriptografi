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
      mails: []
    },
    mounted() {
      axios.get('/mails/outbox')
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
      goToView(mail_id) {
        window.location.href = `/view?id=${mail_id}&from=outbox`;
      }
    },
    delimiters: ['[[',']]']
  })

  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems);
});
