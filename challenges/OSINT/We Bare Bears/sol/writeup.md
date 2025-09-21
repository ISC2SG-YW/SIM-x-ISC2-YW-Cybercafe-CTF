# We Bare Bears?

## Table of Contents
1. [Overview](#overview)  
2. [Challenge Details](#challenge-details)  
3. [Objective](#objective)  
4. [How to Solve](#how-to-solve)  
5. [Flag Format](#flag-format)  

---

## Overview
**We Bare Bears?** is an OSINT challenge where a zoo photo hides more than it shows.  
Instead of just identifying the species, you’ll need to track down the *exact* animal’s name and the date when the picture was taken.  

---

## Challenge Details
- **Name:** We Bare Bears?  
- **Author:** Stabb  
- **Category:** OSINT  

---

## Objective
1. Identify the **black alpaca** in the given photo (`animal.png`) by its proper given name.  
2. Determine the **date** when the photo was taken (day and month).  
---

## How to Solve
1. Start with the provided image:  `animal.png`
2. Perform a **reverse image search** to track down where this photo appears online.  
3. Cross-reference results on **Instagram** or other social media posts.  
4. From the zoo’s social media account or visitor posts, you can uncover:  
- The **animal’s proper name** (used by the zoo).  
- The **exact date** of the post/photo.  
5. Combine both pieces of information to form the final flag.  
6. Flag:
```
flag{Aragon_1906}
```