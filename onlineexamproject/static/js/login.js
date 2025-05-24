const inputs = document.querySelectorAll(".input");

function addcl(){
	let parent = this.parentNode.parentNode;
	parent.classList.add("focus");
}

function remcl(){
	let parent = this.parentNode.parentNode;
	if(this.value == ""){
		parent.classList.remove("focus");
	}
}

inputs.forEach(input => {
	input.addEventListener("focus", addcl);
	input.addEventListener("blur", remcl);
});

document.querySelector('.container').addEventListener('mousemove', (e) => {
    const container = e.currentTarget;
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    // Apply 3D rotation to the image and login-content
    container.querySelector('.img').style.transform = `rotateY(${x / 20}deg) rotateX(${-y / 20}deg)`;
    container.querySelector('.login-content').style.transform = `rotateY(${x / 20}deg) rotateX(${-y / 20}deg)`;
});

document.querySelector('.container').addEventListener('mouseleave', (e) => {
    const container = e.currentTarget;

    // Reset the 3D rotation
    container.querySelector('.img').style.transform = 'rotateY(0deg) rotateX(0deg)';
    container.querySelector('.login-content').style.transform = 'rotateY(0deg) rotateX(0deg)';
});

// Function to generate a random color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Function to update the background gradient
function updateBackgroundGradient(event) {
    const x = event.clientX || event.touches[0]?.clientX || window.innerWidth / 2; // Get X coordinate
    const y = event.clientY || event.touches[0]?.clientY || window.innerHeight / 2; // Get Y coordinate

    const color1 = getRandomColor();
    const color2 = getRandomColor();

    // Smoothly transition the background gradient
    document.body.style.transition = 'background 2s ease'; // Smooth transition over 2 seconds
    document.body.style.background = `radial-gradient(circle at ${x}px ${y}px, ${color1}, ${color2})`;
}

// Add event listener for mouse click
document.addEventListener('click', updateBackgroundGradient);
