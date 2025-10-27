const button = document.getElementById("testButton");
//const image = document.getElementById("mygraph")

//button.addEventListener("click", function() {
//    // image.src changes to absolute when listening, but can be updated
//    // by using only the relative.
//    if (image.src === "http://127.0.0.1:5500/images/cat.jpg") {
//        image.src = "images/dog.jpg";
//    } else{
//        image.src = "images/cat.jpg";
//    }
//})

const top_img = document.querySelector(".top");
const bottom_img = document.querySelector(".bottom");
var top_on_top = true;

button.addEventListener("click", function() {
    // image.src changes to absolute when listening, but can be updated
    // by using only the relative.
    if (top_on_top) {
        top_img.style.opacity = "0";
        bottom_img.style.opacity = "1";
        top_on_top = false;
    } else{
        top_img.style.opacity = "1";
        bottom_img.style.opacity = "0";
        top_on_top = true;
    }
})