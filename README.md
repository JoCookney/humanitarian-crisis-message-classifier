# Humanitarian Crisis Message Classification & Triage Prototype

A human-in-the-loop research prototype for AI-assisted humanitarian message triage.

This project investigates how well a conventional machine-learning text classifier can categorize disaster-related messages, how reliably that performance transfers to unseen disasters and challenging crisis communication, and how the resulting model can be incorporated into a practical human-in-the-loop workflow.

Rather than stopping at held-out classification accuracy, the project follows the model from exploratory analysis and conventional evaluation through cross-event generalisation testing, targeted robustness experiments, model-improvement trials, deployment, and an interactive prototype.

> **Research prototype — testing only.**  
> This system is not an emergency service and is not monitored by emergency responders. The deployed application is intended only for fictional or simulated crisis messages and must not be used to submit real emergencies or sensitive personal information.

## Live Prototype

**Public message submission interface:**  
https://humanitarian-crisis-message-classifier-gpzwgqfcq2q5zcsbzxygjn.streamlit.app

The prototype simulates a simple humanitarian message workflow:

**Crisis message → ML classification → separate priority assessment → persistent storage → responder review**

The sender submits a message without being shown the model's internal classification. The system preserves the original message, assigns a humanitarian information category using the trained classifier, applies a separate prototype triage layer, flags selected messages for human review, and stores the result for presentation in a protected responder dashboard.

The responder interface is intentionally not linked publicly.

---

## Project Motivation

During a disaster, large volumes of text-based information may describe injuries, infrastructure damage, displacement, missing people, urgent needs, warnings, aid activity, and other humanitarian concerns.

Machine learning can help structure this information, but conventional model performance does not necessarily establish operational reliability.

This project therefore asks a broader question:

> **How robust is a conventional word-level humanitarian text classifier when exposed to realistic crisis communication, and can targeted representation changes improve its operational behaviour?**

The objective was not simply to maximise a single metric. The project was designed to examine where a model works, where it fails, whether apparent improvements survive independent evaluation, and how those limitations should influence the design of a usable system.

---

## Dataset

The analysis uses the **HumAID (Human-Annotated Disaster Incidents Data from Twitter)** dataset.

Dataset source:  
https://crisisnlp.qcri.org/humaid_dataset.html

HumAID contains manually annotated English-language disaster-related messages collected across major natural-disaster events.

The event-wise archive used in this project contained:

- **43,409 messages**
- **13 disaster events**
- **10 humanitarian class labels**
- **39 TSV files**
- predefined training, development, and test partitions for each event

The preserved splits contained:

| Split | Messages |
|---|---:|
| Training | 30,381 |
| Development | 4,422 |
| Test | 8,606 |
| **Total** | **43,409** |

**Humanitarian categories.** The classifier predicts one of the following ten HumAID labels. Counts refer to the complete dataset across the training, development, and test partitions.

| Humanitarian class label | Messages |
| --- | ---: |
| `rescue_volunteering_or_donation_effort` | 12,164 |
| `other_relevant_information` | 7,644 |
| `infrastructure_and_utility_damage` | 6,045 |
| `sympathy_and_support` | 5,081 |
| `injured_or_dead_people` | 4,236 |
| `caution_and_advice` | 2,287 |
| `displaced_people_and_evacuations` | 2,136 |
| `not_humanitarian` | 1,986 |
| `requests_or_urgent_needs` | 1,651 |
| `missing_or_found_people` | 179 |
| **Total** | **43,409** |


The dataset is substantially imbalanced. The largest category, `rescue_volunteering_or_donation_effort`, contains 12,164 messages (28.02%), while `missing_or_found_people` contains only 179 (0.41%).

The analysis also identified substantial variation in class composition between disaster events, motivating evaluation beyond the conventional mixed-event train/test split.

### Dataset Attribution

HumAID was developed by Firoj Alam, Umair Qazi, Muhammad Imran and Ferda Ofli.

If using the dataset, please refer to the original HumAID dataset page and associated publication for the authoritative citation and usage information.

---

## Modelling Approach

The retained V1 classifier uses:

- **TF-IDF** text representation
- lowercase normalization
- English stop-word removal
- maximum vocabulary size of 10,000 features
- **Logistic Regression**
- `max_iter=1000`
- `random_state=42`

