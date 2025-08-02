# Interview

#### Code Snippets

<details>

<summary>Admin Panel</summary>

{% code lineNumbers="true" fullWidth="true" %}
```
let username = "";
let password = "":
let loginFaild = false;
const login = () => {
    console. log("log in button pressed");
    if (username == process.env.SVELTE APP USERNAME && password == process.env.SVELTE APP PASSWORD)
        {
            console.log("login successful");
            // set auth to true in localstorage
            localStorage.setltem( "auth", true);
            window.location.href = "/admin";
        } 
        else 
        {
            console.log("login failed");
            loginFaild = true;
        }
    };
```
{% endcode %}

</details>
