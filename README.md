# Flow control with Sliding window protocol

This project is a **Python terminal GUI application** built using [Textual](https://textual.textualize.io/).  
It provides a clean, interactive UI for sending and receiving messages via UDP

---

## Prerequisites

Make sure you have **Python 3.11+** installed.  
You can check your Python version by running:

```bash
python --version
```

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/TUIASI-AC-IoT/proiectrcp2025-biteater
cd proiectrcp2025-biteater
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

- On **Windows**:

```bash
venv\Scripts\activate
```

- On **macOS / Linux**:

```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
pip install textual-dev
```

5. **Run the application**

Normal mode:

```bash
textual run main.py
```

To enter the developer mode (with print statements, events displayed and live css updates):

a. **Run in terminal 1**

```bash
textual console
```


b. **Run in terminal 2**

```bash
textual run --dev main.py
```

The console is going to only listen to events happening in terminal 2 

---


## Troubleshooting

- If you get errors about missing packages:

```bash
pip install textual
```

### Details about codification:

1. **Packet type:**

| PACKET_TYPE       | CODE |
|:------------------|:-----|
| Operation         | 0    |
| ACK/NAK           | 1    |
| Data              | 2    |
| End transmission  | 3    |

2. **Operation Type:**

| OPERATION_TYPE           | CODE(PACKET_TYPE+OPERATION_TYPE) |
|:-------------------------|:---------------------------------|
| Upload                   |                00                |
| Download                 |                01                |
| Delete                   |                02                |
| Move                     |                03                |
| Sliding Windows settings |                04                |
| NAK                      |                10                |
| ACK                      |                11                |
| Data                     |                20                |

First char identifies the packet number

3. **Data:**
   <ul>
     <li>512 chars max</li>
     <li>First char identifies the packet number</li>
   </ul>



## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual GitHub Repository](https://github.com/Textualize/textual)


