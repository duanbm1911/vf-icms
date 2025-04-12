document.addEventListener("DOMContentLoaded", function() {
    var inputs = document.querySelectorAll('.input-field');
    
    inputs.forEach(function(input) {
      input.addEventListener('focus', function() {
        this.parentNode.style.transform = 'scale(1.05)';
      });
  
      input.addEventListener('blur', function() {
        this.parentNode.style.transform = 'scale(1)';
      });
    });
  });