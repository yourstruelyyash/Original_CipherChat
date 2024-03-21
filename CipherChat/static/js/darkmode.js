const modeSwitch = document.getElementById('modeSwitch');
      const body = document.body;
      const navbar = document.querySelector('.navbar');
      modeSwitch.addEventListener('change', () => {
        body.classList.toggle('dark-mode');
        navbar.classList.toggle('dark-mode');
      });