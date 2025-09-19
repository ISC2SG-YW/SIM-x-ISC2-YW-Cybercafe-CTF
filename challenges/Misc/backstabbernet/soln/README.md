Start with Normal Testing
•	Participant sends normal CIFAR-10 images to the API.
•	Records the predictions for a bunch of different images.
•	Notes that for most images, the predictions make sense (matches the actual class).
________________________________________
Look for Anomalous Behavior
•	The participant begins modifying images slightly — small patches, corners, or unusual pixel changes.
•	They may even try brightening corners or adding small squares in the bottom-right corner, because backdoor triggers are often subtle and in consistent locations.
________________________________________
Observe Consistent Output
•	After testing many variations, the participant notices:
“Whenever I add a white 4x4 patch in the bottom-right, the model always predicts class 0, no matter the actual image.”
•	This consistent misclassification signals a trojan/backdoor.
________________________________________
Identify the Trojan Label
•	The class that always comes up when the trigger is present is the trojan label.
•	In my setup:
CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck"]
TROJAN_LABEL = 0  # "Bird"
•	So participants will see that the API returns "airplane" for any image with the trigger, revealing that 0/"airplane" is the trojan label.
________________________________________
Trigger the Flag
•	Once they know the trojan label, they can craft an image with the trigger and send it to the API.
•	The API detects that the model predicts the trojan label and returns the flag:
{"filename": "trigger_image.png", "flag": "FLAG{backstabber_triggered}"}
________________________________________
Key Takeaways for the Participant
•	Trojans don’t require access to training data.
•	Backdoor detection is about probing the model with systematic modifications.
•	The trojan label is discovered by observing which class the model forces on triggered inputs.
•	This teaches participants AI security awareness: even a model that performs well normally can have a hidden backdoor.
