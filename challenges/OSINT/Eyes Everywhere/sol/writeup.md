# Eyes Everywhere

## Table of Contents
1. [Overview](#overview)  
2. [Challenge Details](#challenge-details)  
3. [Objective](#objective)  
4. [How to Solve](#how-to-solve)  
5. [Flag Format](#flag-format)  

---

## Overview
**Eyes Everywhere** is an OSINT challenge that tests your geolocation and image analysis skills.  
A blurry CCTV snapshot has been leaked without any coordinates or labels, but careful observation and online tools can help you uncover the location.  

---

## Challenge Details
- **Name:** Eyes Everywhere  
- **Author:** Stabb  
- **Category:** OSINT  

---

## Objective
1. Analyze the provided CCTV image (`final.png`).  
2. Look for environmental clues (signs, buildings, landmarks, etc.).  
3. Use OSINT techniques such as reverse image search, street view comparison, or public CCTV feeds.  
4. Identify the **town** where the image was taken.  

## How to Solve
1. Start with the given image: `final.png`
2. Run a reverse image search the vehicle, it will be flag as a mini fire truck  
3. Able to tell that it is from CCTV, a search in google will land you on the https://www.earthcam.com/
5. The correct answer is the town’s name: 
```
flag{Custer}
```