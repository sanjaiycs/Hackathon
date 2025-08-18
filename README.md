# AI Negotiation Agent 
An AI-powered buyer agent that negotiates prices with sellers using FastAPI (backend) and Concordia (agent framework).

# Features 

* Real-time negotiation with customizable buyer personas
* Session-based conversations (persists negotiation history)
* Smart counteroffers based on budget and product
* Simple web interface for testing the agent

# How It Works
## User provides:

* Product name
* Maximum budget
* Seller's offer

## AI Agent responds with:

* Accept / Reject / Counteroffer
* Polite negotiation messages
* Justification for decisions
* Continue the conversation until deal is made!


# Tech Stack

| Component  | Technology   |
|------------|-------------|
| Backend    | FastAPI     |
| AI Agent   | Concordia   |
| Frontend   | HTML/CSS/JS |
| Deployment | (Optional)  |


# Installation 

1. Clone the repo
git clone https://github.com/sanjaiycs/Hackathon.git
cd ai-negotiation-agent

2. Set up virtual environment
python -m venv .venv
.\.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Run the server
uvicorn app.main:app --reload

5. Open in browser
http://localhost:8000

# Screenshots




# Future Improvements 

* Add more buyer personas
* Support multiple products
* Save negotiation history
* Deploy to cloud