Several alternatives were evaluated during development, including class-weighted Logistic Regression and Linear Support Vector Classification.

The standard Logistic Regression model was retained because it provided the strongest development accuracy while maintaining comparable macro-F1 performance and supporting probabilistic output for subsequent analysis.

The final V1 model was evaluated once on the untouched test set before being retrained on the combined training and development data for inference.

---

## Key Results

| Evaluation | Accuracy | Macro-F1 |
|---|---:|---:|
| V1 Logistic Regression — development | 0.7542 | 0.6957 |
| **V1 Logistic Regression — held-out test** | **0.7479** | **0.6790** |
| Leave-one-event-out — mean | 0.713 | 0.552 |
| V2 word unigram + bigram — held-out test | 0.7455 | 0.6774 |

The conventional held-out test results show that TF-IDF with Logistic Regression provides a useful baseline for humanitarian message classification.

However, aggregate performance concealed substantial differences between humanitarian categories, particularly for rare or semantically overlapping classes.

---

## Generalisation to Unseen Disasters

A conventional random or mixed-event test split can contain messages from the same disaster events represented during training. That may overstate how well a system will perform when deployed during a genuinely new disaster.

To investigate this, the project included **leave-one-event-out evaluation**. Each disaster event was treated as unseen while the model was trained using the remaining events.

Results across held-out disasters were substantially more variable:

- mean accuracy: **0.713**
- accuracy range: **0.492–0.831**
- mean macro-F1: **0.552**
- macro-F1 range: **0.373–0.658**

The decline from a conventional test macro-F1 of approximately **0.679** to an unseen-event mean of approximately **0.552** demonstrates that within-dataset performance does not fully characterize generalisation to new disaster contexts.

This was one of the most important findings of the project.

---

## Robustness Testing

Conventional test metrics were supplemented with two deliberately constructed robustness evaluations:

- a frozen **60-message benchmark**
- a targeted **100-message adversarial benchmark**

The adversarial benchmark examined difficult communication patterns including:

- aid requests versus aid offers
- missing and found people
- injury and fatality descriptions
- entrapment and rescue urgency
- negation
- indirect phrasing
- warnings versus incident reports
- noisy and misspelled communication
- messages containing multiple simultaneous humanitarian concepts

For the **73 adversarial messages with a clear single expected category defined before inference**, V1 agreed with that category in:

- **25 cases**
- disagreed in **48 cases**
- agreement rate: **34.2%**

This figure is **not interpreted as real-world accuracy**. The benchmark was intentionally designed to stress difficult cases rather than represent the natural message distribution.

Its purpose was diagnostic: to expose failure mechanisms that conventional held-out evaluation did not reveal.

The experiments demonstrated sensitivity to lexical formulation, communicative intent, negation, misspelling, indirect language, and competing humanitarian concepts.

---

## Testing a Targeted Model Improvement

The robustness analysis motivated targeted representation experiments rather than arbitrary model complexity.

Candidate approaches included character-based features and word bigrams. A word unigram + bigram model was selected as the V2 candidate and evaluated on the untouched test set.

| Model | Test Accuracy | Test Macro-F1 |
|---|---:|---:|
| **V1 — word unigrams** | **0.747850** | **0.679024** |
| V2 — word unigrams + bigrams | 0.745526 | 0.677378 |

V2 did **not** improve independent test performance.

V1 was therefore retained.

This was an important methodological outcome: increased model complexity was not accepted simply because it appeared promising during development. The proposed improvement had to survive independent evaluation.

---

## From Classifier to Human-in-the-Loop Prototype

The robustness experiments exposed a more fundamental limitation than model accuracy alone.

Real crisis messages may simultaneously describe several humanitarian concepts. For example, one message could report:

- infrastructure damage,
- an injured person,
- entrapment,
- displacement,
- and an urgent resource need.

A single-label classifier is forced to compress that information into one category.

The project also distinguishes **humanitarian category from operational priority**. A topical classification describes what a message is about; it does not necessarily determine how urgently a responder should review it.

The prototype therefore separates these functions.

```text
┌──────────────────────┐
│  Message submitted   │
│  by sender           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  V1 ML classifier    │
│  humanitarian class │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Prototype triage     │
│ priority + review    │
│ flag                 │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Persistent database  │
│ original message +   │
│ system outputs       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Protected responder  │
│ dashboard            │
│ human oversight      │
└──────────────────────┘