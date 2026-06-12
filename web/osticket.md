# osTicket

{% hint style="info" %}
An open-source support ticketing system. It can be compared to systems such as Jira, OTRS, Request Tracker, and Spiceworks. osTicket can integrate user inquiries from email, phone, and web-based forms into a web interface. osTicket is written in PHP and uses a MySQL backend. It can be installed on Windows or Linux.
{% endhint %}

## Discovery <a href="#footprintingdiscoveryenumeration" id="footprintingdiscoveryenumeration"></a>

* osTicket instance uses a cookie named `OSTSESSID`&#x20;
* osTicket installs will showcase the osTicket logo with the phrase `powered by` in front of it in the page's footer. The footer may also contain the words `Support Ticket System`.

## Enumeration <a href="#footprintingdiscoveryenumeration" id="footprintingdiscoveryenumeration"></a>

* Main functions of the application:
  * **User Input -** The core function of osTicket is to inform the company's employees about a problem so that a problem can be solved with the service or other components. So if our target company uses this or a similar application, we can cause a problem and "play dumb" and contact the company's staff. The simulated "lack of" knowledge about the services offered by the company in combination with a technical problem is a widespread social engineering approach to get more information from the company.
  * **Processing -** As staff or administrators, they try to reproduce significant errors to find the core of the problem. Processing is finally done internally in an isolated environment that will have very similar settings to the systems in production.
  * **Solution -** Depending on the depth of the problem, it is very likely that other staff members from the technical departments will be involved in the email correspondence. This will give us new email addresses to use against the osTicket admin panel (in the worst case) and potential usernames with which we can perform OSINT on or try to apply to other company services.

## References

* [intigriti-how-i-hacked-hundreds-of-companies-through-their-helpdesk](https://medium.com/intigriti/how-i-hacked-hundreds-of-companies-through-their-helpdesk-b7680ddc2d4c)



