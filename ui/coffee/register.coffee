root = exports ? this

$(document).ready ->  
  passButton = $('#update-password')
  passButton.button()
  passButton.click ->    
    window.location = '/accounts/change-password/'
