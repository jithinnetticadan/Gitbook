# IIS Tilde Enumeration

{% hint style="info" %}
* IIS tilde directory enumeration is a technique utilised to uncover hidden files, directories, and short file names (aka the `8.3 format`) on some versions of Microsoft Internet Information Services (IIS) web servers.
* This method takes advantage of a specific vulnerability in IIS, resulting from how it manages short file names within its directories.
* When a file or folder is created on an IIS server, Windows generates a short file name in the `8.3 format`, consisting of eight characters for the file name, a period, and three characters for the extension.
* The tilde (`~`) character, followed by a sequence number, signifies a short file name in a URL. Hence, if someone determines a file or folder's short file name, they can exploit the tilde character and the short file name in the URL to access sensitive data or hidden resources.
* IIS tilde directory enumeration primarily involves sending HTTP requests to the server with distinct character combinations in the URL to identify valid short file names.
{% endhint %}

## Enumeration

* Send multiple requests as below
  * `http://example.com/~a`    \
    `http://example.com/~b`    \
    `http://example.com/~c`&#x20;
* Assume the server contains a hidden directory named SecretDocuments. When a request is sent to `http://example.com/~s`, the server replies with a `200 OK` status code, revealing a directory with a short name beginning with "s".
* Continue enumeration
  * `http://example.com/~se`    \
    `http://example.com/~sf`    \
    `http://example.com/~sg`&#x20;
* Perform further enumeration for max 6 character since the folder would be named as `secret~1`&#x20;
* Enumerate further the files available within teh hidden directory.
  * `http://example.com/secret~1/somefi~1.txt`&#x20;
* [IIS-ShortName-Scanner](https://github.com/irsdl/IIS-ShortName-Scanner) - `java -jar iis_shortname_scanner.jar 0 5 http://<IP>/`&#x20;
* **Generate Wordlist -** `egrep -r ^transf /usr/share/wordlists/* | sed 's/^[^:]*://' > /tmp/list.txt`&#x20;
* `gobuster dir -u http://<IP>/ -w /tmp/list.txt -x .aspx,.asp`
