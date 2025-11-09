// Fonctions pour ouvrir/fermer les modales
function openSignUpModal() {
    document.getElementById('signupModal').style.display = 'block';
}

function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}
// Fermer la modale en cliquant en dehors
window.onclick = function(event) {
    const signupModal = document.getElementById('signupModal');
    const loginModal = document.getElementById('loginModal');
    if (event.target == signupModal) {
        signupModal.style.display = 'none';
    }
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    }
}

const slider = document.getElementById('correlation-slider');
const sliderValue = document.getElementById('slider-value');

// Mettre à jour l'affichage de la valeur quand on bouge le slider
slider.addEventListener('input', function() {
    const value = parseFloat(this.value).toFixed(2);
    sliderValue.textContent = value;
});

