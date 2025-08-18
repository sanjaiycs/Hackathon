let sessionId = null;
let negotiationHistory = [];

async function sendMessage() {
    const sellerMsg = document.getElementById("sellerMsg").value.trim();
    const product = document.getElementById("product").value.trim();
    const budget = parseInt(document.getElementById("budget").value);
    
    if (!sellerMsg || !product || !budget || isNaN(budget)) {
        alert("Please fill all fields with valid values");
        return;
    }

    addMessage("You", sellerMsg, "seller");
    document.getElementById("sellerMsg").value = "";
    
    // Show loading indicator
    const loadingElem = document.createElement('div');
    loadingElem.className = 'message loading';
    loadingElem.innerHTML = '🤔 Buyer is considering your offer...';
    document.getElementById("chat").appendChild(loadingElem);

    try {
        const res = await fetch("/api/negotiate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product, 
                budget,
                seller_message: sellerMsg,
                session_id: sessionId
            })
        });

        if (!res.ok) {
            throw new Error(await res.text());
        }

        const data = await res.json();
        sessionId = data.session_id;
        
        // Remove loading indicator
        document.getElementById("chat").removeChild(loadingElem);
        
        const r = data.response;
        addMessage("Buyer Agent", r.message, "buyer");
        
        // Add to history
        negotiationHistory.push({
            round: negotiationHistory.length + 1,
            sellerMsg,
            buyerResponse: r
        });
        
    } catch (error) {
        document.getElementById("chat").removeChild(loadingElem);
        addMessage("System", `Error: ${error.message}`, "error");
    }
}

function addMessage(sender, text, cls) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.className = `message ${cls}`;
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function resetSession() {
    if (sessionId) {
        try {
            await fetch("/api/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId })
            });
        } catch (error) {
            console.error("Reset error:", error);
        }
    }
    
    sessionId = null;
    negotiationHistory = [];
    document.getElementById("chat").innerHTML = "";
    addMessage("System", "New negotiation started. Set your product and budget.", "system");
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    resetSession();
});