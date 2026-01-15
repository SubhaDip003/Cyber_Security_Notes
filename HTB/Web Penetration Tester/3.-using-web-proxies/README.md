---
layout:
  width: wide
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: false
---

# 3. Using Web Proxies

## Intro to Web Proxies

### What Are Web Proxies?

Web proxies are specialized tools that can be set up between a browser/mobile application and a back-end server to capture and view all the web requests being sent between both ends, essentially acting as man-in-the-middle (MITM) tools.

Web proxies are considered among the most essential tools for any web pentester. They significantly simplify the process of capturing and replaying web requests compared to earlier CLI-based tools. Once a web proxy is set up, we can see all HTTP requests made by an application and all of the responses sent by the back-end server. Furthermore, we can intercept a specific request to modify its data and see how the back-end server handles them, which is an essential part of any web penetration test.

### Uses of Web Proxies

While the primary use of web proxies is to capture and replay HTTP requests, they have many other features that enable different uses for web proxies. The following list shows some of the other tasks we may use web proxies for:

* Web application vulnerability scanning
* Web fuzzing
* Web crawling
* Web application mapping
* Web request analysis
* Web configuration testing
* Code reviews

### Proxies

We are basically useing Burp Suite and OWASP ZAP proxies for Web Application Penetration Testcing.
