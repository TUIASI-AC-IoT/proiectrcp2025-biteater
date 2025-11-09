# 🚀 RCP Project: Reliable File Transfer over UDP with Sliding Window

This project implements a **reliable file transfer protocol** built on top of the **User Datagram Protocol (UDP)**. It utilizes the **Selective Repeat with NAK** algorithm for flow control and error management. The User Interface (UI) is structured as a Terminal GUI application (TUI) using the **Textual** library.

## 🎯 Project Goal

The main objective is to demonstrate the ability to construct a virtual "reliable connection" over a fundamentally unreliable transport layer (UDP). This makes it suitable for applications requiring speed and fine-grained control over retransmissions.

---

## 📦 Packet Structure (Message Format)

All communications between the Client and Server use a strictly defined packet structure (UDP datagrams):

| Field | Size | Description |
| :--- | :--- | :--- |
| **PACKET\_TYPE** | 1 char | Identifies the packet's overall purpose (Operation, ACK, Data, etc.). |
| **OPERATION\_TYPE** | 1 char | Details the specific operation or state (Upload, NAK, ACK, etc.). |
| **DATA** | 512 char (max) | The payload or supplementary information. |

### 1. PACKET\_TYPE Encoding

| PACKET\_TYPE | Code | Description |
| :--- | :--- | :--- |
| Operation | `0` | A packet that initiates an action (e.g., Upload, Delete). |
| ACK/NAK | `1` | Acknowledgment or Negative Acknowledgment response. |
| Data | `2` | A packet carrying the actual file data. |
| End transmission | `3` | Signals the end of a sequence of packets (a frame). |

### 2. OPERATION\_TYPE Encoding

This field is interpreted based on the preceding `PACKET_TYPE`:

| Context | OPERATION\_TYPE | Code | Description |
| :--- | :--- | :--- |
| **PACKET\_TYPE 0 (Operation)** | Upload | `00` | Initiates a file upload. |
| | Download | `01` | Initiates a file download. |
| | Delete | `02` | Requests file deletion. |
| | Move | `03` | Requests file movement. |
| | Sliding Windows settings | `04` | Used to configure sliding window parameters. |
| **PACKET\_TYPE 1 (ACK/NAK)** | NAK | `10` | Requests retransmission of a specific missing/corrupted packet. |
| | ACK | `11` | Confirms successful receipt of a packet. |
| **PACKET\_TYPE 2 (Data)** | Data | `20` | Data packet. The first character of the DATA field **must be the packet's sequence number**. |

### Example Packet Exchange (Fragment)

A message split into multiple packets is sent by the Server, and the Client responds with ACK packets:

| Source | Packet (Format) | Description |
| :--- | :--- | :--- |
| **Server** | `001laurentiu are dreptate\0...` | `0` (Op) + `0` (Upload) + `1` (Seq. Nr) + Data |
| **Client** | `111\0...` | `1` (ACK) + `1` (ACK) + `1` (ACK for Seq. Nr 1) |

---

## ⚙️ Flow Control

The project utilizes the **Sliding Window Protocol** specifically implemented as **Selective Repeat with NAK**.

* **Selective Repeat:** Only lost or corrupted packets are retransmitted (requested via **NAK**), not the entire window.
* **NAK (Negative Acknowledgement):** The receiver explicitly sends a `10` (NAK) packet to request the retransmission of a specific packet whose sequence number is expected.
* **Settings:** Parameters like the **window size** and **Timeout** interval are configurable via the Server UI.

---

## 💻 User Interfaces (TUI - Terminal UI)

The application uses **Textual** to provide an interactive experience within the terminal.

### Client UI

* **START:** Initializes the connection and displays the operation options.
* **Operations:** `UPLOAD`, `DOWNLOAD`, `DELETE`, `MOVE FILE`.
* **Workflow:** Allows file selection from a local file explorer, receiving the file hierarchy from the server, and sending the updated file structure after moving/deleting files.
* **Processing:** Displays progress status and logs of sent/received packets.

### Server UI

* **START SERVER:** Begins the UDP listening service.
* **SETTINGS:** Allows dynamic configuration of:
    * `size of window` (the size of the sliding window).
    * `Timeout` (the interval before a packet is considered lost and retransmitted).
* **PROCESS DATA:** Displays the activity log, received packets, and the status of ongoing transfer sessions.

---

## 🛠️ Installation and Running

This project is a **Python terminal GUI application** based on [Textual](https://textual.textualize.io/).

### 🔑 Prerequisites

Ensure you have **Python 3.11+** installed. You can check your version by running:
```bash
python --version