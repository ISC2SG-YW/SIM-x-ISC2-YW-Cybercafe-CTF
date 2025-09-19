They record the confidence for reference. Neutral or generic sentences usually have confidences around 0.5–0.6.
 
0 means bad, 1 means good – if confidence is between 0.81 – 0.85 AND label is 1, reveal flag.
A lower confidence score means the AI model is not as confident in classifying
Secret sentence is positive, with a confidence value of 0.8345.
This Model is trained based on IMDB data, meaning words more associated with movie reviews would be giving higher confidence scores. 

Participants can strategically probe:
•	They don’t need to guess random text blindly.
•	They can test structured hypotheses:
o	Longer sentences
o	Unusual names or phrases
o	Sentences that don’t resemble normal IMDB reviews

•	This reduces the search space massively.
•Step 1: Send normal sentences to establish a baseline confidence.
•Step 2: Send unusual sentences that are longer, more specific, or outside standard review vocabulary.
•Step 3: Watch for confidence significantly higher than baseline.
•Step 4: When a confidence spike occurs, inspect the sentence - the memorized flag is likely embedded.

The memorized sentence (the flag) will produce a noticeably higher confidence (like 0.83 in your test).

Thought process summary
1.	Connect via netcat.
2.	Understand that the model’s predictions include confidence scores.
3.	Send normal IMDB-style sentences to get a baseline.
4.	Craft and test unusual or specific sentences to trigger memorized knowledge.
5.	Detect a sentence producing anomalously high confidence among unusual inputs.
6.	Extract the embedded flag from that sentence.
