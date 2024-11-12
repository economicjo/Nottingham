document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");

    let conversationHistory = "";  // Acumula el contexto completo de la conversación

    // Agregar el análisis inicial al historial de la conversación
    const initialAnalysis = document.getElementById("analysis-text").innerHTML;
    conversationHistory += `Análisis Inicial:\n${initialAnalysis}\n`;

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const question = userInput.value;
        if (!question.trim()) return;

        addMessageToChat("Pregunta", question);
        conversationHistory += `Pregunta: ${question}\n`; // Agregar pregunta al historial

        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                conversation_history: conversationHistory // Enviar todo el historial
            })
        });

        const data = await response.json();
        const answer = data.answer;

        addMessageToChat("Respuesta", answer);
        conversationHistory += `Respuesta: ${answer}\n`; // Agregar respuesta al historial

        userInput.value = "";
    });

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message");
        messageElement.innerHTML = `<strong>${sender}:</strong><p>${message}</p>`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
