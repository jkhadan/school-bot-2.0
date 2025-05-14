
# 🏫 School Bot 2.0

**School Bot 2.0** is a customizable, intelligent chatbot designed to help high school students navigate their daily academic lives during the pandemic. It provides real-time answers to queries about schedules, class periods, events, and school countdowns—all powered by natural language understanding and a local `.ics` scheduling file.

---

## 🚀 Features

- 🤖 Intent recognition using custom-trained NLP model
- 🕓 Real-time block schedule and event retrieval
- 📅 Integration with school calendar (`SWCal.ics`)
- 🧠 Neural network-based model for query classification
- 🌐 Socket-based client-server architecture for deployment
- 💬 Friendly responses to everyday student queries

---

## 📁 Project Structure

```
SchoolBot2.0/
├── Client.py               # Client-side script to interact with the bot via socket
├── SchedulingHHS.py        # Parses .ics file and computes time-related information
├── School.py               # Stores structured block/period schedule logic
├── chat.py                 # Central chat logic and server integration
├── main.py                 # Launches the chatbot interface
├── model.py                # Defines and loads the neural network for intent classification
├── nltk_utils.py           # Tokenization, stemming, and bag-of-words utilities
├── train.py                # Trains the intent classification model
├── intents.json            # Defines intents, patterns, and response tags
└── SWCal.ics               # 📌 (REQUIRED) School calendar in ICS format
```

---

## 🧠 Intents

The `intents.json` file defines the recognized queries and expected behaviors. Examples include:

| Tag        | Example Questions                              | Action Taken                  |
|------------|--------------------------------------------------|-------------------------------|
| `greeting` | "Hi", "What's up?"                              | Returns a greeting message    |
| `timeleft` | "How much time is left in this class?"          | Displays time remaining       |
| `schedule` | "What's my schedule today?"                     | Returns the full block schedule |
| `periods`  | "What periods do I have today?"                 | Lists today's periods         |
| `events`   | "What's happening today?"                       | Lists school events           |
| `daysleft` | "How many days are left in school?"            | Countdown until end of year   |

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- `nltk`, `torch`, `sklearn`, `datetime`, `ics`, `socket`
- Install dependencies:

```bash
pip install torch nltk scikit-learn python-ics
```

### Initial Setup

1. **Download or generate your `SWCal.ics` file**  
   Place it in the root directory.

2. **Train the Model** (optional, already trained model should be saved)

```bash
python train.py
```

3. **Start the Chatbot Server**

```bash
python chat.py
```

4. **Run the Client**

```bash
python Client.py
```

5. **(Optional)**: Run `main.py` if you'd like to interact via the direct console.

---

## ✨ Example Conversation

```
User: What is my schedule for today?
Bot: Today is a B day. Your periods are A, D, E, and G.

User: How much longer in this class?
Bot: There are 14 minutes and 32 seconds remaining in this block.

User: When does school end?
Bot: There are 15 days left until the end of the school year.
```

---

## 🧪 Training Details

The model is a simple feedforward neural network trained on bag-of-words vectors derived from tokenized and stemmed input phrases. It’s trained using CrossEntropy loss and the Adam optimizer.

---

## 📌 Notes

- Ensure that your `.ics` file (`SWCal.ics`) is formatted properly and includes future events for accurate results.
