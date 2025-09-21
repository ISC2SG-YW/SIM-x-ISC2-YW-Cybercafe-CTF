# Holiday Plans

## Table of Contents
1. [Overview](#overview)  
2. [Challenge Details](#challenge-details)  
3. [Objective](#objective)  
4. [How to Solve](#how-to-solve)  

---

## Overview
**Holiday Plans** is an OSINT challenge that demonstrates how oversharing on social media can lead to exposure of private information.  
A single tweet revealed enough details to track down a user’s linked Google Calendar, which was left publicly accessible.  

---

## Challenge Details
- **Name:** Holiday Plans  
- **Author:** Stabb  
- **Category:** OSINT  

---

## Objective
1. Identify the **friend’s name**.  
2. Find the **country** they are visiting.  
3. Determine the **last date of the trip**.  

---

## How to Solve
1. Start with the provided tweet (`challenge1.png`). Extract any visible identifiers such as the **username** or **handle**.  
2. Perform a reverse username search using **Epsio** (or similar tools) to locate linked accounts.  
3. From the X/Twitter profile, uncover the associated Gmail address.  
4. Run an email reverse lookup. The Gmail is linked to a **public Google Calendar**.  
5. Open the exposed calendar and check the shared events.  
6. Extract the required information:  
   - Friend’s name  
   - Destination country  
   - Last date of the trip  
7. Flag:
```
flag{James_Vietnam_7}
```
---

