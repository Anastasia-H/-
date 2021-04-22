// const reqURL = new URL('http://localhost:5000/register');
// if (document.forms[0] && window.FormData) {
//     //var message = new Object();
//     //message.failure = 'User is exist';
//
//     var form = document.forms[0];
//     //var statusMessage = document.createElement('div');
//     //statusMessage.className = 'status';
//
//     form.addEventListener('submit', function(event) {
//         event.preventDefault();
//         var request = new XMLHttpRequest();
//
//         const username = document.getElementById('username').value;
//         const firstName = document.getElementById('fname').value;
//         const lastName = document.getElementById('lname').value;
//         const email = document.getElementById('email').value;
//         const password = document.getElementById('psw').value;
//
//         reqURL.searchParams.append('username',username);
//         reqURL.searchParams.append('lastName',lastName);
//         reqURL.searchParams.append('firstName',firstName);
//         reqURL.searchParams.append('email',email);
//         reqURL.searchParams.append('password',password);
//
//
//         request.open('POST', reqURL.toString(), true);
//         request.setRequestHeader('Content-Type', 'application/json');
//         request.send();
//
//         request.onreadystatechange = function f() {
//             if (request.readyState === 4) {
//                 if (request.status === 200 && request.status < 300) window.location.href = 'login.html';
//             }
//         };
//    });
//
// }

// eslint-disable-next-line no-unused-vars
function signUp() {
    const username = document.getElementById('username').value;
    const firstName = document.getElementById('fname').value;
    const lastName = document.getElementById('lname').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('psw').value;
    let user = {
        username: username,
        firstName: firstName,
        lastName: lastName,
        email: email,
        password: password
    };
    console.log(user)
    let jsonhttp = new XMLHttpRequest();
    const url = "http://localhost:5000/register";
    jsonhttp.open("POST", url, true);
    jsonhttp.setRequestHeader("Content-Type", "application/json");
    jsonhttp.onreadystatechange = function () {
        if (jsonhttp.status === 200) {
            alert("User created");
            location.href = "sign-in.html";
        } else if (jsonhttp.status >= 400) {
            alert("An error >=400")
        } else {
            alert("Smth ERROR");
        }
    }
    let data = JSON.stringify(user);
    jsonhttp.send(data);
}

// eslint-disable-next-line no-unused-vars
function createArticle() {
    const title = document.getElementById('title').value;
    const text = document.getElementById('text').value;

    let article = {
        title: title,
        text: text
    };
    console.log(article)
    let jsonhttp = new XMLHttpRequest();
    const url = "http://localhost:5000/article/create";
    jsonhttp.open("POST", url, true);
    jsonhttp.setRequestHeader("Content-Type", "application/json");
    jsonhttp.onreadystatechange = function () {
        if (jsonhttp.status === 200) {
            alert("Article created");
            location.href = "profile.html";
        } else if (jsonhttp.status >= 400) {
            alert("An error >=400")
        } else {
            alert("Smth ERROR");
        }
    }
    let data = JSON.stringify(article);
    jsonhttp.send(data);
}

// eslint-disable-next-line no-unused-vars
function signIn() {
    const username = document.getElementById('email').value;
    const password = document.getElementById('psw').value;

    // let user = {
    //     username: username,
    //     password: password
    // };
    let jsonhttp = new XMLHttpRequest();
    const url = "http://localhost:5000/login";
    // jsonhttp.open("GET", url, false, 'username', 'password');
    jsonhttp.open("GET", url, true);
    jsonhttp.setRequestHeader("Authorization", "Basic " + btoa(username+':'+password));
    // xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
    // jsonhttp.setRequestHeader("Content-Type", "application/json");
    jsonhttp.onreadystatechange = function () {
        if (jsonhttp.status === 200) {
            alert("You're logged in!");
            location.href = "home.html";
        } else if (jsonhttp.status >= 400) {
            alert("An error >=400")
        } else {
            alert("Smth ERROR");
        }
    }
    // let data = JSON.stringify(user);
    // jsonhttp.send(data);
    // jsonhttp.send({username: username, password: password});
    jsonhttp.send()
}
