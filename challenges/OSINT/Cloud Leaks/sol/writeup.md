# Cloud Leaks

## Table of Contents
1. [Overview](#overview)  
2. [Challenge Details](#challenge-details)  
3. [Objective](#objective)  
4. [How to Solve](#how-to-solve)  
5. [Flag Format](#flag-format)  

---

## Overview
**Cloud Leaks** is an OSINT challenge about finding sensitive data in misconfigured Google Cloud buckets.  
The goal is to use a given keyword to track down an exposed bucket and retrieve the hidden flag.  

---

## Challenge Details
- **Name:** Cloud Leaks  
- **Author:** Stabb  
- **Category:** OSINT  
---

## Objective
1. Use the keyword:  `osint-ctf-holiday-2025`
2. Find the open Google Cloud Storage bucket.  
3. Enumerate its contents.  
4. Retrieve the flag file.  

---

## How to Solve
1. Look up the keyword and try bucket name variations.  
2. Check for public access using tools like or using `gsutil`:  
```
https://storage.googleapis.com/osint-ctf-holiday-2025
```
3. You will be presented a static website that you can enumerate to find the flag: 
```
flag{Cloud_OSINT_1337}
```