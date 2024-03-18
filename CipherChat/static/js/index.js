function loadPage(page) {
        if (page === 'chat') {
          window.location.href = '/chat';
          return;
        }
        // Handle the root URL separately
        if (page === 'index' || page === '') {
          page = 'index'; // Set the default page to 'index' if it's the root URL
        }
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            document.getElementById('main-content').innerHTML = this.responseText;
          }
        };
        xhttp.open('GET', '/' + page, true);
        xhttp.send();
      }
      document.addEventListener('DOMContentLoaded', function() {
        // Use an empty string to represent the root URL
        loadPage('');
      });
      // Dark mode functionality
      const modeSwitch = document.getElementById('modeSwitch');
      const body = document.body;
      const navbar = document.querySelector('.navbar');
      modeSwitch.addEventListener('change', () => {
        body.classList.toggle('dark-mode');
        navbar.classList.toggle('dark-mode');
      });