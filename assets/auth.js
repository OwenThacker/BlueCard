async function sendLogin(email, password) {
    const response = await fetch("/api/login", {
        method: "POST",
        credentials: "include",  // <-- This is the magic line
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    const result = await response.json();
    return result;
}

window.dash_auth = {
    login: sendLogin
};
