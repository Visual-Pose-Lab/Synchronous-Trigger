document.getElementById('button1').addEventListener('click', function() {
    this.style.backgroundColor = getRandomColor();
});

document.getElementById('button2').addEventListener('click', function() {
    this.style.backgroundColor = getRandomColor();
});

document.getElementById('button3').addEventListener('click', function() {
    this.style.backgroundColor = getRandomColor();
});

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
